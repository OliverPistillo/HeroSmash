import { HeroSelectScene } from "./HeroSelectScene.js";
import { drawSceneArt } from "../ui/ArtScene.js";
import { FighterTheme } from "../ui/fighter/FighterTheme.js";
import { RUNTIME } from "../game/GameState.js";

const T = FighterTheme.colors;

const MODES = [
  {
    id: "ranked",
    label: "CLASSIFICATA",
    short: "Ranked",
    icon: "🏆",
    status: "PROSSIMAMENTE",
    enabled: false,
    title: "Partite classificate",
    desc: "Scala la lega stagionale, ottieni punti ranking e sblocca ricompense competitive.",
    meta: ["8 giocatori", "Ranking attivo", "Ricompense stagionali"]
  },
  {
    id: "normal",
    label: "NORMALE",
    short: "Normal",
    icon: "⚔",
    status: "PROSSIMAMENTE",
    enabled: false,
    title: "Partite normali",
    desc: "Gioca senza perdere ranking. Modalità ideale per provare build e strategie.",
    meta: ["8 giocatori", "No ranking", "XP standard"]
  },
  {
    id: "bots",
    label: "ALLENAMENTO BOT",
    short: "Bots",
    icon: "🤖",
    status: "DISPONIBILE",
    enabled: true,
    title: "Allenamento contro bot",
    desc: "La modalità attuale: draft eroe, market, arena e league gestita da bot.",
    meta: ["Offline", "Bot league", "Test build"]
  },
  {
    id: "private",
    label: "LOBBY PRIVATA",
    short: "Private",
    icon: "🔐",
    status: "PROSSIMAMENTE",
    enabled: false,
    title: "Lobby private",
    desc: "Crea una stanza o entra con codice. Pensata per giocare con amici e test privati.",
    meta: ["Codice lobby", "Inviti", "Custom room"]
  }
];

function inside(x,y,r){ return r && x>=r.x && x<=r.x+r.w && y>=r.y && y<=r.y+r.h; }

function panel(r,x,y,w,h,opts={}){
  const ctx=r.ctx;
  const radius=opts.radius ?? 24;
  ctx.save();
  ctx.shadowColor=opts.shadow || "rgba(0,0,0,.42)";
  ctx.shadowBlur=opts.blur ?? 22;
  ctx.shadowOffsetY=opts.offsetY ?? 8;
  r.roundRect(x,y,w,h,radius,opts.fill || "rgba(5,8,18,.66)",opts.stroke || "rgba(255,255,255,.10)",opts.lineWidth ?? 1.2);
  ctx.restore();

  const g=ctx.createLinearGradient(x,y,x,y+h);
  g.addColorStop(0,"rgba(255,255,255,.070)");
  g.addColorStop(.45,"rgba(255,255,255,.018)");
  g.addColorStop(1,"rgba(0,0,0,.12)");
  ctx.save();
  ctx.beginPath();
  ctx.roundRect(x,y,w,h,radius);
  ctx.clip();
  ctx.fillStyle=g;
  ctx.fillRect(x,y,w,h);
  ctx.restore();
}

function glowText(r,text,x,y,opts={}){
  const ctx=r.ctx;
  ctx.save();
  if(opts.glow){
    ctx.shadowColor=opts.glow;
    ctx.shadowBlur=opts.glowBlur ?? 14;
  }
  r.text(text,x,y,opts);
  ctx.restore();
}

function navButton(r,rect,label,icon,active=false){
  panel(r,rect.x,rect.y,rect.w,rect.h,{radius:15,fill:active?"rgba(255,202,58,.16)":"rgba(6,9,20,.76)",stroke:active?"rgba(255,202,58,.55)":"rgba(255,255,255,.10)",blur:active?12:7,offsetY:2});
  r.text(icon,rect.x+24,rect.y+rect.h/2,{align:"center",baseline:"middle",size:18,weight:950,color:active?T.gold:"#e9f8ff"});
  r.text(label,rect.x+50,rect.y+rect.h/2,{baseline:"middle",size:11.4,weight:950,color:active?T.gold:"#f8f1df"});
}

