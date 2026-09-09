import { Button } from "../ui/Button.js";
import { LeagueSystem } from "../game/LeagueSystem.js";
import { RunSystem } from "../game/RunSystem.js";
import { CardSystem } from "../game/CardSystem.js";
import { MarketScene } from "./MarketScene.js";

export class StandingsScene {
  constructor(app) {
    this.app = app;
    this.next = new Button({ x:1066, y:670, w:260, h:58, label:"Prossimo Market", onClick:()=>this.goNext(), variant:"primary", size:18 });
  }

  goNext() {
    RunSystem.advanceRound(this.app.state);
    CardSystem.rollShop(this.app.state, this.app.rng);
    this.app.scenes.set(MarketScene);
  }

  handleInput(events) { this.next.handle(events); }

  draw(r) {
    const s = this.app.state;
    const standings = LeagueSystem.standings(s);
    r.bg();
    r.topBar("Classifica League", `Round ${s.round} completato`);

    r.panel(42, 102, 590, 570, .78);
    r.text("Risultati Round", 78, 132, { size:24, weight:950, color:"#ffb703" });
    const results = s.roundResults || [];
    if (!results.length) r.text("Nessun risultato", 78, 178, { size:14, color:"#b8adc9" });
    results.slice(0, 8).forEach((res,i)=>{
      const y = 178+i*52;
      const human = res.loser==="you" || res.winner==="you";
      r.roundRect(78, y, 510, 38, 14, human ? "rgba(255,183,3,.13)" : "rgba(255,255,255,.055)");
      r.text(res.text, 98, y+10, { size:14, color:res.loser==="you" ? "#ef476f" : res.winner==="you" ? "#06d6a0" : "#fff", weight:850 });
    });

    r.panel(688, 102, 638, 570, .78);
    r.text("8 Player League", 724, 132, { size:24, weight:950, color:"#ffb703" });
    standings.forEach((p,i)=>{
      const col = i < 4 ? 0 : 1;
      const row = i % 4;
      const x = 724 + col*292, y = 184 + row*94;
      const alive = !p.eliminated && p.life > 0;
      r.roundRect(x, y, 260, 70, 18, p.id==="you" ? "rgba(255,183,3,.16)" : alive ? "rgba(255,255,255,.055)" : "rgba(239,71,111,.08)", "rgba(255,255,255,.09)");
      r.text(`#${i+1}`, x+16, y+24, { size:14, color:"#b8adc9", weight:950 });
      r.text(`${p.hero.icon} ${p.name}`, x+58, y+13, { size:14, weight:950, color:alive?"#fff":"#888" });
      r.text(`${p.stats.wins}-${p.stats.losses}`, x+58, y+40, { size:12, color:"#b8adc9", weight:850 });
      r.text(`${p.life}/100`, x+238, y+24, { align:"right", size:18, color:alive?"#06d6a0":"#ef476f", weight:950 });
    });
    this.next.draw(r);
  }
}
