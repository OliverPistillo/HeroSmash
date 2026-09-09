import { CombatSystem } from "../game/CombatSystem.js";
import { RunSystem } from "../game/RunSystem.js";
import { LeagueSystem } from "../game/LeagueSystem.js";
import { BranchSystem } from "../game/BranchSystem.js";
import { SummaryScene } from "./SummaryScene.js";
import { MarketScene } from "./MarketScene.js";
import { drawSceneArt } from "../ui/ArtScene.js";
import { FighterHealthBar } from "../ui/fighter/FighterHealthBar.js";
import { RoundTimer } from "../ui/fighter/RoundTimer.js";
import { StatusIconBar } from "../ui/fighter/StatusIconBar.js";
import { CombatBanner } from "../ui/fighter/CombatBanner.js";
import { FighterButton } from "../ui/fighter/FighterButton.js";
import { drawBeveledPanel, FighterTheme } from "../ui/fighter/FighterTheme.js";
import { drawHpStandingsBanner, drawBranchReportBanner, drawCardDrawer, pointInRect } from "../ui/fighter/OverlayUI.js";
import { loadArena } from "../arena/ArenaLoader.js";
import { ParallaxArena } from "../arena/ParallaxArena.js";
import { CardSystem } from "../game/CardSystem.js";
import { CinematicSystem } from "../engine/CinematicSystem.js";

// Dimensioni sprite a schermo
const SPRITE_W = 160, SPRITE_H = 240;

export class CombatScene {
  constructor(app) {
    this.app = app;
    app.state.preGold = app.state.gold;
    app.state.startBattle?.();
    this.combat = new CombatSystem(app.state, app.rng);
    this.cin    = new CinematicSystem();

    this.resolvedLeague   = false;
    this.showHelp         = false;
    this.resultBannerShown= false;
    this.burstDone        = false;
    this.lastTrailCount   = 0;
    this.arena            = null;
    this.arenaReady       = false;
    this.drawerInfo       = null;
    this.arenaPanel       = { x:0, y:0, w:1366, h:768 };

    this.timer  = new RoundTimer({ x:624, y:16 });
    this.banner = new CombatBanner();
    this.banner.show("Round Start", "gold", 1.2);

    this.next  = new FighterButton({ x:1196, y:704, w:140, h:40, label:"Market", onClick:()=>this.goNext(), variant:"primary", size:12 });
    this.resultHold = 0;
    this.autoAdvanced = false;
    this.speed = new FighterButton({ x:1196, y:654, w:66,  h:36, label:`x${app.speed}`, onClick:()=>this.cycleSpeed(), variant:"secondary", size:12 });
    this.help  = new FighterButton({ x:1270, y:654, w:66,  h:36, label:"Info", onClick:()=>this.showHelp=!this.showHelp, variant:"secondary", size:12 });

    // Avvia animazioni idle per entrambi i fighter
    const playerId  = app.state.hero?.id;
    const enemyId   = this.combat.enemy?.id;
    if (playerId) { app.anim.setState(playerId,  'idle'); }
    if (enemyId)  { app.anim.setState(enemyId,   'idle'); }
  }

  async enter() {
    try {
      const { config, images } = await loadArena("data/arenas/arena01_beast_crucible.json");
      this.arena = new ParallaxArena(config, images, { showDebug: false });
      this.arenaReady = true;
      this.syncArenaPositions();
    } catch (e) {
      console.warn("Arena01 failed to load, using static background.", e);
    }
  }

  syncArenaPositions() {
    if (!this.arena?.config?.fighters) return;
    const design = this.arena.config.sourceResolution || { width:2048, height:1152 };
    const map    = (p) => ({ x:(p.x/design.width)*1366, y:(p.y/design.height)*768 });
    const pp = map(this.arena.config.fighters.player), ep = map(this.arena.config.fighters.enemy);
    const cx = 683;
    this.combat.player.x = cx + (pp.x - cx) * 1.20;
    this.combat.enemy.x  = cx + (ep.x - cx) * 1.20;
    this.combat.player.y = pp.y - 16;
    this.combat.enemy.y  = ep.y - 16;
    this.combat.player.r = 36;
    this.combat.enemy.r  = 36;
  }

