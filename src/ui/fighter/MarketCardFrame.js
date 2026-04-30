import { FighterTheme } from "./FighterTheme.js";

export class MarketCardFrame {
  constructor(card,x,y,w,h,level=0,o={}){Object.assign(this,{card,x,y,w,h,level,o})}
  contains(x,y){return x>=this.x&&x<=this.x+this.w&&y>=this.y&&y<=this.y+this.h}
  rarityColor(){return FighterTheme.rarity[this.card.rarity]||FighterTheme.colors.gold}
  draw(r,assets){
    const c=this.rarityColor(),x=this.x,y=this.y,w=this.w,h=this.h,compact=this.o?.compact || h<100;
    r.roundRect(x,y,w,h,compact?14:18,"rgba(8,10,18,.76)",c,compact?1.4:2);
    r.roundRect(x+4,y+4,w-8,h-8,compact?11:14,"rgba(255,255,255,.025)","rgba(255,255,255,.07)");

    if (compact) {
      r.roundRect(x+8,y+8,30,22,8,"rgba(0,0,0,.68)",c,1);
      r.text(this.card.cost,x+23,y+19,{align:"center",baseline:"middle",size:11,weight:950,color:FighterTheme.colors.ivory});
      r.text(this.card.icon||"◆",x+w-21,y+20,{align:"center",baseline:"middle",size:16,weight:950,color:c});
      r.text(String(this.card.name).toUpperCase(),x+w/2,y+41,{align:"center",size:10.5,weight:950,color:"#fff"});
      r.text(`${this.card.rarity} · Lv ${this.level}/${this.card.max}`,x+w/2,y+60,{align:"center",size:8.5,weight:900,color:c});
      return;
    }

    const imgTop = y + 9;
    const imgH = Math.max(52, h - 68);
    r.roundRect(x+10,imgTop,w-20,imgH,14,"rgba(255,255,255,.06)","rgba(255,255,255,.08)");
    const img = assets?.get?.(this.card.id);
    if (img) r.img(img,x+10,imgTop,w-20,imgH,14);
    else r.text(this.card.icon||"◆",x+w/2,imgTop+imgH/2,{align:"center",baseline:"middle",size:48,weight:950,color:c});

    r.roundRect(x+8,y+8,36,28,10,"rgba(0,0,0,.72)",c,1.2);
    r.text(this.card.cost,x+26,y+22,{align:"center",baseline:"middle",size:15,weight:950,color:FighterTheme.colors.ivory});
    r.roundRect(x+w-42,y+8,34,28,10,"rgba(0,0,0,.66)",c,1.2);
    r.text(this.card.icon||"◆",x+w-25,y+22,{align:"center",baseline:"middle",size:15,weight:950,color:c});

    r.roundRect(x+10,y+h-52,w-20,42,12,"rgba(0,0,0,.78)");
    r.text(String(this.card.name).toUpperCase(),x+w/2,y+h-45,{align:"center",size:11,weight:950,color:"#fff"});
    r.text(`${this.card.rarity} · Lv ${this.level}/${this.card.max}`,x+w/2,y+h-25,{align:"center",size:9,weight:900,color:c});
  }
}
