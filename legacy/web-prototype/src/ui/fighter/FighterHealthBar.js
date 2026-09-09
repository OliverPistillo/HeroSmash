import { FighterTheme, drawSlantedBar, drawHexPortrait, fitText } from "./FighterTheme.js";

export class FighterHealthBar {
  constructor(o){ Object.assign(this,o); }

  draw(r){
    const {x,y,w,side="left",unit,portrait,name=unit?.name||"Fighter",subtitle=unit?.title||unit?.heroName||"",level=1} = this;
    const c = FighterTheme.colors;
    const isLeft = side === "left";
    const h = 82;
    const ps = 70;
    const px = isLeft ? x + 10 : x + w - ps - 10;
    const tx = isLeft ? x + 94 : x + 18;
    const textW = w - 120;
    const align = isLeft ? "left" : "right";
    const nameX = isLeft ? tx : x + w - 94;
    const barX = isLeft ? tx : x + 18;
    const barW = w - 122;
    const hp = unit?.hp ?? 0;
    const max = unit?.max ?? 1;
    const hpPct = hp / Math.max(1,max);
    const hpFill = hpPct > .55 ? c.green : hpPct > .25 ? c.gold : c.red;

    r.roundRect(x,y,w,h,14,"rgba(6,8,16,.58)","rgba(255,202,58,.22)",1.2);
    r.ctx.save();
    const gloss = r.ctx.createLinearGradient(x,y,x,y+h);
    gloss.addColorStop(0,"rgba(255,255,255,.07)");
    gloss.addColorStop(.48,"rgba(255,255,255,.015)");
    gloss.addColorStop(1,"rgba(0,0,0,.30)");
    r.ctx.fillStyle = gloss;
    r.roundRect(x,y,w,h,14,gloss);
    r.ctx.restore();

    drawHexPortrait(r,portrait,px,y+6,ps,{stroke:c.gold,lineWidth:2.2});
    r.roundRect(isLeft ? px+48 : px+4, y+56, 24, 18, 7, "rgba(0,0,0,.66)", "rgba(255,202,58,.34)");
    r.text(level,isLeft ? px+60 : px+16,y+65,{align:"center",baseline:"middle",size:11,weight:950,color:c.gold});

    r.text(fitText(name,16).toUpperCase(),nameX,y+11,{align,size:18,weight:950,color:c.ivory,shadow:true});
    r.text(fitText(subtitle,24).toUpperCase(),nameX,y+35,{align,size:10,weight:850,color:c.muted});
    drawSlantedBar(r,barX,y+49,barW,15,hpPct,hpFill,{fill2:hpFill,bg:"rgba(0,0,0,.58)",stroke:"rgba(255,255,255,.16)",cut:9});
    r.text(`${Math.ceil(hp)} / ${Math.ceil(max)}`,barX+barW/2,y+56.5,{align:"center",baseline:"middle",size:11,weight:950,color:"#fff",shadow:true});
    drawSlantedBar(r,barX+16,y+68,barW-32,6,(unit?.energy??0)/100,c.blue,{fill2:c.cyan,bg:"rgba(0,0,0,.52)",stroke:"rgba(255,255,255,.10)",cut:5});
  }
}
