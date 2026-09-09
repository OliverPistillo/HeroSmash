import { BRANCHES } from "../game/GameState.js";
import { Button } from "../ui/Button.js";
import { MarketScene } from "./MarketScene.js";
import { drawSceneArt, artPanel } from "../ui/ArtScene.js";
import { FighterButton } from "../ui/fighter/FighterButton.js";

export class BranchDraftScene {
  constructor(app) {
    this.app = app;
    this.start = new FighterButton({ x:1080, y:674, w:236, h:58, label:"Vai al Market", onClick:()=>app.scenes.set(MarketScene), variant:"primary", size:18 });
  }

  handleInput(e) { this.start.handle(e); }

  draw(r) {
    const active = new Set(this.app.state.activeBranches);
    drawSceneArt(r, this.app.assets.get("final_arena_bg"), { alpha:.60, overlayBottom:"rgba(7,5,12,.82)" });
    r.topBar("Rami Attivi", "8 disponibili · 4 bannati casualmente");
    artPanel(r, 40, 108, 300, 560, "DRAFT", this.app.assets.get("final_branch_sheet"), { imageAlpha:.34 });
    r.text("Draft rami", 70, 138, { size:28, weight:950, color:"#ffca3a" });
    r.wrap("I rami attivi decidono quali card possono apparire nel market. Le soglie 4 / 10 / 20 / 40 sbloccano potenza e rarità.", 70, 188, 240, 25, { size:16, color:"#d8cfe8", weight:700 });
    r.roundRect(70, 410, 230, 72, 18, "rgba(255,255,255,.07)");
    r.text("Soglie", 90, 426, { size:15, weight:900, color:"#b8adc9" });
    r.text("4 / 10 / 20 / 40", 90, 452, { size:24, weight:950, color:"#ffca3a" });

    BRANCHES.forEach((b,i)=>{
      const col = i % 4, row = Math.floor(i/4);
      const x = 388 + col*162, y = 128 + row*162;
      const on = active.has(b.id);
      r.ctx.globalAlpha = on ? 1 : .34;
      r.roundRect(x, y, 142, 132, 24, on ? "rgba(8,10,18,.88)" : "rgba(40,40,50,.46)", on ? b.color : "rgba(255,255,255,.08)", on ? 2 : 1);
      r.text(b.icon, x+20, y+20, { size:32 });
      r.text(b.name, x+20, y+60, { size:16, weight:950 });
      r.wrap(on ? b.desc : "Bannato in questa run", x+20, y+84, 102, 16, { size:11, color:on ? "#d7cee7" : "#a19aac", weight:700 });
      r.ctx.globalAlpha = 1;
    });

    artPanel(r, 1060, 108, 280, 290, "BRANCH SHEET", this.app.assets.get("final_branch_sheet"), { imageAlpha:.74 });
    r.wrap("Branch sheet integrato come reference visiva. Lo slicing atomico delle icone è un prossimo step, ma il pack non è perso.", 1082, 420, 238, 22, { size:13, color:"#d8cfe8", weight:700 });

    this.start.draw(r);
  }
}