  cycleSpeed() { this.app.speed = this.app.speed===1?2:this.app.speed===2?3:1; this.speed.label = `x${this.app.speed}`; }

  goNext() {
    if (!this.resolvedLeague) {
      const results = LeagueSystem.resolveRound(this.app.state, this.combat.result==="win", this.combat.hpLost||0, this.app.rng);
      this.storeRoundRecap(results);
      this.resolvedLeague = true;
    }
    if (RunSystem.isOver(this.app.state)) { this.app.state.finishRun(); this.app.scenes.set(SummaryScene); }
    else { RunSystem.advanceRound(this.app.state); this.app.scenes.set(MarketScene); }
  }

  storeRoundRecap(results = []) {
    const state = this.app.state;
    const standings = LeagueSystem.standings(state);
    const rank = Math.max(1, standings.findIndex(p => p.id === "you") + 1);
    const aliveCount = standings.filter(p => !p.eliminated && p.life > 0).length;
    const humanResult = results.find(r => r.winner === "you" || r.loser === "you");
    const victory = this.combat.result === "win";

    state.lastRoundRecap = {
      round: state.round,
      result: this.combat.result,
      victory,
      opponentName: state.currentOpponent?.name || this.combat.enemy?.name || "Opponent",
      opponentHero: state.currentOpponent?.hero?.name || this.combat.enemy?.heroName || "Enemy",
      hpLost: victory ? (humanResult?.hpLost || 0) : (this.combat.hpLost || 0),
      playerHp: state.life,
      gold: state.gold,
      goldDelta: state.gold - (state.preGold ?? state.gold),
      rank,
      aliveCount,
      recap: { ...(this.combat.recap || {}) },
      results: results.map(r => ({ ...r })),
      standings: standings.slice(0, 8).map((p, i) => ({
        rank: i + 1,
        id: p.id,
        name: p.name,
        life: p.life,
        eliminated: !!p.eliminated,
        wins: p.stats?.wins || 0,
        losses: p.stats?.losses || 0,
        icon: p.hero?.icon || p.icon || "◆"
      })),
      seen: false
    };
  }

  // ── Update ────────────────────────────────────────────────────────────────

  update(dt) {
    this.banner.update(dt);
    if (this.arena) this.arena.update(dt);
    this.app.particles.update(dt);

    const simDt = dt * this.app.speed;

    // Cinematic system sempre avanza
    this.cin.update(simDt);

    // Combat simulation solo quando non in INTRO
    if (!this.cin.isCombatPaused()) {
      this.combat.update(simDt);
    }

    // Trigger cinematic KO al termine del combat
    if (this.combat.result && !this.resultBannerShown) {
      this.resultBannerShown = true;
      this.cin.triggerKO();
      this.banner.show(
        this.combat.result === "win" ? "Victory" : "Defeat",
        this.combat.result === "win" ? "gold" : "danger",
        2.2
      );
    }

    // Particle burst KO
    if (this.combat.result && !this.burstDone && this.cin.isInKO()) {
      this.burstDone = true;
      if (this.arena) this.arena.impact("heavy");
      const loser = this.combat.result === "win" ? this.combat.enemy : this.combat.player;
      this.app.particles.burst(loser.x, loser.y, this.combat.result==="win" ? "#ffca3a" : "#ef233c", 52);
      this.app.audio.beep(this.combat.result==="win" ? 720 : 180, .12, "square");
    }

    // Fight banner
    if (!this._fightBannerShown && this.cin.isFighting() && this.combat.time <= 0.1) {
      this._fightBannerShown = true;
      this.banner.show("Fight!", "gold", .9);
    }

    // Trail impact
    if (this.arena && this.combat.trails.length > this.lastTrailCount) {
      this.arena.impact(this.combat.trails.some(t => t.kind==="skill") ? "medium" : "small");
      this.lastTrailCount = this.combat.trails.length;
    }

    // Aggiorna animazioni
    this._updateAnimations(simDt);

    // Dopo KO/victory: niente schermata intermedia, si torna al market nell'arena.
    if (this.combat.result && this.cin.isDone() && !this.autoAdvanced) {
      this.resultHold += dt;
      if (this.resultHold >= 1.15) {
        this.autoAdvanced = true;
        this.goNext();
      }
    }
  }

