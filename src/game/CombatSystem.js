import { ENEMIES } from "./GameState.js";
import { BranchSystem } from "./BranchSystem.js";
import { EconomySystem } from "./EconomySystem.js";

function clone(o) { return JSON.parse(JSON.stringify(o)); }
function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }

export class CombatSystem {
  constructor(state, rng = Math.random) {
    this.state = state;
    this.rng = rng;
    this.time = 0;
    this.maxTime = 45;
    this.result = null;
    this.resultDelay = 0;
    this.hpLost = 0;
    this.log = [];
    this.floaters = [];
    this.trails = [];
    this.events = [];
    this.hitFlash = 0;
    this.slowMo = 1;
    this.recap = { physical:0, magic:0, dot:0, crits:0, heals:0, taken:0, shielded:0, dodges:0, skills:0 };
    this.player = this.makeHero(state.hero, 880, 430, "YOU");
    this.enemy  = state.currentOpponent
      ? this.makeHero(state.currentOpponent.hero, 520, 350, state.currentOpponent.name, state.currentOpponent)
      : this.makeEnemy();
    this.applyLoadout(this.player);
    if (state.currentOpponent?.cardLevels) this.applyExternalLoadout(this.enemy, state.currentOpponent.cardLevels);
  }

  // ── Unit factories ─────────────────────────────────────────────────────────

  makeHero(hero, x, y, label = "YOU", owner = null) {
    const s = hero.stats;
    return {
      id: hero.id, name: owner?.name || hero.name, heroName: hero.name,
      icon: hero.icon, color: hero.color,
      max: s.hp, hp: s.hp, atk: s.atk, arm: s.arm,
      focus: s.focus, spd: s.spd, crit: s.crit, critD: s.critD,
      regen: s.regen, dodge: s.dodge || 0,
      energy: 0, energyMax: 100,
      basic: 0, skillCd: 0, skill: clone(hero.skill),
      status: [], x, y, r: 34,
      dmg: 0, taken: 0, heal: 0, cnt: 0, label,
      attackPulse: 0, castPulse: 0, lastAction: "", actionLife: 0, intent: null,
      // v1.6 special fields
      openingCritsLeft: 0,   // guaranteed crits at combat start
      deathShieldCharges: 0, // prevents first death
      phaseCooldown: 0,      // phase immunity cooldown
    };
  }

  makeEnemy() {
    let pool;
    const r = this.state.round;
    if (r === 6)       pool = ENEMIES.slice(5, 6);
    else if (r === 12) pool = ENEMIES.slice(6);
    else if (r >= 9)   pool = ENEMIES.slice(2, 5);
    else if (r >= 4)   pool = ENEMIES.slice(2, 5);
    else               pool = ENEMIES.slice(0, 2);
    const e = clone(pool[Math.floor(this.rng() * pool.length)]);
    const s = e.stats, sc = 1 + (r - 1) * .10;
    return {
      id: e.id, name: e.name, icon: e.icon, color: e.color, level: e.level,
      max: Math.round(s.hp * sc), hp: Math.round(s.hp * sc),
      atk: Math.round(s.atk * sc), arm: Math.round(s.arm * sc), focus: Math.round(s.focus * sc),
      spd: s.spd, crit: s.crit, critD: s.critD,
      regen: s.regen + r * .25, dodge: s.dodge || 0,
      energy: 0, energyMax: 100, basic: 0, skillCd: 2,
      skill: {
        name: r >= 7 ? "Elite Burst" : "Rough Touch",
        cd: 6, energy: 45, pow: r >= 7 ? 1.25 : 1,
        type: r >= 7 ? "magic" : "phys",
        status: r >= 9 ? "burn" : null, dur: 3, dot: 16,
      },
      status: [], x: 520, y: 350, r: 32,
      dmg: 0, taken: 0, heal: 0, cnt: 0, label: "ENEMY",
      attackPulse: 0, castPulse: 0, lastAction: "", actionLife: 0, intent: null,
      openingCritsLeft: 0, deathShieldCharges: 0, phaseCooldown: 0,
    };
  }

  applyExternalLoadout(unit, cardLevels) {
    const old = this.state.cardLevels;
    this.state.cardLevels = cardLevels;
    this.applyLoadout(unit);
    this.state.cardLevels = old;
  }

