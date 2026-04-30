import { BRANCHES, HEROES, heroFavoredBranches } from "../game/GameState.js";
import { MarketScene } from "./MarketScene.js";
import { HomeScene } from "./HomeScene.js";
import { drawSceneArt } from "../ui/ArtScene.js";
import { FighterTheme, fitText } from "../ui/fighter/FighterTheme.js";
import { RUNTIME } from "../game/GameState.js";

const T = FighterTheme.colors;
const DRAFT_TIME_LIMIT = 20;

function pointInRect(x, y, rect) {
  return !!rect && x >= rect.x && x <= rect.x + rect.w && y >= rect.y && y <= rect.y + rect.h;
}

function panel(r, x, y, w, h, opts = {}) {
  const ctx = r.ctx;
  const radius = opts.radius ?? 22;
  ctx.save();
  ctx.shadowColor = opts.shadow || "rgba(0,0,0,.48)";
  ctx.shadowBlur = opts.blur ?? 18;
  ctx.shadowOffsetY = opts.offsetY ?? 6;
  r.roundRect(x, y, w, h, radius, opts.fill || "rgba(5,8,18,.74)", opts.stroke || "rgba(255,255,255,.10)", opts.lineWidth ?? 1.2);
  ctx.restore();

  const g = ctx.createLinearGradient(x, y, x, y + h);
  g.addColorStop(0, "rgba(255,255,255,.070)");
  g.addColorStop(.48, "rgba(255,255,255,.018)");
  g.addColorStop(1, "rgba(0,0,0,.16)");
  ctx.save();
  ctx.beginPath();
  ctx.roundRect(x, y, w, h, radius);
  ctx.clip();
  ctx.fillStyle = g;
  ctx.fillRect(x, y, w, h);
  ctx.restore();
}

function glowText(r, text, x, y, opts = {}) {
  const ctx = r.ctx;
  ctx.save();
  if (opts.glow) {
    ctx.shadowColor = opts.glow;
    ctx.shadowBlur = opts.glowBlur ?? 14;
  }
  r.text(text, x, y, opts);
  ctx.restore();
}

function button(r, rect, label, opts = {}) {
  const ctx = r.ctx;
  const disabled = !!opts.disabled;
  const active = !!opts.active;
  const fill = disabled
    ? "rgba(70,70,80,.42)"
    : active
      ? (opts.activeFill || "rgba(255,202,58,.92)")
      : (opts.fill || "rgba(8,13,28,.78)");
  const stroke = disabled
    ? "rgba(255,255,255,.10)"
    : active
      ? "rgba(255,246,214,.78)"
      : (opts.stroke || "rgba(255,202,58,.34)");

  ctx.save();
  if (!disabled && opts.glow) {
    ctx.shadowColor = opts.glow;
    ctx.shadowBlur = opts.glowBlur ?? 14;
  }
  r.roundRect(rect.x, rect.y, rect.w, rect.h, opts.radius ?? 16, fill, stroke, opts.lineWidth ?? 1.4);
  ctx.restore();

  r.text(label, rect.x + rect.w / 2, rect.y + rect.h / 2, {
    align:"center",
    baseline:"middle",
    size:opts.size ?? 12,
    weight:950,
    color:disabled ? "rgba(255,255,255,.38)" : (active ? "#241200" : (opts.color || "#f8f1df"))
  });
}

function statBar(r, x, y, w, label, value, max, color) {
  const pct = Math.max(0, Math.min(1, value / Math.max(1, max)));
  r.text(label, x, y, { size:10.5, weight:950, color:"#b8adc9" });
  r.text(String(value), x + w, y, { align:"right", size:10.5, weight:950, color:"#fff" });
  r.roundRect(x, y + 10, w, 7, 4, "rgba(0,0,0,.42)");
  r.roundRect(x, y + 10, Math.max(4, w * pct), 7, 4, color);
}