  _updateAnimations(dt) {
    const anim    = this.app.anim;
    const p       = this.combat.player;
    const e       = this.combat.enemy;
    const playerId= this.app.state.hero?.id;
    const enemyId = e?.id;

    if (playerId) {
      const state = this.cin.getAnimState(p, this.combat.result, true);
      anim.setState(playerId, state);
      anim.update(playerId, dt);
    }
    if (enemyId) {
      const state = this.cin.getAnimState(e, this.combat.result, false);
      anim.setState(enemyId, state);
      anim.update(enemyId, dt);
    }
  }

  toggleCards() { this.app.state.ui ??= {}; this.app.state.ui.cardsOpen = !this.app.state.ui.cardsOpen; }

  handleInput(events) {
    for (const ev of events)
      if (ev.type === "up" && pointInRect(ev.x, ev.y, this.drawerInfo?.toggle)) { this.toggleCards(); return; }
    this.speed.handle(events);
    this.help.handle(events);
    if (this.combat.result && this.cin.isDone()) this.next.handle(events);
  }

  branchData() {
    const s = this.app.state;
    return BranchSystem.activeBranchObjects(s).map(b => {
      const points = BranchSystem.points(s, b.id);
      return { ...b, points, next: BranchSystem.nextThreshold(points) };
    });
  }

  // ── Draw ──────────────────────────────────────────────────────────────────

  drawArena(r) {
    if (this.arenaReady && this.arena) this.arena.draw(r.ctx, 1366, 768, null);
    else drawSceneArt(r, this.app.assets.get("final_combat_bg") || this.app.assets.get("final_arena_bg"), {
      alpha:.62, overlayTop:"rgba(6,8,16,.08)", overlayBottom:"rgba(6,5,10,.38)"
    });
    const g = r.ctx.createRadialGradient(683,398,0,683,398,520);
    g.addColorStop(0,"rgba(255,255,255,.03)"); g.addColorStop(.65,"rgba(0,0,0,.05)"); g.addColorStop(1,"rgba(0,0,0,.40)");
    r.ctx.fillStyle=g; r.ctx.fillRect(0,0,1366,768);
  }

  drawTrail(r, t) {
    const k=Math.min(1,t.t), x=t.x1+(t.x2-t.x1)*k, y=t.y1+(t.y2-t.y1)*k;
    r.ctx.save();
    r.ctx.globalAlpha=Math.max(0,t.life/.32); r.ctx.strokeStyle=t.color; r.ctx.lineWidth=t.kind==="skill"?7:4;
    r.ctx.beginPath(); r.ctx.moveTo(t.x1,t.y1); r.ctx.lineTo(x,y); r.ctx.stroke();
    r.ctx.fillStyle=t.color; r.ctx.beginPath(); r.ctx.arc(x,y,t.kind==="skill"?8:5,0,Math.PI*2); r.ctx.fill();
    r.ctx.restore();
  }

  /**
   * Disegna un fighter — usa sprite se disponibile, altrimenti cerchio.
   * @param {Renderer} r
   * @param {object}   u         — fighter
   * @param {boolean}  isPlayer
   * @param {number}   overrideX — X override per l'intro
   */
  drawUnit(r, u, isPlayer, overrideX = null) {
    const heroId   = isPlayer ? this.app.state.hero?.id : u.id;
    const drawX    = overrideX ?? u.x;
    const anim     = this.app.anim;

    if (heroId && anim.hasSprite(heroId)) {
      this._drawUnitSprite(r, u, heroId, drawX, isPlayer);
    } else {
      this._drawUnitCircle(r, u, drawX);
    }

    // Status icons e label azione (sempre sopra, indipendente dal tipo di render)
    if (u.actionLife > 0 && u.lastAction) {
      r.roundRect(drawX-92, u.y-u.r-92, 184, 24, 12, "rgba(0,0,0,.64)", "rgba(255,202,58,.22)");
      r.text(u.lastAction, drawX, u.y-u.r-80, {align:"center", baseline:"middle", size:11, weight:950, color:"#ffca3a"});
    }
    new StatusIconBar({x:drawX, y:u.y-u.r-56, align:"center", size:28}).draw(r, u.status||[]);
  }