function drawPlayButton(r, rect, label, enabled=true){
  const ctx=r.ctx;
  ctx.save();
  ctx.shadowColor=enabled ? "rgba(255,202,58,.72)" : "rgba(0,0,0,.35)";
  ctx.shadowBlur=enabled ? 28 : 8;
  ctx.shadowOffsetY=enabled ? 5 : 2;
  const g=ctx.createLinearGradient(rect.x,rect.y,rect.x,rect.y+rect.h);
  if(enabled){
    g.addColorStop(0,"#fff2a5");
    g.addColorStop(.42,"#ffd23f");
    g.addColorStop(1,"#c98912");
  }else{
    g.addColorStop(0,"rgba(110,112,124,.54)");
    g.addColorStop(1,"rgba(52,54,64,.54)");
  }
  r.roundRect(rect.x,rect.y,rect.w,rect.h,24,g,enabled?"rgba(255,246,214,.88)":"rgba(255,255,255,.14)",2.3);
  ctx.restore();

  ctx.save();
  ctx.beginPath();
  ctx.roundRect(rect.x+4,rect.y+4,rect.w-8,Math.max(10,rect.h*.36),20);
  ctx.clip();
  ctx.fillStyle=enabled ? "rgba(255,255,255,.32)" : "rgba(255,255,255,.08)";
  ctx.fillRect(rect.x,rect.y,rect.w,rect.h);
  ctx.restore();

  r.text(label,rect.x+rect.w/2,rect.y+rect.h/2+1,{align:"center",baseline:"middle",size:22,weight:950,color:enabled?"#201000":"rgba(255,255,255,.44)"});
}

function modeCard(r,mode,rect,selected){
  const enabled=mode.enabled;
  const accent = selected ? T.gold : enabled ? "#4cc9f0" : "rgba(255,255,255,.22)";
  panel(r,rect.x,rect.y,rect.w,rect.h,{
    radius:18,
    fill:selected ? "rgba(255,202,58,.13)" : enabled ? "rgba(9,18,35,.75)" : "rgba(8,10,18,.52)",
    stroke:selected ? "rgba(255,202,58,.55)" : enabled ? "rgba(76,201,240,.28)" : "rgba(255,255,255,.08)",
    blur:selected?18:10,
    offsetY:3
  });
  r.text(mode.icon,rect.x+26,rect.y+31,{align:"center",baseline:"middle",size:24});
  r.text(mode.short.toUpperCase(),rect.x+54,rect.y+17,{size:13,weight:950,color:enabled?"#fff":"rgba(255,255,255,.46)"});
  r.text(mode.status,rect.x+54,rect.y+41,{size:8.5,weight:950,color:enabled?accent:"rgba(255,255,255,.34)"});
  if(selected){
    r.roundRect(rect.x+rect.w-17,rect.y+14,8,rect.h-28,4,T.gold);
  }
}

function smallPill(r,x,y,w,label,color=T.gold){
  r.roundRect(x,y,w,24,12,"rgba(0,0,0,.36)",`${color}55`,1);
  r.text(label,x+w/2,y+12,{align:"center",baseline:"middle",size:10,weight:950,color});
}

export class HomeScene {
  constructor(app){
    this.app=app;
    this.selectedMode="bots";
    this.rects={ modes:[], play:null, settings:null, account:null, createLobby:null, joinLobby:null };
  }

  currentMode(){ return MODES.find(m=>m.id===this.selectedMode) || MODES[2]; }

  startSelectedMode(){
    const mode=this.currentMode();
    if(!mode.enabled){
      this.toast = { text:`${mode.label} non è ancora disponibile`, life:1.8 };
      this.app.audio?.beep?.(180,.05,"sawtooth");
      return;
    }
    this.app.state.selectedGameMode = mode.id;
    this.app.state.beginHeroDraft(this.app.rng);
    this.app.audio?.beep?.(560,.07,"triangle");
    this.app.scenes.set(HeroSelectScene);
  }

  handleInput(events){
    for(const ev of events){
      if(ev.type!=="up") continue;
      const {x,y}=ev;
      for(const item of this.rects.modes||[]){
        if(inside(x,y,item.rect)){
          this.selectedMode=item.mode.id;
          this.app.audio?.beep?.(360,.04,"triangle");
          return;
        }
      }
      if(inside(x,y,this.rects.play)){ this.startSelectedMode(); return; }
      if(inside(x,y,this.rects.settings)){
        this.toast={text:"Opzioni gioco: prossimamente",life:1.6};
        this.app.audio?.beep?.(260,.04,"triangle");
        return;
      }
      if(inside(x,y,this.rects.account)){
        this.toast={text:"Opzioni account: prossimamente",life:1.6};
        this.app.audio?.beep?.(260,.04,"triangle");
        return;
      }
      if(inside(x,y,this.rects.createLobby) || inside(x,y,this.rects.joinLobby)){
        this.toast={text:"Lobby private: prossimamente",life:1.6};
        this.app.audio?.beep?.(220,.04,"triangle");
        return;
      }
    }
  }

  update(dt){
    if(this.toast){
      this.toast.life-=dt;
      if(this.toast.life<=0) this.toast=null;
    }
  }

