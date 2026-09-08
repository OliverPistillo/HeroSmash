import { FighterTheme, drawBeveledPanel } from "./FighterTheme.js";
export class FighterButton {
  constructor(o){Object.assign(this,o);this.variant??="secondary";this.p=false;this.disabled??=false}
  contains(x,y){return x>=this.x&&x<=this.x+this.w&&y>=this.y&&y<=this.y+this.h}
  handle(ev){if(this.disabled)return false;for(const e of ev){if(e.type==="down"&&this.contains(e.x,e.y))this.p=true;if(e.type==="up"){const was=this.p;this.p=false;if(was&&this.contains(e.x,e.y)){try{navigator.vibrate?.(10)}catch{}this.onClick?.();return true}}}return false}
  draw(r){const c=FighterTheme.colors,fill=this.disabled?"rgba(255,255,255,.05)":this.variant==="primary"?"rgba(255,202,58,.88)":this.variant==="danger"?"rgba(239,35,60,.86)":"rgba(9,12,20,.86)",stroke=this.variant==="primary"?c.gold:this.variant==="danger"?c.red:"rgba(255,202,58,.34)";drawBeveledPanel(r,this.x,this.y+(this.p?2:0),this.w,this.h,{cut:Math.min(16,this.h*.35),fill,stroke,lineWidth:1.5});r.text(this.label,this.x+this.w/2,this.y+this.h/2+(this.p?2:0),{align:"center",baseline:"middle",size:this.size||14,weight:950,color:this.variant==="primary"?"#1a0d00":"#fff"});}
}