  applyLoadout(u) {
    const f = BranchSystem.effects(this.state);
    if (f.hp)            { u.max += Math.round(f.hp); u.hp += Math.round(f.hp); }
    if (f.armor)         u.arm     += f.armor;
    if (f.attack)        u.atk     += f.attack;
    if (f.focus)         u.focus   += f.focus;
    if (f.manaRegen)     u.regen   += f.manaRegen;
    if (f.speedPct)      u.spd     *= 1 + f.speedPct;
    if (f.crit)          u.crit    += f.crit;
    if (f.critD)         u.critD   += f.critD;
    if (f.dodge)         u.dodge   += f.dodge;
    if (f.startShield)   this.addStatus(u, { type: "shield", dur: 99, val: f.startShield });
    // v1.6: special procs applied at combat start
    if (f.openingCrits)  u.openingCritsLeft    = Math.round(f.openingCrits);
    if (f.deathShield)   u.deathShieldCharges  = Math.round(f.deathShield);
  }

  // ── Main loop ──────────────────────────────────────────────────────────────

  update(dt) {
    if (this.result) {
      this.resultDelay += dt;
      this.updateVisuals(dt);
      return;
    }
    const simDt = dt * this.slowMo;
    this.time += simDt;
    this.act(this.player, this.enemy, simDt, true);
    this.act(this.enemy, this.player, simDt, false);
    this.tickStatus(this.player, simDt);
    this.tickStatus(this.enemy, simDt);
    this.updateVisuals(dt);

    if (this.player.hp <= 0 || this.enemy.hp <= 0 || this.time >= this.maxTime) {
      this.slowMo = .35;
      this.finish();
    }
  }

  updateVisuals(dt) {
    for (const u of [this.player, this.enemy]) {
      u.attackPulse  = Math.max(0, (u.attackPulse  || 0) - dt * 4.5);
      u.castPulse    = Math.max(0, (u.castPulse    || 0) - dt * 2.2);
      u.actionLife   = Math.max(0, (u.actionLife   || 0) - dt);
      u.phaseCooldown= Math.max(0, (u.phaseCooldown|| 0) - dt);
    }
    this.hitFlash = Math.max(0, this.hitFlash - dt * 3);
    this.floaters.forEach(f => { f.life -= dt; f.y -= dt * 42; });
    this.floaters = this.floaters.filter(f => f.life > 0);
    this.trails.forEach(t => { t.life -= dt; t.t += dt * 4; });
    this.trails = this.trails.filter(t => t.life > 0);
    this.events.forEach(e => e.life -= dt);
    this.events = this.events.filter(e => e.life > 0);
  }

  // ── Actor turn ─────────────────────────────────────────────────────────────

  act(a, t, dt, isPlayer) {
    if (a.hp <= 0) return;
    if (this.has(a, "stun")) { a.energy += a.regen * dt * .3; a.intent = "STUNNED"; return; }

    const f = isPlayer ? BranchSystem.effects(this.state) : {};

    // Passive regen effects
    if (isPlayer && f.hpRegen)     this.heal(a, f.hpRegen * dt);
    if (isPlayer && f.shieldRegen) {
      a.clock = (a.clock || 0) + dt;
      if (a.clock >= 7) { a.clock = 0; this.addStatus(a, { type: "shield", dur: 4, val: f.shieldRegen }); }
    }

    // Ice slow: frozen units attack and regen slower
    const iceStatus = a.status.find(s => s.type === "ice" && s.dur > 0);
    const iceMult   = iceStatus ? Math.max(0.35, 1 - (iceStatus.slow || 0.1) * (iceStatus.stacks || 1)) : 1;

    a.energy  = Math.min(a.energyMax, a.energy + a.regen * dt * iceMult);
    a.basic  -= dt * iceMult;
    a.skillCd-= dt;
    a.intent  = (a.energy >= a.skill.energy && a.skillCd <= 0) ? "SKILL READY" : "ATTACK";

    if (a.skillCd <= 0 && a.energy >= a.skill.energy) { this.skill(a, t, a.skill, isPlayer); return; }
    if (a.basic <= 0)  { this.basic(a, t, isPlayer);  a.basic = Math.max(.25, 1 / Math.max(.1, a.spd)); }
  }

  // ── Basic attack ───────────────────────────────────────────────────────────

