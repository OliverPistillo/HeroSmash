import { FighterTheme, drawBeveledPanel } from "./FighterTheme.js";
export class BranchProgressPanel {
  constructor(o={}){Object.assign(this,o)}
  draw(r,branches=[]){const x=this.x??1056,y=this.y??154,w=this.w??292,h=this.h??390;drawBeveledPanel(r,x,y,w,h,{cut:18,fill:"rgba(6,8,16,.82)",stroke:"rgba(255,202,58,.24)"});r.text("BRANCH SYNERGIES",x+22,y+18,{size:14,weight:950,color:FighterTheme.colors.gold});branches.slice(0,8).forEach((b,i)=>{const yy=y+54+i*39,pts=b.points||0,near=(b.next||40)-pts<=2&&pts<40;r.roundRect(x+18,yy,w-36,29,9,near?"rgba(255,202,58,.14)":"rgba(255,255,255,.055)",near?FighterTheme.colors.gold:"rgba(255,255,255,.08)");r.text(`${b.icon} ${b.name}`,x+30,yy+7,{size:11,weight:900});r.text(`${pts}/40`,x+w-30,yy+7,{align:"right",size:11,weight:950,color:near?FighterTheme.colors.gold:FighterTheme.colors.muted});r.roundRect(x+118,yy+20,w-160,4,2,"rgba(255,255,255,.10)");r.roundRect(x+118,yy+20,Math.min(w-160,(w-160)*pts/40),4,2,b.color);});}
}
