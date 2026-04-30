import { Button } from "../ui/Button.js";
import { HomeScene } from "./HomeScene.js";
import { HeroSelectScene } from "./HeroSelectScene.js";
import { CARDS } from "../game/GameState.js";
import { BranchSystem } from "../game/BranchSystem.js";
import { LeagueSystem } from "../game/LeagueSystem.js";

export class SummaryScene {
  constructor(app) {
    this.app = app;
    this.buttons = [
      new Button({ x:874, y:620, w:220, h:58, label:"Nuova Run", onClick:()=>app.scenes.set(HeroSelectScene), variant:"primary", size:18 }),
      new Button({ x:1110, y:620, w:180, h:58, label:"Home", variant:"secondary", onClick:()=>app.scenes.set(HomeScene), size:18 })
    ];
  }

  handleInput(e) { this.buttons.forEach(b=>b.handle(e)); }

  archetype() {
    const s={};
    for (const b of this.app.state.activeBranches) s[b]=BranchSystem.points(this.app.state,b);
    return Object.entries(s).sort((a,b)=>b[1]-a[1]).slice(0,2).map(([id])=>id).join(" + ") || "improvvisata";
  }

  draw(r) {
    const s = this.app.state;
    const owned = CARDS.filter(c=>s.cardLevels[c.id]>0);
    const standings = s.league ? LeagueSystem.standings(s) : [];
    const rank = standings.findIndex(p=>p.id==="you")+1;

    r.bg();
    r.topBar(s.life>0 ? "Run completata" : "Run terminata", rank ? `Rank #${rank} nella league` : "Summary");

    r.panel(60, 110, 470, 540, .78);
    r.text(`${s.hero?.icon || ""} ${s.hero?.name || "-"}`, 100, 145, { size:34, weight:950, color:"#ffb703" });
    const lines = [["Round",`${s.round}/${s.maxRound}`],["HP Run",`${s.life}/100`],["Wins/Losses",`${s.stats.wins}/${s.stats.losses}`],["Archetipo",this.archetype()],["Danno",Math.round(s.stats.damage)],["Subito",Math.round(s.stats.taken)],["Cure",Math.round(s.stats.healing)],["Cards",owned.length],["Coins",s.gold]];
    lines.forEach((line,i)=>{
      const y=214+i*42;
      r.text(line[0],100,y,{size:15,color:"#b8adc9",weight:850});
      r.text(line[1],486,y,{align:"right",size:16,weight:950});
    });

    r.panel(586, 110, 720, 450, .78);
    r.text("Build finale", 626, 145, { size:26, weight:950, color:"#ffb703" });
    const names = owned.map(c=>`${c.icon} ${c.name} Lv ${s.cardLevels[c.id]}`);
    if (!names.length) r.text("Nessuna carta", 626, 192, { size:15, color:"#b8adc9" });
    names.slice(0,16).forEach((name,i)=>{
      const col=i%2,row=Math.floor(i/2),x=626+col*330,y=194+row*38;
      r.roundRect(x,y,300,28,12,"rgba(255,255,255,.055)");
      r.text(name,x+12,y+7,{size:12,weight:850});
    });

    this.buttons.forEach(b=>b.draw(r));
  }
}
