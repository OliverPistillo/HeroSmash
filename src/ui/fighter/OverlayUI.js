import { FighterTheme, drawBeveledPanel, fitText, drawSlantedBar } from "./FighterTheme.js";
import { MarketCardFrame } from "./MarketCardFrame.js";

export function drawHpStandingsBanner(r, players = [], opts = {}) {
  const x = opts.x ?? 28, y = opts.y ?? 166, w = opts.w ?? 220, h = opts.h ?? 336;
  drawBeveledPanel(r,x,y,w,h,{cut:18,fill:"rgba(6,8,16,.38)",stroke:"rgba(255,202,58,.28)",lineWidth:1.2});
  r.text("CLASSIFICA HP",x+w/2,y+18,{align:"center",size:13,weight:950,color:FighterTheme.colors.ivory,shadow:true});
  const list = [...players].sort((a,b)=>(b.life||0)-(a.life||0)).slice(0,8);
  if(!list.length){r.wrap("La league si inizializza al primo round.",x+20,y+54,w-40,17,{size:11,color:FighterTheme.colors.muted,weight:700});return;}
  list.forEach((p,i)=>{
    const yy=y+44+i*34, alive=!p.eliminated&&p.life>0, isYou=p.id==="you";
    r.roundRect(x+10,yy,w-20,27,9,isYou?"rgba(255,202,58,.20)":"rgba(255,255,255,.040)",isYou?"rgba(255,202,58,.30)":"rgba(255,255,255,.06)");
    r.text(i+1,x+22,yy+7,{size:12,weight:950,color:FighterTheme.colors.gold});
    r.text(`${p.hero?.icon||p.icon||"◆"} ${fitText(p.name||"Bot",12)}`,x+42,yy+7,{size:10.5,weight:900,color:alive?"#fff":"#777"});
    r.text(alive?`❤ ${p.life}`:"KO",x+w-20,yy+7,{align:"right",size:10.5,weight:950,color:alive?FighterTheme.colors.green:FighterTheme.colors.red});
  });
}

export function drawBranchReportBanner(r, branches = [], opts = {}) {
  const x = opts.x ?? 1118, y = opts.y ?? 166, w = opts.w ?? 220, h = opts.h ?? 336;
  drawBeveledPanel(r,x,y,w,h,{cut:18,fill:"rgba(6,8,16,.38)",stroke:"rgba(255,202,58,.28)",lineWidth:1.2});
  r.text("BRANCH REPORT",x+w/2,y+18,{align:"center",size:13,weight:950,color:FighterTheme.colors.ivory,shadow:true});
  const thresholds = "4/10/20/40";
  branches.slice(0,8).forEach((b,i)=>{
    const yy=y+46+i*34, pts=b.points||0, active=pts>0, near=(b.next||40)-pts<=2&&pts<40;
    r.roundRect(x+10,yy,w-20,27,9,active?"rgba(255,255,255,.060)":"rgba(255,255,255,.030)",near?FighterTheme.colors.gold:"rgba(255,255,255,.055)");
    r.text(b.icon||"◆",x+26,yy+13.5,{align:"center",baseline:"middle",size:15,weight:950,color:b.color||FighterTheme.colors.gold});
    r.text(fitText(b.name,11),x+44,yy+7,{size:10.5,weight:900,color:active?"#fff":FighterTheme.colors.muted});
    r.text(`${pts}/${thresholds}`,x+w-18,yy+7,{align:"right",size:10.5,weight:950,color:active?(b.color||FighterTheme.colors.gold):"rgba(255,255,255,.42)"});
  });
}

export function drawCompactEconomy(r, state, opts = {}) {
  const x = opts.x ?? 28, y = opts.y ?? 680, w = opts.w ?? 202, h = opts.h ?? 58;
  drawBeveledPanel(r,x,y,w,h,{cut:14,fill:"rgba(6,8,16,.45)",stroke:"rgba(255,202,58,.24)",lineWidth:1.1});
  const totalLv = Math.min(15,Object.values(state.cardLevels||{}).reduce((a,b)=>a+b,0));
  r.text(`Lv. ${Math.max(1,Math.ceil(totalLv/2))}`,x+20,y+14,{size:15,weight:950,color:FighterTheme.colors.ivory});
  r.text(`${totalLv}/56`,x+w-18,y+16,{align:"right",size:10.5,weight:900,color:FighterTheme.colors.ivory});
  drawSlantedBar(r,x+20,y+34,w-40,6,(totalLv%56)/56,FighterTheme.colors.blue,{cut:5});
  r.text("🪙",x+20,y+50,{size:14,baseline:"middle"});
  r.text(state.gold ?? 0,x+44,y+50,{baseline:"middle",size:19,weight:950,color:FighterTheme.colors.gold});
  const interest = Math.min(100, Math.floor((state.preGold||0)/100)*10);
  r.text(`+${interest}`,x+w-18,y+50,{align:"right",baseline:"middle",size:16,weight:950,color:FighterTheme.colors.green});
}

export function drawCardDrawer(r, { open = true, cards = [], levels = {}, assets = null, mode = "shop", x = 356, y = 624, w = 654, h = 118 } = {}) {
  const isBattle = mode === "battle";
  const toggle = open
    ? { x:x+w/2-76, y:y-36, w:152, h:30, label:isBattle ? "Hide Cards" : "Hide Cards ▲" }
    : { x:x+w/2-62, y:728, w:124, h:28, label:"Cards ▲" };
  drawBeveledPanel(r,toggle.x,toggle.y,toggle.w,toggle.h,{cut:12,fill:"rgba(6,8,16,.70)",stroke:isBattle?"rgba(72,202,228,.38)":"rgba(255,202,58,.38)",lineWidth:1.2});
  r.text(toggle.label,toggle.x+toggle.w/2,toggle.y+toggle.h/2,{align:"center",baseline:"middle",size:11.5,weight:950,color:FighterTheme.colors.ivory});
  if (!open) return { toggle, cardRects: [] };

  drawBeveledPanel(r,x,y,w,h,{cut:18,fill:isBattle?"rgba(4,7,16,.64)":"rgba(6,8,16,.50)",stroke:isBattle?"rgba(72,202,228,.26)":"rgba(255,202,58,.24)",lineWidth:1.2});
  const title = mode === "shop" ? "MARKET CARDS" : isBattle ? "CARTE · CONSULTAZIONE" : "COLLECTION";
  r.text(title, x+18, y+11, { size:11, weight:950, color:isBattle?FighterTheme.colors.blue:FighterTheme.colors.gold });
  if(isBattle){
    r.text("Market chiuso durante la battle", x+w-18, y+11, { align:"right", size:10, weight:850, color:FighterTheme.colors.muted });
  }

  const shown = cards.slice(0,4);
  const cardRects = [];
  shown.forEach((card,i)=>{
    const cx = x + 72 + i*146, cy = y + 25, cw = 128, ch = 84;
    cardRects.push({ card, x:cx, y:cy, w:cw, h:ch });
    new MarketCardFrame(card,cx,cy,cw,ch,levels[card.id]||0,{compact:true, showCost:true}).draw(r,assets);
  });
  if (!shown.length) r.text("Nessuna carta",x+w/2,y+h/2,{align:"center",baseline:"middle",size:15,weight:950,color:FighterTheme.colors.muted});
  return { toggle, cardRects };
}

export function pointInRect(px,py,rect){return rect && px>=rect.x && px<=rect.x+rect.w && py>=rect.y && py<=rect.y+rect.h;}