  drawTopBar(r){
    const p=this.app.state.profile || {};
    panel(r,24,18,1318,66,{radius:20,fill:"rgba(4,7,18,.72)",stroke:"rgba(255,255,255,.10)",blur:10,offsetY:2});
    r.roundRect(42,30,44,44,14,"rgba(255,202,58,.16)","rgba(255,202,58,.38)",1.4);
    r.text("O",64,52,{align:"center",baseline:"middle",size:21,weight:950,color:T.gold});
    r.text("Oliver",100,38,{size:15,weight:950,color:"#fff"});
    r.text(`Lv. ${p.level || 12} · Silver II`,100,60,{size:11,weight:800,color:"#b8adc9"});

    r.text(RUNTIME.title || "Hero Smash",683,42,{align:"center",size:22,weight:950,color:"#fff",shadow:true});
    r.text("PLAYER HUB",683,62,{align:"center",size:10,weight:950,color:T.gold});

    smallPill(r,1050,38,92,`🪙 ${p.totalCoins ?? 1145}`,T.gold);
    smallPill(r,1152,38,72,"💎 80","#7fd2ff");

    this.rects.account={x:1236,y:31,w:42,h:40};
    this.rects.settings={x:1286,y:31,w:42,h:40};
    r.roundRect(this.rects.account.x,this.rects.account.y,this.rects.account.w,this.rects.account.h,14,"rgba(255,255,255,.07)","rgba(255,255,255,.12)");
    r.roundRect(this.rects.settings.x,this.rects.settings.y,this.rects.settings.w,this.rects.settings.h,14,"rgba(255,255,255,.07)","rgba(255,255,255,.12)");
    r.text("👤",1257,51,{align:"center",baseline:"middle",size:17});
    r.text("⚙",1307,51,{align:"center",baseline:"middle",size:17});
  }

  drawLeftPanel(r){
    panel(r,34,104,260,548,{radius:24,fill:"rgba(4,7,18,.64)",stroke:"rgba(76,201,240,.18)"});
    r.text("MISSIONI",64,134,{size:14,weight:950,color:T.gold});
    const missions=[
      ["Compra 3 carte", "0/3"],
      ["Vinci 1 round", "0/1"],
      ["Gioca una partita", "0/1"]
    ];
    missions.forEach(([name,val],i)=>{
      const y=158+i*64;
      r.roundRect(58,y,212,48,14,"rgba(255,255,255,.055)","rgba(255,255,255,.08)");
      r.text(name,74,y+17,{size:11.5,weight:850,color:"#fff"});
      r.text(val,252,y+17,{align:"right",size:11,weight:950,color:T.gold});
      r.roundRect(74,y+33,166,5,3,"rgba(0,0,0,.40)");
      r.roundRect(74,y+33,i===2?40:10,5,3,"rgba(255,202,58,.70)");
    });

    r.text("RAPIDI",64,386,{size:14,weight:950,color:"#7fd2ff"});
    const btns=[
      ["PASS","🎫"],
      ["SHOP","🛒"],
      ["EVENTI","✦"]
    ];
    btns.forEach(([label,ic],i)=>{
      navButton(r,{x:58,y:412+i*58,w:212,h:44},label,ic,false);
    });
  }

  drawRightPanel(r){
    const mode=this.currentMode();
    panel(r,1072,104,260,548,{radius:24,fill:"rgba(3,6,16,.78)",stroke:"rgba(255,202,58,.18)",blur:18,offsetY:5});
    r.text("STAGIONE",1102,134,{size:14,weight:950,color:T.gold});
    r.text("Season 1",1102,166,{size:24,weight:950,color:"#fff"});
    r.text("Reset tra 12 giorni",1102,190,{size:12,weight:800,color:"#b8adc9"});

    r.roundRect(1102,222,200,92,18,"rgba(255,202,58,.10)","rgba(255,202,58,.28)");
    r.text("LEGA",1124,244,{size:11,weight:950,color:T.gold});
    r.text("Silver II",1124,271,{size:23,weight:950,color:"#fff"});
    r.text("+23 alla prossima divisione",1124,294,{size:10.5,weight:850,color:"#b8adc9"});
    r.roundRect(1124,302,152,5,3,"rgba(0,0,0,.36)");
    r.roundRect(1124,302,84,5,3,"rgba(255,202,58,.70)");

    r.text("MODALITÀ",1102,358,{size:13,weight:950,color:"#7fd2ff"});
    r.roundRect(1102,378,200,104,18,"rgba(76,201,240,.09)","rgba(76,201,240,.24)");
    r.text(mode.icon,1128,410,{align:"center",baseline:"middle",size:22});
    r.text(mode.label,1158,399,{size:12,weight:950,color:"#fff"});
    r.wrap(mode.desc,1158,421,124,16,{size:10.2,weight:750,color:"#b8adc9"});

    r.text("SOCIAL",1102,526,{size:13,weight:950,color:"#c77dff"});
    r.roundRect(1102,546,200,44,16,"rgba(199,125,255,.08)","rgba(199,125,255,.18)");
    r.text("Amici / Clan: prossimamente",1120,572,{size:11,weight:850,color:"#d8cfe8"});
  }