function branchInfo(branchId) {
  return BRANCHES.find(b => b.id === branchId);
}

export class HeroSelectScene {
  constructor(app) {
    this.app = app;
    this.heroRects = [];
    this.rerollRects = [];
    this.rects = { back:null, confirm:null };
    this.selectedHeroId = null;
    this.toast = null;
    this.draftTimeLimit = DRAFT_TIME_LIMIT;
    this.draftTimeLeft = DRAFT_TIME_LIMIT;
    this.timerResolved = false;

    if (!app.state.activeBranches?.length || app.state.hero) app.state.beginHeroDraft(app.rng);
    if (!app.state.heroDraft?.choices?.length) app.state.rollHeroDraft(app.rng);
  }

  choiceHeroes() {
    const ids = this.app.state.heroDraft?.choices || [];
    return ids.map(id => HEROES.find(h => h.id === id)).filter(Boolean).slice(0, 3);
  }

  selectedHero() {
    const heroes = this.choiceHeroes();
    return heroes.find(h => h.id === this.selectedHeroId) || null;
  }

  fallbackHero() {
    return this.choiceHeroes()[0] || null;
  }

  selectHero(hero) {
    if (!hero) return;
    this.selectedHeroId = hero.id;
    this.app.audio?.beep?.(360, .04, "triangle");
  }

  confirmHero(auto = false) {
    let hero = this.selectedHero();

    if (!hero && auto) {
      hero = this.fallbackHero();
      this.selectedHeroId = hero?.id || null;
    }

    if (!hero) {
      this.toast = { text:"Seleziona un eroe oppure attendi l'auto-pick", life:1.4 };
      this.app.audio?.beep?.(180, .05, "sawtooth");
      return;
    }

    this.timerResolved = true;
    this.app.state.startRun(hero.id, this.app.rng);
    this.app.audio?.beep?.(auto ? 460 : 560, .07, "triangle");
    this.app.scenes.set(MarketScene);
  }

  resolveTimer() {
    if (this.timerResolved) return;
    this.timerResolved = true;
    if (!this.selectedHero()) {
      const fallback = this.fallbackHero();
      this.selectedHeroId = fallback?.id || null;
    }
    this.confirmHero(true);
  }

  rerollSlot(index) {
    if ((this.app.state.heroDraft?.rerollsLeft || 0) <= 0) {
      this.toast = { text:"Nessun reroll disponibile", life:1.2 };
      this.app.audio?.beep?.(180, .05, "sawtooth");
      return;
    }

    const before = this.app.state.heroDraft?.choices?.[index];
    const ok = this.app.state.rerollHeroSlot(index, this.app.rng);
    this.app.audio?.beep?.(ok ? 420 : 180, .06, ok ? "triangle" : "sawtooth");

    if (!ok) {
      this.toast = { text:"Nessun altro eroe compatibile disponibile", life:1.3 };
      return;
    }

    const after = this.app.state.heroDraft?.choices?.[index];
    if (this.selectedHeroId === before) this.selectedHeroId = after || null;
  }

  handleInput(events) {
    for (const e of events) {
      if (e.type !== "up") continue;

      if (pointInRect(e.x, e.y, this.rects.back)) {
        this.app.audio?.beep?.(260, .04, "triangle");
        this.app.scenes.set(HomeScene);
        return;
      }

      if (pointInRect(e.x, e.y, this.rects.confirm)) {
        this.confirmHero(false);
        return;
      }

      for (const rr of this.rerollRects) {
        if (pointInRect(e.x, e.y, rr)) {
          this.rerollSlot(rr.index);
          return;
        }
      }

      for (const hr of this.heroRects) {
        if (pointInRect(e.x, e.y, hr) && hr.hero) {
          this.selectHero(hr.hero);
          return;
        }
      }
    }
  }

