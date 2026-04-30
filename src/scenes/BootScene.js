import { HomeScene } from "./HomeScene.js";
import { GameState } from "../game/GameState.js";
import {
  loadGameData,
  ASSET_REGISTRY,
  ASSET_MANIFEST,
  FINAL_ART_MANIFEST,
  CARD_FRAMES_MANIFEST,
  BRANCH_ICONS_MANIFEST,
  MARKET_UI_MANIFEST,
  RUNTIME
} from "../game/GameData.js";

export class BootScene {
  constructor(app) {
    this.app = app;
    this.progress = 0;
    this._phase = 'data';
    this.error = null;
  }

  async enter() {
    // Phase 0: dati gameplay/runtime. Da qui in poi i JSON sono la fonte autorevole.
    this._phase = 'data';
    try {
      await loadGameData('data');
      this.app.state = new GameState(this.app.save);
    } catch (e) {
      console.error("Runtime data load failed", e);
      this.error = e;
      return;
    }

    // Phase 1: art assets
    this._phase = 'assets';
    try {
      await this.app.assets.loadFromRegistry(ASSET_REGISTRY);
      await this.app.assets.loadImages(FINAL_ART_MANIFEST);
      await this.app.assets.loadImages(CARD_FRAMES_MANIFEST);
      await this.app.assets.loadImages(BRANCH_ICONS_MANIFEST);
      await this.app.assets.loadImages(MARKET_UI_MANIFEST);
    } catch (e) {
      console.warn("Registry load failed, fallback to JSON simple manifest", e);
      const m = {};
      for (const [k,v] of Object.entries(ASSET_MANIFEST.heroes || {})) m[k] = v;
      for (const [k,v] of Object.entries(ASSET_MANIFEST.cards || {}))  m[k] = v;
      for (const [k,v] of Object.entries(FINAL_ART_MANIFEST || {}))     m[k] = v;
      for (const [k,v] of Object.entries(CARD_FRAMES_MANIFEST || {}))   m[k] = v;
      for (const [k,v] of Object.entries(BRANCH_ICONS_MANIFEST || {}))  m[k] = v;
      for (const [k,v] of Object.entries(MARKET_UI_MANIFEST || {}))      m[k] = v;
      await this.app.assets.loadImages(m);
    }

    // Phase 2: sprite sheets (non-blocking, graceful degradation per hero mancante)
    this._phase = 'sprites';
    try {
      const res = await fetch('data/sprites_manifest.json');
      if (res.ok) {
        const spritesManifest = await res.json();
        await this.app.assets.loadAllSpriteSheets(spritesManifest, this.app.anim);
      }
    } catch (e) {
      console.warn("Sprite sheets non trovati, usando fallback cerchi", e);
    }

    this.app.scenes.set(HomeScene);
  }

  update() { this.progress = this.app.assets.progress; }

  draw(r) {
    const keyart = this.app.assets.get("final_home_keyart");
    if (keyart) {
      r.ctx.drawImage(keyart, 0, 0, 1366, 768);
      const g = r.ctx.createLinearGradient(0,0,0,768);
      g.addColorStop(0,"rgba(10,8,22,.18)"); g.addColorStop(1,"rgba(6,5,11,.88)");
      r.ctx.fillStyle=g; r.ctx.fillRect(0,0,1366,768);
    } else r.bg();

    r.topBar(RUNTIME.title || "Hero Smash", `${RUNTIME.label || "v1.7"} — ${RUNTIME.subtitle || "Runtime JSON"}`);
    r.roundRect(520,206,326,326,48,"rgba(255,202,58,.16)","rgba(255,255,255,.20)",2);
    r.text("HS",683,366,{align:"center",baseline:"middle",size:124,weight:950,color:"#ffca3a",shadow:true});
    const label = this.error
      ? "Errore caricamento dati runtime"
      : this._phase === 'data' ? "Caricamento JSON runtime…"
      : this._phase === 'sprites' ? "Caricamento sprite…"
      : "Caricamento assets";
    r.text(label,683,550,{align:"center",size:26,weight:950,color:this.error?"#ef476f":"#fff"});
    if (this.error) {
      r.wrap(String(this.error.message || this.error), 438, 586, 490, 22, { size:15, color:"#ffd6df", weight:800, align:"center" });
      return;
    }
    r.roundRect(438,595,490,24,12,"rgba(255,255,255,.10)");
    r.roundRect(438,595,490*this.progress,24,12,"#ffca3a");
    r.text(`${Math.round(this.progress*100)}%`,683,628,{align:"center",size:14,color:"#b8adc9",weight:800});
  }
}