  basic(a, t, isPlayer) {
    a.cnt += 1;
    a.attackPulse = 1;
    a.lastAction  = "Attack";
    a.actionLife  = .8;
    this.trail(a, t, isPlayer ? "#ffffff" : "#ef476f", "attack");

    const d    = this.damage(a, t, a.atk, "phys", isPlayer);
    const done = this.take(t, d.amount, a, isPlayer, "phys");
    a.dmg += done;
    if (isPlayer) this.recap.physical += done; else this.recap.taken += done;
    if (d.crit && isPlayer) this.recap.crits += 1;
    if (done > 0) this.float(`${d.crit ? "CRIT " : ""}${Math.round(done)}`, t.x, t.y - 38, d.crit ? "#ffb703" : "#ffffff", "phys");
    this.event(`${a.name}: attack ${Math.round(done)}`, isPlayer ? "#ffffff" : "#ef476f");

    if (!isPlayer) return;
    const f = BranchSystem.effects(this.state);

    // DoT / debuff procs on hit
    if (f.toxinHit  && this.rng() < f.toxinHit)  this.addStatus(t, { type: "toxin", dur: 4, tick: (f.toxinTick || 6) * (1 + (f.toxinBoost || 0)), stacks: 1 });
    if (f.woundHit  && this.rng() < f.woundHit)  this.addStatus(t, { type: "wound", dur: 5, amp: f.woundAmp || .04, stacks: 1 });
    if (f.iceHit    && this.rng() < f.iceHit)     this.addStatus(t, { type: "ice",   dur: 3, slow: f.slow || .1, stacks: 1 });
    if (f.stunHit   && this.rng() < f.stunHit)    this.addStatus(t, { type: "stun",  dur: .25 });

    // Attack speed burst on every 5th hit
    if (f.tempo && a.cnt % 5 === 0) {
      a.energy = Math.min(a.energyMax, a.energy + f.tempo);
      this.float(`⚡ +${Math.round(f.tempo)}`, a.x, a.y - 55, "#ffb703", "buff");
    }

    // Multi-hit (extra light swing)
    if (f.multiHit && this.rng() < f.multiHit) {
      const dd = this.take(t, Math.max(1, a.atk * .45), a, true, "phys");
      a.dmg += dd;
      this.recap.physical += dd;
      if (dd > 0) this.float(`+${Math.round(dd)}`, t.x + 22, t.y - 18, "#ffffff", "phys");
    }

    // Lifesteal: heal attacker for % of damage dealt
    if (f.lifesteal && done > 0) {
      const healed = done * f.lifesteal;
      this.heal(a, healed);
    }
  }

  // ── Skill ──────────────────────────────────────────────────────────────────

  skill(a, t, s, isPlayer) {
    a.energy  -= s.energy;
    a.skillCd  = s.cd;
    a.castPulse = 1;
    a.lastAction = s.name || "Skill";
    a.actionLife = 1.2;
    this.recap.skills += isPlayer ? 1 : 0;
    this.trail(a, t, isPlayer ? "#9b5cff" : "#ff7b8a", "skill");

    const f    = isPlayer ? BranchSystem.effects(this.state) : {};
    const hits = s.hits || 1;
    for (let i = 0; i < hits; i++) {
      const base = (s.type === "phys" ? a.atk : a.focus) * s.pow * (1 + (isPlayer ? (f.skillPower || 0) : 0));
      const d    = this.damage(a, t, base, s.type, isPlayer);
      const done = this.take(t, d.amount, a, isPlayer, s.type);
      a.dmg += done;
      if (isPlayer) {
        if (s.type === "phys") this.recap.physical += done; else this.recap.magic += done;
        if (d.crit) this.recap.crits += 1;
      } else this.recap.taken += done;
      if (done > 0) this.float(`${d.crit ? "CRIT " : ""}${Math.round(done)}`, t.x + i * 14, t.y - 48, s.type === "magic" ? "#9b5cff" : "#ffb703", s.type);

      // Lifesteal on skill hit
      if (isPlayer && f.lifesteal && done > 0) this.heal(a, done * f.lifesteal);
    }
    this.event(`${a.name}: ${s.name}`, isPlayer ? "#9b5cff" : "#ff7b8a");

    if (s.status) this.addStatus(t, { type: s.status, dur: s.dur || 3, tick: s.dot || 14, stacks: 1 });

    // Echo: chance to repeat skill at reduced power
    if (isPlayer && f.echo && this.rng() < f.echo) {
      const done = this.take(t, Math.max(1, a.focus * .5), a, true, "magic");
      a.dmg += done;
      this.recap.magic += done;
      if (done > 0) this.float(`ECHO ${Math.round(done)}`, t.x - 22, t.y - 60, "#9b5cff", "magic");
    }

    // Power damage: flat bonus on physical skills (power branch)
    if (isPlayer && f.powerDamage && s.type === "phys") {
      const bonusDmg = this.take(t, f.powerDamage, a, true, "phys");
      a.dmg += bonusDmg;
      this.recap.physical += bonusDmg;
      if (bonusDmg > 0) this.float(`PWR +${Math.round(bonusDmg)}`, t.x + 26, t.y - 56, "#fb5607", "phys");
    }
  }