  update(dt) {
    if (!this.timerResolved) {
      this.draftTimeLeft = Math.max(0, this.draftTimeLeft - dt);
      if (this.draftTimeLeft <= 0) this.resolveTimer();
    }

    if (this.toast) {
      this.toast.life -= dt;
      if (this.toast.life <= 0) this.toast = null;
    }
  }

  drawBranchPill(r, branchId, x, y, opts = {}) {
    const b = branchInfo(branchId);
    if (!b) return;
    const on = opts.on !== false;
    const w = opts.w ?? 94;
    const h = opts.h ?? 26;
    r.roundRect(x, y, w, h, h / 2, on ? "rgba(8,10,18,.76)" : "rgba(40,40,50,.38)", on ? b.color : "rgba(255,255,255,.10)", 1.2);
    r.text(`${b.icon} ${fitText(b.name, 9)}`, x + w / 2, y + h / 2, {
      align:"center",
      baseline:"middle",
      size:10,
      weight:900,
      color:on ? "#fff" : "rgba(230,225,240,.48)"
    });
  }

  drawTopBar(r) {
    panel(r, 24, 16, 1318, 70, {
      radius:20,
      fill:"rgba(4,7,18,.78)",
      stroke:"rgba(255,255,255,.10)",
      blur:10,
      offsetY:2
    });

    this.rects.back = { x:42, y:31, w:120, h:40 };
    button(r, this.rects.back, "‹ HOME", { radius:14, fill:"rgba(255,255,255,.055)", stroke:"rgba(255,202,58,.25)", size:13 });

    r.text("Hero Draft", 683, 38, {
      align:"center",
      size:25,
      weight:950,
      color:"#fff",
      shadow:true
    });
    r.text("Scegli 1 eroe tra 3 · 2 reroll totali", 683, 63, {
      align:"center",
      size:11,
      weight:950,
      color:T.gold
    });

    const seconds = Math.ceil(this.draftTimeLeft);
    const danger = seconds <= 5;
    const timerRect = { x:1124, y:30, w:168, h:42 };
    panel(r, timerRect.x, timerRect.y, timerRect.w, timerRect.h, {
      radius:16,
      fill:danger ? "rgba(100,18,20,.68)" : "rgba(8,13,28,.70)",
      stroke:danger ? "rgba(255,80,80,.56)" : "rgba(76,201,240,.28)",
      blur:danger ? 16 : 8,
      offsetY:2
    });
    r.text("AUTO-PICK", timerRect.x + 18, timerRect.y + 15, {
      size:8.5,
      weight:950,
      color:danger ? "#ff7b7b" : "#7fd2ff"
    });
    glowText(r, `${seconds}s`, timerRect.x + timerRect.w - 24, timerRect.y + 26, {
      align:"right",
      baseline:"middle",
      size:22,
      weight:950,
      color:danger ? "#ffdddd" : "#fff",
      glow:danger ? "#ff5050" : "#4cc9f0",
      glowBlur:danger ? 16 : 10
    });

    const barX = 480, barY = 82, barW = 406, barH = 5;
    const pct = Math.max(0, Math.min(1, this.draftTimeLeft / this.draftTimeLimit));
    r.roundRect(barX, barY, barW, barH, 3, "rgba(0,0,0,.38)");
    r.roundRect(barX, barY, barW * pct, barH, 3, danger ? "rgba(255,80,80,.86)" : "rgba(76,201,240,.82)");
  }

