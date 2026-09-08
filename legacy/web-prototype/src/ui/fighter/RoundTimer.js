import { FighterTheme, drawBeveledPanel } from "./FighterTheme.js";
export class RoundTimer {
  constructor(o={}){ Object.assign(this,o); }
  draw(r,{round=1,time=0,phase="FIGHT"}={}){
    const x=this.x??624, y=this.y??16, c=FighterTheme.colors;
    drawBeveledPanel(r,x,y,118,86,{cut:18,fill:"rgba(8,10,18,.70)",stroke:"rgba(255,202,58,.42)",lineWidth:1.6});
    r.text(`ROUND ${round}`,x+59,y+13,{align:"center",size:11,weight:950,color:c.gold});
    r.text(String(Math.max(0,Math.ceil(time))).padStart(2,"0"),x+59,y+29,{align:"center",size:38,weight:950,color:c.ivory,shadow:true});
    r.text(phase.toUpperCase(),x+59,y+69,{align:"center",size:10,weight:900,color:c.muted});
  }
}