  // ── Damage calc ────────────────────────────────────────────────────────────

  damage(a, t, base, type, isPlayer) {
    // Opening crits: first N attacks always crit (GIFT OF FREEDOM)
    let crit = (isPlayer && a.openingCritsLeft > 0)
      ? (a.openingCritsLeft--, true)
      : this.rng() < clamp(a.crit, 0, .9);

    let amount = base;
    if (crit)            amount *= a.critD;
    if (type === "phys") amount -= t.arm;

    const f = isPlayer ? BranchSystem.effects(this.state) : {};

    // Wound amplification
    const wound = t.status.find(s => s.type === "wound");
    if (wound) amount *= 1 + (wound.amp || .05) * (wound.stacks || 1);

    // Execute: bonus damage at low HP
    if (isPlayer && f.execute && t.hp / t.max <= .3) amount *= 1 + f.execute;

    return { amount: Math.max(1, amount), crit };
  }

  // ── Take damage ────────────────────────────────────────────────────────────

  take(t, amount, src, fromPlayer, type) {
    if (amount <= 0) return 0;

    // Phase immunity proc (TRICKERY): chance to negate hit entirely
    if (t === this.player && t.phaseCooldown <= 0) {
      const f = BranchSystem.effects(this.state);
      if (f.phaseChance && this.rng() < f.phaseChance) {
        t.phaseCooldown = 0.5;  // 0.5s cooldown before next proc
        this.float("PHASE", t.x, t.y - 28, "#9b5cff", "buff");
        this.event(`${t.name}: phase immunity!`, "#9b5cff");
        return 0;
      }
    }

    // Dodge
    if ((t.dodge || 0) > 0 && type === "phys" && this.rng() < t.dodge) {
      this.float("MISS", t.x, t.y - 28, "#70e000", "miss");
      if (t === this.player) this.recap.dodges += 1;

      // Dodge reflect (DIVINE REFLECTION): bounce % of damage as magic
      if (t === this.player && src) {
        const f = BranchSystem.effects(this.state);
        if (f.dodgeReflect) {
          const reflected = Math.max(1, amount * f.dodgeReflect);
          this.take(src, reflected, t, true, "magic");
          this.float(`↩ ${Math.round(reflected)}`, src.x, src.y - 28, "#9b5cff", "magic");
          this.recap.magic += reflected;
        }
      }
      return 0;
    }

    // Shield absorption
    const shield = t.status.find(s => s.type === "shield" && s.val > 0);
    if (shield) {
      const absorb = Math.min(shield.val, amount);
      shield.val  -= absorb;
      amount      -= absorb;
      if (absorb > 0) {
        if (t === this.player) this.recap.shielded += absorb;
        this.float(`🛡 ${Math.round(absorb)}`, t.x, t.y + 8, "#48cae4", "shield");
      }
    }

    // Shield reduction (passive)
    const f = t === this.player ? BranchSystem.effects(this.state) : {};
    if (f.shieldReduction) amount *= 1 - Math.min(.75, f.shieldReduction);
    if (amount <= 0) return 0;

    // Counter-attack on taking damage (COURAGEOUS MOMENT)
    if (t === this.player && src && f.counterHit && this.rng() < f.counterHit) {
      const dd = Math.max(1, t.atk * .5);
      // Apply directly to avoid recursion
      const actualCounter = Math.max(0, dd - src.arm);
      if (actualCounter > 0) {
        src.hp = Math.max(0, src.hp - actualCounter);
        src.taken += actualCounter;
        t.dmg += actualCounter;
        this.recap.physical += actualCounter;
        this.float(`⚡ ${Math.round(actualCounter)}`, src.x, src.y - 44, "#ffb703", "phys");
        this.event(`${t.name}: counter-attack!`, "#ffb703");
      }
    }

    t.hp    = Math.max(0, t.hp - amount);
    t.taken += amount;
    this.hitFlash = 1;

    // Death prevention (BERSERKER FRENZY / LAST STAND)
    if (t.hp <= 0 && t.deathShieldCharges > 0) {
      t.deathShieldCharges--;
      t.hp = 1;
      this.addStatus(t, { type: "shield", dur: 3, val: Math.round(t.max * .35) });
      this.float("LAST STAND!", t.x, t.y - 62, "#ffb703", "special");
      this.event(`${t.name}: death prevented!`, "#ffb703");
    }

    return amount;
  }