  drawLeftPanel(r) {
    panel(r, 34, 112, 274, 548, {
      radius:24,
      fill:"rgba(4,7,18,.72)",
      stroke:"rgba(76,201,240,.18)"
    });

    r.text("RUN DRAFT", 64, 144, { size:13, weight:950, color:T.gold });
    r.text("Rami attivi", 64, 170, { size:25, weight:950, color:T.gold, shadow:true });
    r.wrap("Gli eroi proposti hanno almeno un ramo favorito compatibile con i rami attivi. I rami bannati non generano carte nella run.", 64, 202, 214, 22, {
      size:12.2,
      color:"#d8cfe8",
      weight:800
    });

    const active = this.app.state.activeBranches || [];
    const banned = this.app.state.bannedBranches?.() || [];
    const startY = 304;
    active.slice(0, 8).forEach((b, i) => {
      const col = i % 2, row = Math.floor(i / 2);
      this.drawBranchPill(r, b, 64 + col * 112, startY + row * 38, { w:100, h:28, on:true });
    });

    r.text("Bannati", 64, 500, { size:14, weight:950, color:"#b8adc9" });
    banned.slice(0, 6).forEach((b, i) => {
      const col = i % 2, row = Math.floor(i / 2);
      this.drawBranchPill(r, b, 64 + col * 112, 526 + row * 36, { w:100, h:26, on:false });
    });

    const rerolls = this.app.state.heroDraft?.rerollsLeft || 0;
    r.roundRect(64, 618, 214, 34, 14, "rgba(255,202,58,.10)", "rgba(255,202,58,.24)");
    r.text(`Reroll disponibili: ${rerolls}`, 171, 635, {
      align:"center",
      baseline:"middle",
      size:12.5,
      weight:950,
      color:T.gold
    });
  }

  drawHeroCard(r, hero, x, y, index) {
    const w = 198, h = 350;
    const selected = hero.id === this.selectedHeroId;
    const favored = heroFavoredBranches(hero);
    const active = new Set(this.app.state.activeBranches || []);
    const compatible = favored.some(b => active.has(b));
    const color = hero.color || T.gold;
    const ctx = r.ctx;

    ctx.save();
    if (selected) {
      ctx.shadowColor = color;
      ctx.shadowBlur = 26;
    }
    panel(r, x, y, w, h, {
      radius:26,
      fill:selected ? "rgba(12,18,36,.90)" : "rgba(6,9,20,.76)",
      stroke:selected ? color : compatible ? "rgba(255,202,58,.25)" : "rgba(255,255,255,.10)",
      lineWidth:selected ? 2.6 : 1.2,
      blur:selected ? 22 : 9,
      offsetY:4
    });
    ctx.restore();

    if (selected) {
      r.roundRect(x + 14, y + 14, w - 28, 5, 3, color);
      r.roundRect(x + 18, y + h - 38, w - 36, 26, 13, "rgba(255,202,58,.18)", "rgba(255,202,58,.38)");
      r.text("SELEZIONATO", x + w / 2, y + h - 25, {
        align:"center",
        baseline:"middle",
        size:10.5,
        weight:950,
        color:T.gold
      });
    }

    r.text(`SLOT ${index + 1}`, x + 22, y + 32, {
      size:9.5,
      weight:950,
      color:selected ? T.gold : "#b8adc9"
    });

    const rr = { x:x + w - 78, y:y + 18, w:58, h:28, index };
    const disabled = (this.app.state.heroDraft?.rerollsLeft || 0) <= 0;
    button(r, rr, "↻", {
      disabled,
      radius:12,
      fill:"rgba(76,201,240,.10)",
      stroke:"rgba(76,201,240,.32)",
      size:15,
      color:"#7fd2ff"
    });
    this.rerollRects.push(rr);

    const img = this.app.assets.get(hero.id);
    r.roundRect(x + 33, y + 62, 132, 132, 22, "rgba(0,0,0,.34)", "rgba(255,255,255,.10)");
    if (img) r.img(img, x + 37, y + 66, 124, 124, 20);
    else r.text(hero.icon, x + w / 2, y + 128, { align:"center", baseline:"middle", size:46 });

    r.text(fitText(hero.name.toUpperCase(), 12), x + w / 2, y + 222, {
      align:"center",
      size:20,
      weight:950,
      color:"#fff",
      shadow:true
    });
    r.text(fitText(hero.title, 20), x + w / 2, y + 248, {
      align:"center",
      size:11.5,
      weight:900,
      color:T.gold
    });

    r.text("Rami favoriti", x + 24, y + 278, { size:10.5, weight:950, color:"#b8adc9" });
    favored.slice(0, 2).forEach((b, i) => {
      this.drawBranchPill(r, b, x + 24 + i * 78, y + 292, { w:72, h:24, on:active.has(b) });
    });

    if (!selected) {
      r.roundRect(x + 22, y + h - 40, w - 44, 28, 14, "rgba(255,255,255,.045)");
      r.text(`HP ${hero.stats.hp} · ATK ${hero.stats.atk}`, x + w / 2, y + h - 26, {
        align:"center",
        baseline:"middle",
        size:10.5,
        weight:850,
        color:"#d8cfe8"
      });
    }

    this.heroRects.push({ x, y, w, h, hero });
  }

