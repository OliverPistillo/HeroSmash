import { FighterTheme, drawBeveledPanel } from "./FighterTheme.js";
export class CombatBanner {
  constructor(){this.active=null;this.life=0;this.maxLife=0}
  show(text,variant="gold",duration=1.4){this.active={text,variant};this.life=duration;this.maxLife=duration}
  update(dt){if(!this.active)return;this.life-=dt;if(this.life<=0)this.active=null}
  draw(r){if(!this.active)return;const {text,variant}=this.active,pct=Math.max(0,this.life/Math.max(.01,this.maxLife)),alpha=Math.min(1,pct*1.8),scale=1+(1-pct)*.08,c=FighterTheme.colors,color=variant==="danger"?c.red:variant==="violet"?c.violet:c.gold;r.ctx.save();r.ctx.globalAlpha=alpha;r.ctx.translate(683,354);r.ctx.scale(scale,scale);drawBeveledPanel(r,-270,-58,540,116,{cut:32,fill:"rgba(8,10,18,.88)",stroke:color,lineWidth:3});r.text(text.toUpperCase(),0,-5,{align:"center",baseline:"middle",size:56,weight:950,color,shadow:true});r.ctx.restore();}
}