  _drawUnitSprite(r, u, heroId, cx, isPlayer) {
    const frame = this.app.anim.getFrame(heroId);
    if (!frame) { this._drawUnitCircle(r, u, cx); return; }

    const dx = cx - SPRITE_W / 2;
    const dy = u.y  - SPRITE_H + 20;  // piedi a u.y

    // Ombra ovale
    r.ctx.save();
    r.ctx.globalAlpha = 0.38;
    r.ctx.fillStyle = "rgba(0,0,0,.5)";
    r.ctx.beginPath();
    r.ctx.ellipse(cx, u.y + 6, 60, 15, 0, 0, Math.PI * 2);
    r.ctx.fill();
    r.ctx.restore();

    // Skill ready ring
    if (u.intent === "SKILL READY" && !this.combat.result) {
      r.ctx.save();
      r.ctx.strokeStyle = "rgba(255,202,58,.50)";
      r.ctx.lineWidth = 3;
      r.ctx.setLineDash([8, 8]);
      r.ctx.beginPath();
      r.ctx.ellipse(cx, u.y - SPRITE_H * 0.3, SPRITE_W * 0.45, SPRITE_H * 0.45, 0, 0, Math.PI * 2);
      r.ctx.stroke();
      r.ctx.setLineDash([]);
      r.ctx.restore();
    }

    // Cast pulse glow
    if ((u.castPulse||0) > 0) {
      r.ctx.save();
      r.ctx.strokeStyle = `rgba(155,92,255,${(u.castPulse||0) * 0.65})`;
      r.ctx.lineWidth = 5;
      r.ctx.beginPath();
      r.ctx.ellipse(cx, u.y - SPRITE_H * 0.3, (SPRITE_W * 0.45) + 20 * (u.castPulse||0),
                    (SPRITE_H * 0.45) + 28 * (u.castPulse||0), 0, 0, Math.PI * 2);
      r.ctx.stroke();
      r.ctx.restore();
    }

    // Tint danno subito (flash bianco)
    const hitFlash = this.combat.hitFlash > 0 && u === (isPlayer ? this.combat.player : this.combat.enemy);
    const tintAlpha = hitFlash ? this.combat.hitFlash * 0.35 : 0;

    // Player non viene specchiato (già nel foglio), il nemico sì
    const flipX = !isPlayer;
    r.drawSpriteColored(frame.image, frame.sx, frame.sy, frame.sw, frame.sh,
                        dx, dy, SPRITE_W, SPRITE_H, flipX,
                        "#ffffff", tintAlpha);
  }

  _drawUnitCircle(r, u, cx) {
    r.ctx.save();
    const pulse = 1 + (u.attackPulse||0)*.12 + (u.castPulse||0)*.18;
    r.ctx.fillStyle = "rgba(0,0,0,.34)";
    r.ctx.beginPath(); r.ctx.ellipse(cx, u.y+u.r*.95, u.r*1.8, u.r*.44, 0, 0, Math.PI*2); r.ctx.fill();
    if (u.intent==="SKILL READY" && !this.combat.result) {
      r.ctx.strokeStyle="rgba(255,202,58,.48)"; r.ctx.lineWidth=3; r.ctx.setLineDash([8,8]);
      r.ctx.beginPath(); r.ctx.arc(cx,u.y,u.r+20,0,Math.PI*2); r.ctx.stroke(); r.ctx.setLineDash([]);
    }
    if ((u.castPulse||0)>0) {
      r.ctx.strokeStyle=`rgba(155,92,255,.60)`; r.ctx.lineWidth=5;
      r.ctx.beginPath(); r.ctx.arc(cx,u.y,u.r+32*u.castPulse,0,Math.PI*2); r.ctx.stroke();
    }
    const g=r.ctx.createLinearGradient(cx-u.r,u.y-u.r,cx+u.r,u.y+u.r);
    g.addColorStop(0,u.color); g.addColorStop(1,"rgba(255,255,255,.25)");
    r.ctx.fillStyle=g; r.ctx.beginPath(); r.ctx.arc(cx,u.y,u.r*pulse,0,Math.PI*2); r.ctx.fill();
    r.ctx.strokeStyle="#fff"; r.ctx.lineWidth=3; r.ctx.stroke();
    r.text(u.icon,cx,u.y+2,{align:"center",baseline:"middle",size:28,weight:900,color:"#100c1a"});
    r.ctx.restore();
  }