  // ── Healing ────────────────────────────────────────────────────────────────

  heal(a, amount) {
    const f = a === this.player ? BranchSystem.effects(this.state) : {};
    const before = a.hp;
    a.hp = Math.min(a.max, a.hp + amount * (1 + (f.healBoost || 0)));
    const gained = a.hp - before;
    if (gained > 1) {
      a.heal += gained;
      if (a === this.player) this.recap.heals += gained;
      this.float(`+${Math.round(gained)}`, a.x, a.y - 42, "#06d6a0", "heal");
    }
  }

  // ── Status management ──────────────────────────────────────────────────────

  addStatus(t, s) {
    if (s.type === "shield") {
      t.status.push(s);
      this.event(`${t.name}: shield`, "#48cae4");
      return;
    }
    const stackable = ["toxin", "wound", "ice", "burn"];
    const existing  = t.status.find(x => x.type === s.type && stackable.includes(s.type));
    if (existing) {
      existing.dur    = Math.max(existing.dur, s.dur);
      existing.stacks = Math.min(20, (existing.stacks || 1) + 1);
      existing.tick   = Math.max(existing.tick || 0, s.tick || 0);
      existing.amp    = Math.max(existing.amp  || 0, s.amp  || 0);
      existing.slow   = Math.max(existing.slow || 0, s.slow || 0);
    } else {
      t.status.push(s);
    }
    this.event(`${t.name}: ${s.type}`, this.statusColor(s.type));
  }

  has(a, type) { return a.status.some(s => s.type === type && s.dur > 0); }

  tickStatus(a, dt) {
    for (let i = a.status.length - 1; i >= 0; i--) {
      const s = a.status[i];
      if (["toxin", "burn"].includes(s.type)) {
        const done = this.take(a, (s.tick || 0) * (s.stacks || 1) * dt, null, false, "dot");
        if (a === this.enemy)  this.recap.dot   += done;
        else                   this.recap.taken += done;
        if (done > 0 && Math.random() < .08)
          this.float(Math.round(done), a.x - 18, a.y - 35, this.statusColor(s.type), "dot");
      }
      s.dur -= dt;
      if (s.dur <= 0) a.status.splice(i, 1);
    }
    // Expire depleted shields
    for (let i = a.status.length - 1; i >= 0; i--) {
      const s = a.status[i];
      if (s.type === "shield" && s.val <= 0 && s.dur < 90) a.status.splice(i, 1);
    }
  }

  // ── Finish ─────────────────────────────────────────────────────────────────

  finish() {
    const won =
      this.enemy.hp  <= 0 && this.player.hp > 0 ? true  :
      this.player.hp <= 0 && this.enemy.hp  > 0 ? false :
      (this.player.hp / this.player.max) >= (this.enemy.hp / this.enemy.max);

    this.result = won ? "win" : "loss";
    const state = this.state;
    state.stats.damage  += this.player.dmg;
    state.stats.taken   += this.player.taken;
    state.stats.healing += this.player.heal;

    if (won) {
      state.stats.wins += 1;
      state.winStreak  += 1;
      state.lossStreak  = 0;
      this.pushLog("Vittoria: +50 e streak.");
      EconomySystem.income(state, true, 0);
    } else {
      const hpLost = EconomySystem.lifeDamage(state, this.enemy.level || 3);
      this.hpLost = hpLost;
      state.stats.losses   += 1;
      state.lossStreak     += 1;
      state.winStreak       = 0;
      state.life            = Math.max(0, state.life - hpLost);
      state.stats.hpLost   += hpLost;
      this.pushLog(`Sconfitta: -${hpLost} HP run.`);
      EconomySystem.income(state, false, hpLost);
    }
  }

  // ── Helpers ────────────────────────────────────────────────────────────────

  statusColor(type) {
    return { toxin: "#70e000", burn: "#fb5607", wound: "#ef476f", ice: "#7bdff2", stun: "#ffb703", shield: "#48cae4" }[type] || "#fff";
  }

  trail(a, t, color, kind) {
    this.trails.push({ x1: a.x, y1: a.y, x2: t.x, y2: t.y, color, kind, life: .32, t: 0 });
  }

  pushLog(msg) {
    this.log.unshift(msg);
    if (this.log.length > 4) this.log.pop();
  }

  event(text, color = "#fff") {
    this.events.unshift({ text, color, life: 2.4 });
    if (this.events.length > 6) this.events.pop();
  }

  float(text, x, y, color = "#fff", type = "generic") {
    this.floaters.push({ text, x, y, color, type, life: .85 });
  }
}