  drawCenter(r) {
    panel(r, 326, 112, 708, 548, {
      radius:30,
      fill:"rgba(5,8,18,.74)",
      stroke:"rgba(76,201,240,.18)",
      blur:26,
      offsetY:8
    });

    r.text("SCEGLI IL TUO EROE", 680, 146, {
      align:"center",
      size:17,
      weight:950,
      color:T.gold
    });
    r.text("Tocca una card per selezionarla. Se il timer scade senza scelta, parte automaticamente l'eroe a sinistra.", 680, 170, {
      align:"center",
      size:11.5,
      weight:800,
      color:"#b8adc9"
    });

    this.heroRects = [];
    this.rerollRects = [];

    const heroes = this.choiceHeroes();
    const cardW = 198, gap = 28;
    const totalW = heroes.length * cardW + Math.max(0, heroes.length - 1) * gap;
    const startX = Math.round(326 + (708 - totalW) / 2);

    heroes.forEach((h, i) => {
      this.drawHeroCard(r, h, startX + i * (cardW + gap), 206, i);
    });
  }

  drawRightPanel(r) {
    const hero = this.selectedHero();
    panel(r, 1072, 112, 260, 548, {
      radius:24,
      fill:"rgba(4,7,18,.72)",
      stroke:"rgba(255,202,58,.18)"
    });

    r.text("DETTAGLI", 1102, 144, { size:14, weight:950, color:T.gold });

    if (!hero) {
      r.roundRect(1102, 174, 200, 92, 20, "rgba(255,255,255,.045)", "rgba(255,255,255,.08)");
      r.text("Nessun eroe", 1122, 204, { size:18, weight:950, color:"#fff" });
      r.wrap("Seleziona una card per vedere statistiche e rami favoriti.", 1122, 230, 158, 18, {
        size:11,
        weight:780,
        color:"#b8adc9"
      });
      r.text("AUTO-PICK", 1102, 334, { size:12, weight:950, color:"#7fd2ff" });
      r.wrap("Se il countdown arriva a zero senza selezione, verrà scelto automaticamente il primo eroe a sinistra.", 1102, 360, 198, 20, {
        size:11.5,
        weight:780,
        color:"#d8cfe8"
      });
      return;
    }

    const color = hero.color || T.gold;
    r.roundRect(1102, 174, 70, 70, 20, "rgba(255,255,255,.06)", `${color}66`, 1.5);
    const img = this.app.assets.get(hero.id);
    if (img) r.img(img, 1106, 178, 62, 62, 18);
    else r.text(hero.icon, 1137, 209, { align:"center", baseline:"middle", size:32 });

    r.text(fitText(hero.name.toUpperCase(), 12), 1186, 188, {
      size:19,
      weight:950,
      color:"#fff"
    });
    r.text(fitText(hero.title, 18), 1186, 214, {
      size:11.5,
      weight:900,
      color:T.gold
    });

    r.text("RAMI FAVORITI", 1102, 286, { size:12, weight:950, color:"#7fd2ff" });
    const active = new Set(this.app.state.activeBranches || []);
    heroFavoredBranches(hero).forEach((b, i) => {
      this.drawBranchPill(r, b, 1102 + i * 102, 308, { w:94, h:26, on:active.has(b) });
    });

    r.text("STATISTICHE", 1102, 374, { size:12, weight:950, color:"#7fd2ff" });
    statBar(r, 1102, 402, 194, "HP", hero.stats.hp, 1200, "rgba(112,224,0,.76)");
    statBar(r, 1102, 452, 194, "ATK", hero.stats.atk, 42, "rgba(255,202,58,.82)");
    statBar(r, 1102, 502, 194, "CRIT", Math.round(hero.stats.crit * 100), 25, "rgba(199,125,255,.82)");

    r.roundRect(1102, 574, 200, 48, 18, "rgba(76,201,240,.08)", "rgba(76,201,240,.18)");
    r.text("PROSSIMO STEP", 1120, 591, { size:10.5, weight:950, color:"#7fd2ff" });
    r.text("Market · Round 1", 1120, 610, { size:13, weight:950, color:"#fff" });
  }