  // ── Cinematic overlays ────────────────────────────────────────────────────

  drawIntroOverlay(r) {
    if (!this.cin.isInIntro()) return;
    const p = this.cin.progress;
    // Name tags che appaiono al centro
    if (p > 0.5) {
      const a = Math.min(1, (p - 0.5) * 2);
      r.ctx.save();
      r.ctx.globalAlpha = a;
      // Player name
      r.roundRect(530, 340, 300, 44, 14, "rgba(0,0,0,.72)", "rgba(255,202,58,.45)", 2);
      r.text(this.combat.player.name, 680, 362, {align:"center", baseline:"middle", size:18, weight:950, color:"#fff"});
      // Enemy name
      r.roundRect(536, 388, 294, 44, 14, "rgba(0,0,0,.72)", "rgba(255,255,255,.20)", 2);
      r.text(this.combat.enemy.name, 683, 410, {align:"center", baseline:"middle", size:18, weight:950, color:"#cfc4dd"});
      r.ctx.restore();
    }
  }

  drawKOOverlay(r) {
    if (!this.cin.isInKO()) return;
    // Flash bianco
    const fa = this.cin.koFlashAlpha;
    if (fa > 0) {
      r.ctx.save();
      r.ctx.globalAlpha = fa;
      r.ctx.fillStyle = "#ffffff";
      r.ctx.fillRect(0, 0, 1366, 768);
      r.ctx.restore();
    }
    // "KO" banner al centro
    if (this.cin.progress > 0.2) {
      const scale = Math.min(1, (this.cin.progress - 0.2) * 1.6);
      r.ctx.save();
      r.ctx.globalAlpha = Math.min(1, (this.cin.progress - 0.2) * 2.5);
      r.ctx.translate(683, 340);
      r.ctx.scale(scale, scale);
      r.text("KO", 0, 0, {align:"center", baseline:"middle", size:88, weight:950, color:"#ffca3a", shadow:true});
      r.ctx.restore();
    }
  }

  drawVictoryOverlay(r) {
    if (!this.cin.isInVictory()) return;
    const winnerName = this.combat.result === "win" ? this.combat.player.name : this.combat.enemy.name;
    const p = Math.min(1, this.cin.t / 0.5);
    r.ctx.save();
    r.ctx.globalAlpha = p;
    r.roundRect(434, 310, 498, 54, 16, "rgba(0,0,0,.78)", "rgba(255,202,58,.55)", 2);
    r.text(`${winnerName} WINS`, 683, 337, {align:"center", baseline:"middle", size:24, weight:950, color:"#ffca3a", shadow:true});
    r.ctx.restore();
  }

  // ── Existing draw helpers ─────────────────────────────────────────────────

  drawCombatLog(r) {
    const c = this.combat;
    drawBeveledPanel(r,1118,520,220,34,{cut:12,fill:"rgba(6,8,16,.42)",stroke:"rgba(255,202,58,.18)"});
    r.text(c.events[0]?.text||"",1132,530,{size:11,weight:850,color:c.events[0]?.color||FighterTheme.colors.muted});
  }

  drawRecap(r) {
    const c=this.combat, rec=c.recap;
    drawBeveledPanel(r,468,174,430,268,{cut:24,fill:"rgba(6,8,16,.82)",stroke:"rgba(255,202,58,.42)",lineWidth:2});
    r.text(c.result==="win"?"VICTORY":"DEFEAT",683,198,{align:"center",size:34,weight:950,color:c.result==="win"?"#ffca3a":"#ef233c"});
    const rows=[["⚔️ Physical",Math.round(rec.physical)],["🔮 Magic",Math.round(rec.magic)],
                ["☠️ DoT",Math.round(rec.dot)],["🎯 Crit",rec.crits],
                ["💚 Heal",Math.round(rec.heals)],["💔 Taken",Math.round(rec.taken)]];
    rows.forEach((row,i)=>{const x=520+(i%2)*180,y=256+Math.floor(i/2)*42;
      r.text(row[0],x,y,{size:13,color:"#cfc4dd",weight:850});
      r.text(row[1],x+140,y,{align:"right",size:16,weight:950,color:"#fff"});
    });
  }