  drawCenter(r){
    const mode=this.currentMode();

    panel(r,326,112,714,500,{radius:34,fill:"rgba(3,6,16,.80)",stroke:mode.enabled?"rgba(76,201,240,.35)":"rgba(255,255,255,.13)",blur:32,offsetY:10});

    r.text("SELEZIONA MODALITÀ",683,150,{align:"center",size:13,weight:950,color:T.gold});
    this.rects.modes=[];
    const startX=386, y=174, w=136, h=66, gap=18;
    MODES.forEach((m,i)=>{
      const rect={x:startX+i*(w+gap),y,w,h};
      this.rects.modes.push({mode:m,rect});
      modeCard(r,m,rect,m.id===mode.id);
    });

    r.roundRect(404,272,558,206,30,"rgba(3,7,18,.74)","rgba(255,255,255,.10)",1.2);
    r.roundRect(430,297,72,72,22,"rgba(76,201,240,.10)",mode.enabled?"rgba(76,201,240,.32)":"rgba(255,255,255,.10)");
    glowText(r,mode.icon,466,333,{align:"center",baseline:"middle",size:42,glow:mode.enabled?"#4cc9f0":"#777",glowBlur:18});
    r.text(mode.title.toUpperCase(),526,314,{size:25,weight:950,color:mode.enabled?"#fff":"rgba(255,255,255,.55)",shadow:true});
    r.wrap(mode.desc,526,352,384,22,{size:15,weight:760,color:"#d8cfe8"});

    mode.meta.forEach((m,i)=>smallPill(r,526+i*126,430,112,m,mode.enabled?"#4cc9f0":"#8a8198"));

    if(mode.id==="private"){
      this.rects.createLobby={x:486,y:504,w:180,h:46};
      this.rects.joinLobby={x:700,y:504,w:180,h:46};
      navButton(r,this.rects.createLobby,"CREA LOBBY","+",false);
      navButton(r,this.rects.joinLobby,"ENTRA CODICE","#",false);
      this.rects.play=null;
    } else {
      this.rects.createLobby=null;
      this.rects.joinLobby=null;
      this.rects.play={x:514,y:508,w:338,h:68};
      const enabled=mode.enabled;
      drawPlayButton(r,this.rects.play,enabled?"GIOCA":"PROSSIMAMENTE",enabled);
    }
  }

  drawBottomNav(r){
    panel(r,330,682,706,50,{radius:18,fill:"rgba(3,6,16,.78)",stroke:"rgba(255,255,255,.10)",blur:10,offsetY:2});
    const nav=[
      ["HOME","⌂",true],
      ["COLLECTION","▱",false],
      ["LEAGUE","🏆",false],
      ["SHOP","🛒",false],
      ["SOCIAL","☰",false]
    ];
    nav.forEach(([label,ic,active],i)=>{
      navButton(r,{x:348+i*136,y:689,w:116,h:36},label,ic,active);
    });
  }

  drawToast(r){
    if(!this.toast) return;
    const x=483,y=620,w=400,h=36;
    r.roundRect(x,y,w,h,14,"rgba(0,0,0,.80)","rgba(255,202,58,.36)");
    r.text(this.toast.text,x+w/2,y+h/2,{align:"center",baseline:"middle",size:13,weight:950,color:"#fff"});
  }

  draw(r){
    drawSceneArt(r, this.app.assets.get("final_home_keyart") || this.app.assets.get("final_market_bg"), {
      alpha:.38,
      overlayTop:"rgba(3,5,14,.58)",
      overlayBottom:"rgba(2,3,9,.96)"
    });

    const ctx=r.ctx;
    ctx.save();
    ctx.fillStyle="rgba(0,0,0,.34)";
    ctx.fillRect(0,0,1366,768);
    const bg=ctx.createRadialGradient(683,360,80,683,390,650);
    bg.addColorStop(0,"rgba(76,201,240,.12)");
    bg.addColorStop(.38,"rgba(3,7,18,.44)");
    bg.addColorStop(1,"rgba(0,0,0,.72)");
    ctx.fillStyle=bg; ctx.fillRect(0,0,1366,768);
    ctx.restore();

    this.drawTopBar(r);
    this.drawLeftPanel(r);
    this.drawRightPanel(r);
    this.drawCenter(r);
    this.drawBottomNav(r);
    this.drawToast(r);

    r.text(RUNTIME.footer || "Hero Smash",683,754,{align:"center",size:10,color:"rgba(255,255,255,.26)",weight:800});
  }
}