  drawBottom(r) {
    const hero = this.selectedHero();
    panel(r, 402, 678, 562, 58, {
      radius:20,
      fill:"rgba(4,7,18,.78)",
      stroke:hero ? "rgba(255,202,58,.28)" : "rgba(255,255,255,.10)",
      blur:12,
      offsetY:2
    });

    r.text(hero ? `Selezionato: ${hero.name}` : "Nessun eroe selezionato", 426, 698, {
      size:12,
      weight:900,
      color:hero ? "#fff" : "#b8adc9"
    });
    r.text(hero ? hero.title : "Alla scadenza: auto-pick del primo eroe", 426, 716, {
      size:10.5,
      weight:800,
      color:hero ? T.gold : "#b8adc9"
    });

    this.rects.confirm = { x:664, y:686, w:278, h:42 };
    button(r, this.rects.confirm, hero ? "CONFERMA FIGHTER" : "SELEZIONA UN EROE", {
      disabled:!hero,
      active:!!hero,
      size:14.5,
      glow:hero ? T.gold : null,
      glowBlur:20,
      radius:17
    });
  }

  drawToast(r) {
    if (!this.toast) return;
    const x = 483, y = 630, w = 400, h = 36;
    r.roundRect(x, y, w, h, 14, "rgba(0,0,0,.84)", "rgba(255,202,58,.36)");
    r.text(this.toast.text, x + w / 2, y + h / 2, {
      align:"center",
      baseline:"middle",
      size:13,
      weight:950,
      color:"#fff"
    });
  }

  draw(r) {
    drawSceneArt(r, this.app.assets.get("final_hero_select_bg") || this.app.assets.get("final_home_keyart"), {
      alpha:.38,
      overlayTop:"rgba(4,7,18,.72)",
      overlayBottom:"rgba(2,3,8,.96)"
    });

    const ctx = r.ctx;
    ctx.save();
    ctx.fillStyle = "rgba(0,0,0,.46)";
    ctx.fillRect(0,0,1366,768);
    ctx.restore();

    const vignette = ctx.createRadialGradient(683, 380, 80, 683, 380, 700);
    vignette.addColorStop(0, "rgba(76,201,240,.08)");
    vignette.addColorStop(.42, "rgba(0,0,0,.12)");
    vignette.addColorStop(1, "rgba(0,0,0,.64)");
    ctx.fillStyle = vignette;
    ctx.fillRect(0, 0, 1366, 768);

    this.drawTopBar(r);
    this.drawLeftPanel(r);
    this.drawCenter(r);
    this.drawRightPanel(r);
    this.drawBottom(r);
    this.drawToast(r);

    r.text(RUNTIME.label || "v1.14.3", 683, 754, {
      align:"center",
      size:10.5,
      color:"rgba(255,255,255,.32)",
      weight:800
    });
  }
}