  drawLegend(r) {
    if (!this.showHelp) return;
    r.ctx.save(); r.ctx.fillStyle="rgba(0,0,0,.72)"; r.ctx.fillRect(0,0,1366,768); r.ctx.restore();
    drawBeveledPanel(r,400,126,566,500,{cut:26,fill:"#111626",stroke:"rgba(255,202,58,.45)",lineWidth:2});
    r.text("Come leggere il combat",683,158,{align:"center",size:28,weight:950,color:"#ffca3a"});
    const items=[["Cards","apre/chiude il drawer delle carte"],["Classifica HP","banner overlay a sinistra"],
                 ["Branch Report","banner overlay a destra"],["Arena01","layer 2.5D con parallax"],
                 ["Round banner","timer centrale compatto"],["Status","icone sopra i fighter"]];
    items.forEach((it,i)=>{const y=226+i*48;r.roundRect(450,y,466,34,14,"rgba(255,255,255,.06)");
      r.text(it[0],470,y+9,{size:13,weight:950,color:"#fff"});
      r.text(it[1],630,y+9,{size:13,weight:800,color:"#cfc4dd"});
    });
  }

  // ── Main draw ─────────────────────────────────────────────────────────────

  draw(r) {
    const c = this.combat, p = c.player, e = c.enemy;
    const playerId = this.app.state.hero?.id;

    this.drawArena(r);

    // HUD
    new FighterHealthBar({x:24,y:18,w:440,side:"left",unit:p,portrait:this.app.assets.get(playerId),name:p.name,subtitle:this.app.state.hero?.title||p.heroName||"Player",level:7}).draw(r);
    new FighterHealthBar({x:902,y:18,w:440,side:"right",unit:e,portrait:this.app.assets.get(e.id),name:e.name,subtitle:e.heroName||"Opponent",level:7}).draw(r);
    this.timer.draw(r,{round:this.app.state.round,time:Math.max(0,c.maxTime-c.time),phase:c.result?"END":"FIGHT"});
    drawHpStandingsBanner(r,this.app.state.league?.players||[],{x:28,y:166,w:220,h:336});
    drawBranchReportBanner(r,this.branchData(),{x:1118,y:166,w:220,h:336});

    // Trails
    for (const t of c.trails) this.drawTrail(r, t);

    // Fighter draw con eventuale override X durante intro
    const px = this.cin.isInIntro() ? this.cin.introX(false, e.x) : null;  // enemy entra da sinistra
    const ex = this.cin.isInIntro() ? this.cin.introX(true,  p.x) : null;  // player entra da destra
    this.drawUnit(r, e, false, px);
    this.drawUnit(r, p, true,  ex);

    this.app.particles.draw(r);

    // Floaters
    for (const f of c.floaters)
      r.text(f.text, f.x, f.y, {align:"center", size:16, weight:950, color:f.color, shadow:true});

    // Overlays cinematici
    this.drawIntroOverlay(r);
    this.drawKOOverlay(r);
    if (this.cin.isInVictory()) this.drawVictoryOverlay(r);

    // Recap / log
    if (c.result && this.cin.isDone()) this.drawRecap(r);
    else if (!c.result || this.cin.isInKO() || this.cin.isInVictory()) this.drawCombatLog(r);

    // Card drawer
    const drawerCards = this.app.state.shop?.length ? this.app.state.shop : CardSystem.ownedCards(this.app.state);
    this.drawerInfo = drawCardDrawer(r,{open:this.app.state.ui?.cardsOpen===true,cards:drawerCards,levels:this.app.state.cardLevels,assets:this.app.assets,mode:"battle",x:356,y:624,w:654,h:118});

    // Bottoni
    this.speed.draw(r);
    this.help.draw(r);
    if (c.result && this.cin.isDone()) this.next.draw(r);
    this.banner.draw(r);
    this.drawLegend(r);
  }
}
