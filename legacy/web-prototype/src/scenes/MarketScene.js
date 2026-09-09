import { CardSystem } from "../game/CardSystem.js";
import { BRANCHES } from "../game/GameData.js";
import { BranchSystem } from "../game/BranchSystem.js";
import { ECONOMY } from "../game/GameState.js";
import { CombatScene } from "./CombatScene.js";
import { LeagueSystem } from "../game/LeagueSystem.js";
import { drawSceneArt } from "../ui/ArtScene.js";
import { FighterTheme, drawBeveledPanel, fitText } from "../ui/fighter/FighterTheme.js";
import { loadArena } from "../arena/ArenaLoader.js";
import { ParallaxArena } from "../arena/ParallaxArena.js";
import { pointInRect } from "../ui/fighter/OverlayUI.js";

// ─── Layout ────────────────────────────────────────────────────────────────
const LEFT  = { x:48,  y:118, w:214, h:558 };
const RIGHT = { x:1134, y:118, w:194, h:558 };
const CARD_W=176, CARD_H=346, CARD_GAP=24;
const CARDS_TOTAL_W = 3*CARD_W + 2*CARD_GAP;
const CARDS_X = 300 + (766 - CARDS_TOTAL_W) / 2;
const CARDS_Y = 188;
const BAR_Y=692, BAR_H=52;

// ─── Palette shortcuts ─────────────────────────────────────────────────────
const T = FighterTheme.colors;

function clamp(v,a,b){ return Math.max(a,Math.min(b,v)); }

function rarityColor(card){
  return FighterTheme.rarity[card?.rarity] || card?.frame || T.gold;
}

function branchMeta(card){
  const id = card?.branches?.[0] || card?.branch || "power";
  return BRANCHES.find(b=>b.id===id) || BRANCHES[0] || {icon:"◆",color:T.gold,name:"Branch"};
}

function wrapTextLines(text, cpl){
  const words = String(text||"").split(" ");
  const lines=[]; let cur="";
  for(const w of words){
    if((cur+" "+w).trim().length>cpl){ if(cur)lines.push(cur.trim()); cur=w; }
    else cur=(cur+" "+w).trim();
  }
  if(cur)lines.push(cur.trim());
  return lines;
}

function shortEffect(t){
  return String(t||"").replace(/\s+/g," ").replace(/For every/g,"Every").replace(/Has /g,"").trim();
}

function cardLevel(state, card){
  return state?.cardLevels?.[card?.id] || 0;
}

function cardOwnedThisRound(state, card, boughtThisRound){
  return !!card && (boughtThisRound?.has?.(card.id) || cardLevel(state, card) >= (card.max || 1));
}

function cardAffordable(state, card){
  return !!card && (state?.gold || 0) >= (card.cost || 0);
}

function formatBranchNames(card){
  return (card?.branches || [])
    .map(id => {
      const b = BRANCHES.find(x => x.id === id);
      return b ? `${b.icon || "◆"} ${b.name}` : id;
    })
    .join("  ");
}

function effectEntries(card){
  const effects = card?.effects || {};
  return Object.entries(effects)
    .filter(([_, v]) => v !== undefined && v !== null && v !== false && v !== 0)
    .map(([k, v]) => {
      const label = String(k)
        .replace(/([A-Z])/g, " $1")
        .replace(/^./, c => c.toUpperCase());
      return `${label}: ${typeof v === "number" ? Number(v.toFixed?.(2) ?? v) : v}`;
    });
}

function missingGold(state, cost){
  return Math.max(0, (cost || 0) - (state?.gold || 0));
}

function buttonFill(disabled, active, base="rgba(10,12,22,.86)", activeFill="rgba(55,18,68,.90)"){
  if(disabled) return "rgba(18,19,27,.55)";
  return active ? activeFill : base;
}

function buttonTextColor(disabled, active=false){
  if(disabled) return "rgba(255,255,255,.36)";
  return active ? "#f1d6ff" : "#f8f1df";
}

function getUiAsset(assets, key){
  return assets?.images?.get?.(key) || null;
}

function drawUiAsset(r, img, x, y, w, h, opts={}){
  if(!img) return false;
  const ctx=r.ctx;
  ctx.save();
  if(opts.alpha!==undefined) ctx.globalAlpha=opts.alpha;
  if(opts.filter) ctx.filter=opts.filter;
  if(opts.shadowColor){
    ctx.shadowColor=opts.shadowColor;
    ctx.shadowBlur=opts.shadowBlur ?? 16;
  }
  if(opts.blend) ctx.globalCompositeOperation=opts.blend;
  ctx.drawImage(img, x, y, w, h);
  ctx.restore();
  return true;
}

function drawAssetButton(r, rect, assets, key, opts={}){
  const img = getUiAsset(assets, key);
  if(img){
    drawUiAsset(r, img, rect.x, rect.y, rect.w, rect.h, {
      filter: opts.disabled ? "grayscale(1) brightness(.62)" : (opts.filter || "none"),
      alpha: opts.disabled ? 0.72 : (opts.alpha ?? 1),
      shadowColor: opts.disabled ? null : (opts.glow || "rgba(255,202,58,.36)"),
      shadowBlur: opts.glowBlur ?? (opts.active ? 18 : 12)
    });
    if(opts.sub){
      const pillW = Math.min(rect.w * 0.54, 102);
      const pillH = 16;
      const pillX = rect.x + (rect.w - pillW) / 2;
      const pillY = rect.y + rect.h - pillH - 5;
      r.roundRect(pillX,pillY,pillW,pillH,8,"rgba(4,8,18,.82)","rgba(255,255,255,.16)");
      r.text(opts.sub,pillX+pillW/2,pillY+pillH/2,{align:"center",baseline:"middle",size:8.4,weight:950,color:opts.subColor||"#fff4d8"});
    }
    if(opts.badge){
      const bx=rect.x+rect.w-22, by=rect.y+8;
      r.roundRect(bx,by,18,16,8,"rgba(5,8,18,.84)","rgba(255,255,255,.18)");
      r.text(opts.badge,bx+9,by+8,{align:"center",baseline:"middle",size:8,weight:950,color:"#fff"});
    }
    return;
  }
  drawActionButton(r, rect, opts);
}

function drawActionButton(r, rect, opts={}){
  const ctx=r.ctx;
  const disabled=!!opts.disabled;
  const active=!!opts.active;
  const accent=disabled ? "rgba(255,255,255,.12)" : (opts.accent || "rgba(255,202,58,.55)");
  const fill=buttonFill(disabled, active, opts.fill, opts.activeFill);
  ctx.save();
  if(!disabled){
    ctx.shadowColor=opts.glow || accent;
    ctx.shadowBlur=opts.glowBlur ?? (active ? 14 : 8);
  }
  drawGlassPanel(r,rect.x,rect.y,rect.w,rect.h,{
    cut:14, fill, accent, lineWidth:active ? 2.2 : 1.8
  });
  ctx.restore();
  drawCornerOrnaments(ctx,rect.x,rect.y,rect.w,rect.h,disabled ? "#555" : (opts.corner || T.gold),7);

  r.text(opts.label || "ACTION", rect.x+rect.w/2, rect.y+18,{
    align:"center",size:12.2,weight:950,color:buttonTextColor(disabled, active)
  });
  if(opts.sub){
    r.text(opts.sub, rect.x+rect.w/2, rect.y+37,{
      align:"center",size:9.4,weight:850,color:disabled ? "rgba(255,255,255,.30)" : (opts.subColor || T.gold)
    });
  }
  if(opts.badge){
    r.roundRect(rect.x+rect.w-28,rect.y+5,21,17,8,"rgba(0,0,0,.55)",accent);
    r.text(opts.badge,rect.x+rect.w-17.5,rect.y+13.5,{align:"center",baseline:"middle",size:9,weight:950,color:"#fff"});
  }
}

function formatCostStatus(state, cost, label="🪙"){
  const miss=missingGold(state,cost);
  return miss>0 ? `-${miss} ${label}` : `${label} ${cost}`;
}

// ═══════════════════════════════════════════════════════════════════════════
// VISUAL PRIMITIVES
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Glassmorphism panel — frosted dark glass with inner light edge + grain.
 */
function drawGlassPanel(r, x, y, w, h, opts={}){
  const ctx=r.ctx, cut=opts.cut??18;
  const accentColor = opts.accent ?? "rgba(255,202,58,.32)";

  ctx.save();

  // 1. Drop shadow for depth
  ctx.shadowColor = "rgba(0,0,0,.55)";
  ctx.shadowBlur  = 22;
  ctx.shadowOffsetY = 6;

  // 2. Panel body — clip to beveled shape
  const p = new Path2D();
  p.moveTo(x+cut,y); p.lineTo(x+w-cut,y); p.lineTo(x+w,y+cut);
  p.lineTo(x+w,y+h-cut); p.lineTo(x+w-cut,y+h);
  p.lineTo(x+cut,y+h); p.lineTo(x,y+h-cut); p.lineTo(x,y+cut); p.closePath();

  ctx.fillStyle = opts.fill ?? "rgba(5,8,18,.72)";
  ctx.fill(p);
  ctx.shadowColor="transparent";

  // 3. Subtle inner vignette (replaces expensive scanline grain)
  ctx.save();
  ctx.clip(p);
  const innerV=ctx.createRadialGradient(x+w/2,y+h*.3,0,x+w/2,y+h*.3,Math.max(w,h)*.7);
  innerV.addColorStop(0,"rgba(255,255,255,.04)");
  innerV.addColorStop(1,"rgba(0,0,0,.14)");
  ctx.fillStyle=innerV; ctx.fillRect(x,y,w,h);
  ctx.restore();

  // 4. Inner top-edge highlight (light refraction)
  ctx.save();
  ctx.clip(p);
  const topLight = ctx.createLinearGradient(x,y,x,y+h*0.42);
  topLight.addColorStop(0, "rgba(255,255,255,.09)");
  topLight.addColorStop(.5, "rgba(255,255,255,.025)");
  topLight.addColorStop(1, "rgba(255,255,255,0)");
  ctx.fillStyle = topLight;
  ctx.fillRect(x,y,w,h);
  ctx.restore();

  // 5. Border — glow + solid line
  ctx.save();
  ctx.shadowColor = accentColor.replace(/[\d.]+\)$/,"0.6)");
  ctx.shadowBlur = 8;
  ctx.strokeStyle = accentColor;
  ctx.lineWidth = opts.lineWidth ?? 1.6;
  ctx.stroke(p);
  ctx.restore();

  ctx.restore();
}

/**
 * Glowing text with inner bloom.
 */
function glowText(r, text, x, y, opts={}){
  const ctx=r.ctx;
  ctx.save();
  if(opts.glow){
    ctx.shadowColor = opts.glow;
    ctx.shadowBlur  = opts.glowBlur ?? 14;
  }
  r.text(text, x, y, opts);
  ctx.restore();
}

/**
 * Radial vignette + dark overlay when market open.
 */
function drawVignette(r, intensity=.52){
  const ctx=r.ctx;
  ctx.save();
  ctx.fillStyle=`rgba(3,5,12,${intensity})`;
  ctx.fillRect(0,0,1366,768);
  const rad=ctx.createRadialGradient(683,365,80,683,365,630);
  rad.addColorStop(0,"rgba(0,0,0,0)");
  rad.addColorStop(.5,"rgba(0,0,0,.06)");
  rad.addColorStop(1,"rgba(0,0,0,.48)");
  ctx.fillStyle=rad;
  ctx.fillRect(0,0,1366,768);
  ctx.restore();
}

/**
 * Decorative corner ornament — two lines meeting at corner with a diamond dot.
 */
function drawCorner(ctx, x, y, dx, dy, color, size=14){
  ctx.save();
  ctx.strokeStyle=color;
  ctx.lineWidth=1.8;
  ctx.globalAlpha=0.85;
  ctx.beginPath();
  ctx.moveTo(x+dx*size,y); ctx.lineTo(x,y); ctx.lineTo(x,y+dy*size);
  ctx.stroke();
  ctx.fillStyle=color;
  ctx.beginPath();
  ctx.arc(x,y,2.8,0,Math.PI*2);
  ctx.fill();
  ctx.restore();
}

/**
 * All four corners of a rect.
 */
function drawCornerOrnaments(ctx, x, y, w, h, color, size=14){
  drawCorner(ctx, x+4,   y+4,   1,  1, color, size);
  drawCorner(ctx, x+w-4, y+4,  -1,  1, color, size);
  drawCorner(ctx, x+4,   y+h-4, 1, -1, color, size);
  drawCorner(ctx, x+w-4, y+h-4,-1, -1, color, size);
}

/**
 * Animated pulse ring (uses a passed-in phase 0→1 for breathing effect).
 */
function drawPulseRing(ctx, cx, cy, radius, color, phase=0){
  const alpha = 0.28 + 0.18 * Math.sin(phase * Math.PI * 2);
  const r     = radius + 4 * Math.sin(phase * Math.PI * 2);
  ctx.save();
  ctx.strokeStyle = color;
  ctx.lineWidth   = 2;
  ctx.globalAlpha = alpha;
  ctx.shadowColor = color;
  ctx.shadowBlur  = 10;
  ctx.beginPath();
  ctx.arc(cx, cy, r, 0, Math.PI*2);
  ctx.stroke();
  ctx.restore();
}

// ═══════════════════════════════════════════════════════════════════════════
// TIMER
// ═══════════════════════════════════════════════════════════════════════════

function drawMarketTimer(r, round, timeLeft, phase=0, assets=null, state=null){
  const x=563, y=0, w=240, h=132;
  const ctx=r.ctx;
  const urgent = timeLeft < 10;
  const img = getUiAsset(assets, "ui_market_top_round_badge");

  if(img){
    drawUiAsset(r, img, x, y, w, h, {
      shadowColor: urgent ? "rgba(239,35,60,.55)" : "rgba(51,196,255,.34)",
      shadowBlur: urgent ? 20 : 14,
      filter: urgent ? "saturate(1.1) brightness(1.04)" : "none"
    });
    r.roundRect(x+48,y+20,w-96,h-52,16,"rgba(3,7,16,.62)");
  } else {
    if(urgent){
      ctx.save();
      ctx.strokeStyle="#ef233c";
      ctx.lineWidth=3;
      ctx.globalAlpha = 0.4 + 0.3*Math.sin(phase*Math.PI*8);
      ctx.shadowColor="#ef233c";
      ctx.shadowBlur=20;
      drawBeveledPanel(r, x-3, y-3, w+6, h+6, {
        cut:25, fill:"transparent", stroke:"rgba(239,35,60,.60)", lineWidth:3
      });
      ctx.restore();
    }
    drawGlassPanel(r, x+32, y+6, w-64, h-26, {
      cut:22, fill:"rgba(8,11,20,.82)",
      accent: urgent ? "rgba(239,35,60,.72)" : "rgba(255,202,58,.70)",
      lineWidth:2.2
    });
  }

  glowText(r, `ROUND ${round}`, x+w/2, y+34, {
    align:"center", size:13.2, weight:950, color:T.ivory,
    glow: urgent ? "#ef233c" : "#4cc9f0", glowBlur:8
  });
  glowText(r, String(Math.ceil(Math.max(0,timeLeft))), x+w/2, y+74, {
    align:"center", baseline:"middle", size:44, weight:950,
    color: urgent?"#ff5d73":"#ffffff",
    glow: urgent?"#ef233c":"#4cc9f0", glowBlur:18
  });

  // Small gold counter under timer
  const gx = x + 72, gy = y + 92, gw = w - 144, gh = 24;
  const gimg = getUiAsset(assets, "ui_market_gold_panel");
  if(gimg){
    drawUiAsset(r, gimg, gx, gy, gw, gh, {
      shadowColor: "rgba(255,202,58,.24)", shadowBlur: 8
    });
  } else {
    r.roundRect(gx,gy,gw,gh,10,"rgba(18,14,5,.92)","rgba(255,202,58,.52)",1.2);
  }
  r.roundRect(gx+10,gy+5,gw-20,gh-10,8,"rgba(0,0,0,.28)");
  glowText(r, `🪙 ${state?.gold ?? 0}`, gx+gw/2, gy+gh/2, {
    align:"center", baseline:"middle", size:12, weight:950,
    color:T.gold, glow:T.gold, glowBlur:8
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// LEADERBOARD
// ═══════════════════════════════════════════════════════════════════════════

function drawLeaderboard(r, players, state, assets=null){
  const {x,y,w,h}=LEFT;
  const panelImg = getUiAsset(assets, "ui_market_left_standings_panel");
  if(panelImg){
    drawUiAsset(r, panelImg, x-8, y-24, w+28, h+58, { shadowColor:"rgba(31,124,255,.22)", shadowBlur:14 });
  } else {
    drawGlassPanel(r, x, y, w, h, {
      accent:"rgba(255,202,58,.28)", fill:"rgba(4,7,16,.54)"
    });
    drawCornerOrnaments(r.ctx, x, y, w, h, T.gold, 14);
  }

  glowText(r,"CLASSIFICA",x+w/2,y+22,{ align:"center",size:12,weight:950,color:T.ivory,glow:T.gold,glowBlur:10 });
  r.ctx.save();
  r.ctx.strokeStyle="rgba(255,202,58,.18)";
  r.ctx.lineWidth=1;
  r.ctx.beginPath(); r.ctx.moveTo(x+18,y+35); r.ctx.lineTo(x+w-18,y+35); r.ctx.stroke();
  r.ctx.restore();

  const maxHp = state.startingLife||100;
  const list=[...(players||[])].sort((a,b)=>(b.life||0)-(a.life||0)).slice(0,8);

  list.forEach((p,i)=>{
    const rowY=y+44+i*60;
    const isYou=p.id==="you";
    const alive=!p.eliminated&&(p.life||0)>0;
    const hp=p.life||0;
    const pct=clamp(hp/maxHp,0,1);
    const hpCol=pct>.55?"#06d6a0":pct>.25?"#ffca3a":"#ef233c";
    const ctx=r.ctx;
    ctx.save();
    ctx.shadowColor = isYou ? "rgba(255,202,58,.28)" : "transparent";
    ctx.shadowBlur  = isYou ? 10 : 0;
    r.roundRect(x+10, rowY, w-20, 52, 12,
      isYou?"rgba(255,202,58,.12)":"rgba(255,255,255,.035)",
      isYou?"rgba(255,202,58,.26)":"rgba(255,255,255,.05)");
    ctx.restore();
    r.roundRect(x+16,rowY+12,24,24,8, isYou?"#ffca3a":"rgba(255,255,255,.12)");
    r.text(i+1,x+28,rowY+24,{ align:"center",baseline:"middle",size:12,weight:950, color:isYou?"#1a0d00":"#f6e6b8" });
    r.ctx.save(); r.ctx.shadowColor=p.hero?.color||"#666"; r.ctx.shadowBlur=alive?10:0;
    r.ctx.beginPath(); r.ctx.arc(x+57,rowY+26,18,0,Math.PI*2); r.ctx.fillStyle=p.hero?.color||"#252b3b"; r.ctx.fill();
    r.ctx.strokeStyle=alive?"rgba(255,202,58,.38)":"rgba(255,255,255,.12)"; r.ctx.lineWidth=2; r.ctx.stroke(); r.ctx.restore();
    r.text(p.hero?.icon||"◆",x+57,rowY+26,{ align:"center",baseline:"middle",size:14,weight:950 });
    r.text(fitText(p.name||"Bot",11),x+82,rowY+11,{ size:10.5,weight:950,color:alive?"#fff":"#666" });
    r.text(`🪙 ${p.gold??0}`,x+82,rowY+28,{size:9,weight:800,color:T.gold});
    r.text(`🏆 ${p.stats?.wins??p.wins??0}`,x+136,rowY+28,{size:9,weight:800,color:"#cfc4dd"});
    r.ctx.save(); r.ctx.shadowColor=hpCol; r.ctx.shadowBlur=4;
    r.roundRect(x+82,rowY+42,w-106,4,2,"rgba(0,0,0,.52)");
    if(pct>0) r.roundRect(x+82,rowY+42,Math.max(4,(w-106)*pct),4,2,hpCol);
    r.ctx.restore();
    r.text(alive?String(hp):"KO",x+w-14,rowY+12,{ align:"right",size:14,weight:950,color:alive?hpCol:"#666" });
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// RIGHT SIDE PANELS
// ═══════════════════════════════════════════════════════════════════════════

function drawBannedBranches(r, allBranches, activeIds, _bnAssets=null){
  const x=RIGHT.x, y=RIGHT.y, w=RIGHT.w, h=88;
  drawGlassPanel(r,x,y,w,h,{
    fill:"rgba(20,5,8,.52)", accent:"rgba(239,35,60,.38)", cut:14
  });
  drawCornerOrnaments(r.ctx,x,y,w,h,"#ef476f",10);
  glowText(r,"RAMI BANNATI",x+w/2,y+17,{
    align:"center",size:11,weight:950,color:"#ff5c6c",glow:"#ef233c",glowBlur:10
  });

  const banned=(allBranches||[]).filter(b=>!activeIds.includes(b.id)).slice(0,4);
  banned.forEach((b,i)=>{
    const col=i%2, row=Math.floor(i/2);
    const bx=x+12+col*84, by=y+35+row*26;
    r.ctx.save();
    r.ctx.shadowColor="rgba(239,35,60,.4)"; r.ctx.shadowBlur=6;
    r.roundRect(bx,by,78,20,8,"rgba(239,35,60,.14)","rgba(239,35,60,.30)");
    r.ctx.restore();
    const _bimg=_bnAssets?.images?.get?.(`branch_${b.id}`);
    if(_bimg){
      r.ctx.save(); r.ctx.globalCompositeOperation="screen";
      r.ctx.drawImage(_bimg,bx+4,by+2,16,16); r.ctx.restore();
      r.text(fitText(b.name,7),bx+24,by+10,{size:9,weight:900,color:"#ffc0c7"});
    } else {
      r.text(`${b.icon} ${fitText(b.name,7)}`,bx+39,by+10,{
        align:"center",baseline:"middle",size:9.2,weight:900,color:"#ffc0c7"
      });
    }
  });
  if(!banned.length)
    r.text("Tutti attivi",x+w/2,y+58,{align:"center",size:10,color:"rgba(255,255,255,.35)"});
}

function drawBranchReport(r, branches, assets=null){
  const x=RIGHT.x, y=RIGHT.y+102, w=RIGHT.w, h=324;
  const panelImg = getUiAsset(assets, "ui_market_right_traits_panel");
  if(panelImg) drawUiAsset(r, panelImg, x-10, y-12, w+22, h+28, { shadowColor:"rgba(0,255,170,.16)", shadowBlur:12 });
  else {
    drawGlassPanel(r,x,y,w,h,{ fill:"rgba(4,7,14,.52)", accent:"rgba(255,202,58,.28)", cut:14 });
    drawCornerOrnaments(r.ctx,x,y,w,h,T.gold,10);
  }
  glowText(r,"RAMI ATTIVI",x+w/2,y+19,{ align:"center",size:11,weight:950,color:T.ivory,glow:T.gold,glowBlur:8 });
  branches.slice(0,8).forEach((b,i)=>{
    const rowY=y+42+i*33;
    const pts=b.points||0, next=b.next||40;
    const pct=clamp(pts/next,0,1);
    const color=b.color||T.gold;
    const active=pts>0;
    const near=(next-pts)<=2&&pts<40;
    r.roundRect(x+10,rowY,w-20,25,9, active?"rgba(255,255,255,.055)":"rgba(255,255,255,.028)", near?color:"rgba(255,255,255,.04)");
    const _brImg=assets?.images?.get?.(`branch_${b.id}`);
    if(_brImg){
      r.ctx.save(); r.ctx.shadowColor=color; r.ctx.shadowBlur=active?10:0; r.ctx.globalCompositeOperation="screen";
      r.ctx.drawImage(_brImg,x+10,rowY+2,22,22); r.ctx.restore();
    } else {
      glowText(r,b.icon||"◆",x+25,rowY+12.5,{ align:"center",baseline:"middle",size:13.5,weight:950, color, glow:active?color:undefined, glowBlur:8 });
    }
    r.text(fitText(b.name,9),x+42,rowY+7,{ size:9.8,weight:950,color:active?"#fff":"rgba(255,255,255,.50)" });
    r.text(`${pts}/${next}`,x+w-14,rowY+7,{ align:"right",size:9.6,weight:950, color:active?color:"rgba(255,255,255,.38)" });
    r.roundRect(x+42,rowY+18,w-64,4,2,"rgba(0,0,0,.50)");
    if(pct>0){
      const barW=Math.max(4,(w-64)*pct);
      r.ctx.save(); r.ctx.shadowColor=color; r.ctx.shadowBlur=6; r.roundRect(x+42,rowY+18,barW,4,2,color); r.ctx.restore();
    }
  });
}

function drawDamageStats(r, stats, assets=null){
  const x=RIGHT.x, y=RIGHT.y+440, w=RIGHT.w, h=114;
  const panelImg = getUiAsset(assets, "ui_market_right_damage_panel");
  if(panelImg) drawUiAsset(r, panelImg, x-8, y-8, w+20, h+18, { shadowColor:"rgba(155,92,255,.20)", shadowBlur:12 });
  else {
    drawGlassPanel(r,x,y,w,h,{ fill:"rgba(4,7,16,.50)", accent:"rgba(155,92,255,.34)", cut:14 });
    drawCornerOrnaments(r.ctx,x,y,w,h,"#9b5cff",10);
  }
  glowText(r,"ULTIMO ROUND",x+w/2,y+17,{ align:"center",size:10.8,weight:950,color:"#c77dff",glow:"#9b5cff",glowBlur:10 });

  const rows=[
    ["✕ Fisico",  Math.round(stats?.physical??stats?.damage??0),"#ffca3a"],
    ["≋ Magico",  Math.round(stats?.magic??0),"#9b5cff"],
    ["☠ DoT",     Math.round(stats?.dot??0),"#70e000"],
    ["◎ Critici", stats?.crits??0,"#ff5c6c"],
    ["♡ Cure",    Math.round(stats?.heals??0),"#06d6a0"],
    ["↓ Subito",  Math.round(stats?.taken??0),"#ef233c"],
  ];
  rows.forEach(([name,val,color],i)=>{
    const yy=y+33+i*13.5;
    r.text(name,x+16,yy,{size:9,weight:850,color:"#cfc4dd"});
    r.ctx.save(); r.ctx.shadowColor=color; r.ctx.shadowBlur=4;
    r.text(String(val),x+w-14,yy,{align:"right",size:9.6,weight:950,color});
    r.ctx.restore();
  });
}

function drawCharacterPanel(r, hero, state, assets=null){
  const x=RIGHT.x, y=RIGHT.y+566, w=RIGHT.w, h=88;
  const panelImg = getUiAsset(assets, "ui_market_hero_panel");
  if(panelImg) drawUiAsset(r, panelImg, x-8, y-8, w+18, h+18, { shadowColor:"rgba(255,202,58,.18)", shadowBlur:12 });
  else {
    drawGlassPanel(r,x,y,w,h,{ fill:"rgba(4,7,14,.52)", accent:"rgba(255,202,58,.30)", cut:14 });
    drawCornerOrnaments(r.ctx,x,y,w,h,T.gold,10);
  }

  if(!hero) return;
  r.ctx.save();
  r.ctx.shadowColor=hero.color||"#888"; r.ctx.shadowBlur=14;
  r.ctx.beginPath(); r.ctx.arc(x+33,y+44,25,0,Math.PI*2); r.ctx.fillStyle=hero.color||"#444"; r.ctx.fill();
  r.ctx.strokeStyle=T.gold; r.ctx.lineWidth=2; r.ctx.stroke();
  r.ctx.restore();
  r.text(hero.icon||"◆",x+33,y+44,{align:"center",baseline:"middle",size:20,weight:950});

  r.text(fitText(hero.name,10),x+70,y+20,{size:12,weight:950,color:"#f6e6b8"});
  const lv=Math.max(1,Math.ceil(Math.min(15,Object.values(state.cardLevels||{}).reduce((a,b)=>a+b,0))/2));
  glowText(r,`Lv. ${lv}`,x+70,y+40,{size:10.5,weight:950,color:T.gold,glow:T.gold,glowBlur:6});

  const s=hero.stats||{};
  [["❤",s.hp],["⚔",s.atk],["🛡",s.arm],["💨",s.spd?.toFixed?.(1)??s.spd]].forEach(([ic,val],i)=>{
    const ax=x+70+i*30;
    r.text(ic,ax,y+64,{align:"center",size:10.5});
    r.text(String(val??"?"),ax,y+78,{align:"center",size:8.5,weight:900,color:"#cfc4dd"});
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// CARDS
// ═══════════════════════════════════════════════════════════════════════════

function drawCardFull(r, card, x, y, w, h, opts={}){
  const {bought=false, levels={}, hovered=false, assets=null, affordable=true, selected=false, gold=0} = opts;
  const color  = rarityColor(card);
  const branch = branchMeta(card);
  const ctx    = r.ctx;
  const lv     = levels[card.id]||0;
  const numBranches = (card.branches||[]).length;

  const frameKey = card.rarity==="Leggendaria" ? "ui_market_card_frame_gold"
                 : card.rarity==="Epica"        ? "ui_market_card_frame_purple"
                 :                                "ui_market_card_frame_green";
  const frameImg = assets?.images?.get?.(frameKey) || assets?.images?.get?.(
    card.rarity==="Leggendaria" ? "frame_leggendaria"
      : card.rarity==="Epica" ? "frame_epica"
      : numBranches>=2 ? "frame_normale_2" : "frame_normale_1"
  );

  ctx.save();
  if(bought) ctx.filter="grayscale(1) brightness(.46)";

  // ── Outer glow ──────────────────────────────────────────────────────────
  if(!bought){
    ctx.save();
    ctx.shadowColor=color; ctx.shadowBlur=hovered?44:20;
    const gp=new Path2D(); gp.roundRect(x,y,w,h,18);
    ctx.strokeStyle="rgba(0,0,0,0)"; ctx.lineWidth=1; ctx.stroke(gp);
    ctx.restore();
  }

  if(selected){
    ctx.save();
    ctx.shadowColor=T.gold; ctx.shadowBlur=34;
    r.roundRect(x-4,y-4,w+8,h+8,22,"rgba(255,202,58,.08)","rgba(255,202,58,.65)",2.2);
    ctx.restore();
  }

  // ── Card base (dark) ─────────────────────────────────────────────────────
  r.roundRect(x,y,w,h,18,"rgba(4,6,16,.96)");

  // ── Art zone: y+32 → y+180 ─────────────────────────────────────────────
  const artX=x+10, artY=y+32, artW=w-20, artH=148;

  ctx.save();
  ctx.beginPath(); ctx.roundRect(artX,artY,artW,artH,10); ctx.clip();

  // Dark base for art
  ctx.fillStyle="rgba(4,8,22,1)"; ctx.fillRect(artX,artY,artW,artH);

  // Subtle radial tint
  const artG=ctx.createRadialGradient(artX+artW/2,artY+artH/2,0,artX+artW/2,artY+artH/2,artW*0.55);
  artG.addColorStop(0,`${color}44`);
  artG.addColorStop(1,"rgba(0,0,0,0)");
  ctx.fillStyle=artG; ctx.fillRect(artX,artY,artW,artH);

  // Branch icon PNG in art zone
  const branchIconImg = assets?.images?.get?.(`branch_${branch?.id}`);
  if(branchIconImg){
    const iconSize=Math.min(artW,artH)*0.76;
    const ix=artX+(artW-iconSize)/2, iy2=artY+(artH-iconSize)/2;
    ctx.save();
    ctx.shadowColor=color; ctx.shadowBlur=22;
    ctx.globalCompositeOperation="screen";
    ctx.drawImage(branchIconImg,ix,iy2,iconSize,iconSize);
    ctx.restore();
  } else {
    ctx.save(); ctx.shadowColor=color; ctx.shadowBlur=22;
    r.text(branch?.icon||"◆",artX+artW/2,artY+artH/2,{
      align:"center",baseline:"middle",size:52,weight:950,color
    });
    ctx.restore();
  }

  // Art bottom fade
  const fadeG=ctx.createLinearGradient(0,artY+artH-24,0,artY+artH+4);
  fadeG.addColorStop(0,"rgba(4,6,16,0)"); fadeG.addColorStop(1,"rgba(4,6,16,1)");
  ctx.fillStyle=fadeG; ctx.fillRect(artX,artY+artH-24,artW,28);
  ctx.restore();

  // ── Frame overlay (screen compositing) ───────────────────────────────────
  if(frameImg){
    ctx.save();
    ctx.globalCompositeOperation="screen";
    ctx.drawImage(frameImg,x,y,w,h);
    ctx.restore();
  }

  // ── Branch icons inside top-frame circles ────────────────────────────────
  const circleIconSize = 28;
  const circleY = y + 18;  // top of card, circle center
  const brsForCircles = card.branches||[];
  if(brsForCircles.length >= 2){
    // Two circles: left and right
    const positions = [x + Math.round(w*0.295), x + Math.round(w*0.695)];
    brsForCircles.slice(0,2).forEach((bid, bi) => {
      const cimg = assets?.images?.get?.(`branch_${bid}`);
      const cx2  = positions[bi];
      if(cimg){
        ctx.save();
        ctx.globalCompositeOperation="screen";
        ctx.shadowColor = (BRANCHES.find(b=>b.id===bid)||{}).color||color;
        ctx.shadowBlur  = 12;
        ctx.drawImage(cimg, cx2 - circleIconSize/2, circleY - circleIconSize/2, circleIconSize, circleIconSize);
        ctx.restore();
      } else {
        const br2 = BRANCHES.find(b=>b.id===bid);
        r.text(br2?.icon||"◆", cx2, circleY, {align:"center",baseline:"middle",size:13,color:br2?.color||color});
      }
    });
  } else if(brsForCircles.length === 1) {
    // Single circle: center
    const bid = brsForCircles[0];
    const cimg = assets?.images?.get?.(`branch_${bid}`);
    const cx2  = x + w/2;
    if(cimg){
      ctx.save();
      ctx.globalCompositeOperation="screen";
      ctx.shadowColor = color; ctx.shadowBlur = 14;
      ctx.drawImage(cimg, cx2 - circleIconSize/2, circleY - circleIconSize/2, circleIconSize, circleIconSize);
      ctx.restore();
    } else {
      r.text(branch?.icon||"◆", cx2, circleY, {align:"center",baseline:"middle",size:14,color});
    }
  }

  // ── Text zone: y+185 → y+h-44 (cost pill) ───────────────────────────────
  // Clip text zone to prevent overflow
  const textY=artY+artH+5;
  const pillY=y+h-42;
  const textZoneH=pillY-textY-4;

  ctx.save();
  ctx.beginPath(); ctx.rect(x+6, textY, w-12, textZoneH+38); ctx.clip();

  // Card name
  glowText(r,fitText(card.name,16).toUpperCase(),x+w/2,textY+13,{
    align:"center",size:12.5,weight:950,color:"#f6e6b8",glow:color,glowBlur:5
  });

  // Rarity
  r.text(card.rarity,x+w/2,textY+27,{align:"center",size:9,weight:900,color});

  // Branch icons row (small PNGs)
  const brs=card.branches||[];
  const brIconSize=16;
  const totalBrW=brs.length*(brIconSize+3)-3;
  brs.forEach((bid,bi)=>{
    const bimg=assets?.images?.get?.(`branch_${bid}`);
    const bx=x+w/2-totalBrW/2+bi*(brIconSize+3);
    const by2=textY+35;
    if(bimg){
      ctx.save(); ctx.globalCompositeOperation="screen";
      ctx.drawImage(bimg,bx,by2,brIconSize,brIconSize);
      ctx.restore();
    } else {
      const br2=BRANCHES.find(b=>b.id===bid);
      r.text(br2?.icon||"◆",bx+brIconSize/2,by2+brIconSize/2,{
        align:"center",baseline:"middle",size:10,color:br2?.color||color
      });
    }
  });

  // Lv + branch points
  r.text(`Lv ${lv}/${card.max}`,x+w/2,textY+57,{
    align:"center",size:8.5,weight:800,color:"rgba(255,255,255,.35)"
  });
  if(card.points){
    r.roundRect(x+w-54,textY+50,38,17,8,"rgba(255,202,58,.10)","rgba(255,202,58,.24)");
    r.text(`+${card.points}`,x+w-35,textY+53,{align:"center",size:8.5,weight:950,color:T.gold});
  }

  // Effect text — max 3 lines, clipped inside zone
  const lines=wrapTextLines(shortEffect(card.desc||card.legacyEffect||""),22);
  lines.slice(0,3).forEach((line,i)=>{
    r.text(line,x+w/2,textY+72+i*18,{
      align:"center",size:10.5,weight:700,color:"#d4cde0"
    });
  });

  ctx.restore();

  // ── Cost pill ─────────────────────────────────────────────────────────────
  ctx.save(); ctx.shadowColor=T.gold; ctx.shadowBlur=10;
  r.roundRect(x+22,pillY,w-44,28,14,"rgba(0,0,0,.90)",color,1.8);
  ctx.restore();
  glowText(r,`🪙 ${card.cost}`,x+w/2,pillY+14,{
    align:"center",baseline:"middle",size:13.5,weight:950,color:"#f6e6b8",
    glow:T.gold,glowBlur:8
  });

  ctx.restore();

  if(!affordable && !bought){
    ctx.save();
    r.roundRect(x+12,y+h-78,w-24,26,13,"rgba(239,35,60,.22)","rgba(239,35,60,.48)");
    r.text(`Mancano ${Math.max(0,(card.cost||0)-gold)} 🪙`,x+w/2,y+h-65,{
      align:"center",baseline:"middle",size:10.5,weight:950,color:"#ffd2d8"
    });
    ctx.restore();
  }

  // ── Bought overlay ─────────────────────────────────────────────────────────
  if(bought){
    ctx.save(); ctx.globalAlpha=0.82;
    r.roundRect(x,y,w,h,18,"rgba(0,0,0,.70)");
    ctx.restore();
    r.text("ACQUISTATA",x+w/2,y+h/2,{
      align:"center",baseline:"middle",size:14,weight:950,color:"#888"
    });
  }
}


// ═══════════════════════════════════════════════════════════════════════════
// BOTTOM BAR
// ═══════════════════════════════════════════════════════════════════════════

function drawBottomBar(r, state, marketOpen=true, phase=0, assets=null){
  const y=692, h=58;
  const smallW=152, gap=12, readyW=210;
  const totalW=(smallW*5) + (gap*5) + readyW;
  const startX=Math.round((1366-totalW)/2);
  const rr={x:startX,y,w:smallW,h};
  const random={x:rr.x+smallW+gap,y,w:smallW,h};
  const collection={x:random.x+smallW+gap,y,w:smallW,h};
  const undo={x:collection.x+smallW+gap,y,w:smallW,h};
  const lock={x:undo.x+smallW+gap,y,w:smallW,h};
  const ready={x:lock.x+smallW+gap,y,w:readyW,h};

  const randomCost=ECONOMY.random_card_cost??100;
  const rerollCost=ECONOMY.reroll_cost??20;
  const poolSize=CardSystem.pool(state).length;
  const ownedCount=CardSystem.ownedCards(state).length;
  const hasUndo=(state.purchaseHistory||[]).length>0;
  const ctx=r.ctx;

  if(marketOpen){
    drawAssetButton(r, rr, assets, "ui_market_btn_reroll", {
      disabled:missingGold(state,rerollCost)>0,
      glow:"rgba(72,202,228,.40)"
    });

    drawAssetButton(r, random, assets, "ui_market_btn_random", {
      sub:poolSize ? formatCostStatus(state,randomCost) : "POOL VUOTO",
      disabled:poolSize<=0 || missingGold(state,randomCost)>0,
      glow:"rgba(72,202,228,.35)"
    });

    drawAssetButton(r, collection, assets, "ui_market_btn_cards", {
      disabled:ownedCount<=0,
      active:!!state.ui?.collectionOpen,
      glow:"rgba(72,202,228,.30)",
      badge:ownedCount>0 ? String(Math.min(99,ownedCount)) : null
    });

    drawAssetButton(r, undo, assets, "ui_market_btn_undo", {
      disabled:!hasUndo,
      glow:"rgba(255,255,255,.22)"
    });

    if(state.shopLocked){
      drawAssetButton(r, lock, assets, "ui_market_btn_lock", {
        active:true,
        glow:"rgba(199,125,255,.40)",
        filter:"brightness(1.05)"
      });
    } else {
      drawAssetButton(r, lock, assets, "ui_market_btn_unlock", {
        glow:"rgba(199,125,255,.32)"
      });
    }
  }

  drawAssetButton(r, ready, assets, "ui_market_btn_ready", {
    glow:"rgba(255,202,58,.55)", glowBlur:20
  });
  if(!getUiAsset(assets, "ui_market_btn_ready")){
    drawPulseRing(ctx,ready.x+ready.w/2,ready.y+h/2,38,T.gold,phase);
    glowText(r,"⚔ READY",ready.x+ready.w/2,ready.y+h/2,{ align:"center",baseline:"middle",size:15.5,weight:950,color:"#fff6d6", glow:T.gold,glowBlur:16 });
  }

  return {
    reroll: marketOpen ? rr : null,
    random: marketOpen ? random : null,
    collection: marketOpen ? collection : null,
    undo: marketOpen ? undo : null,
    lock: marketOpen ? lock : null,
    ready
  };
}

function drawCardInspectPanel(r, card, state, phase = 0, boughtThisRound = new Set(), assets = null) {
  if(!card) return { close:null, buy:null, backdrop:null };
  const ctx = r.ctx;
  const x=354, y=112, w=658, h=486;
  const color = rarityColor(card);
  const lv = cardLevel(state, card);
  const owned = cardOwnedThisRound(state, card, boughtThisRound);
  const affordable = cardAffordable(state, card);
  const canBuy = !owned && affordable;

  ctx.save();
  ctx.fillStyle="rgba(0,0,0,.48)";
  ctx.fillRect(0,0,1366,768);
  ctx.restore();

  drawGlassPanel(r,x,y,w,h,{cut:24,fill:"rgba(5,8,18,.92)",accent:color,lineWidth:2.2});
  drawCornerOrnaments(ctx,x,y,w,h,color,16);

  ctx.save(); ctx.shadowColor=color; ctx.shadowBlur=16;
  r.text(String(card.name||"CARD").toUpperCase(),x+28,y+26,{size:25,weight:950,color:"#fff6d6",shadow:true});
  ctx.restore();
  r.text(`${card.rarity} · Lv ${lv}/${card.max || 1} · ${formatBranchNames(card)}`,x+30,y+62,{size:12.5,weight:900,color:color});

  const close={x:x+w-46,y:y+18,w:28,h:28};
  r.roundRect(close.x,close.y,close.w,close.h,9,"rgba(255,255,255,.09)","rgba(255,255,255,.20)");
  r.text("×",close.x+14,close.y+14,{align:"center",baseline:"middle",size:18,weight:950,color:"#fff"});

  const art={x:x+28,y:y+92,w:208,h:260};
  drawGlassPanel(r,art.x,art.y,art.w,art.h,{cut:18,fill:"rgba(4,6,16,.76)",accent:"rgba(255,255,255,.12)",lineWidth:1.1});
  const br = branchMeta(card);
  const branchIconImg = assets?.images?.get?.(`branch_${br?.id}`);
  r.roundRect(art.x+14,art.y+14,art.w-28,art.h-78,14,"rgba(255,255,255,.045)","rgba(255,255,255,.07)");
  if(branchIconImg){
    const size=132;
    ctx.save(); ctx.shadowColor=color; ctx.shadowBlur=28; ctx.globalCompositeOperation="screen";
    ctx.drawImage(branchIconImg, art.x+art.w/2-size/2, art.y+32, size, size);
    ctx.restore();
  } else {
    ctx.save(); ctx.shadowColor=color; ctx.shadowBlur=28;
    r.text(br?.icon||"◆",art.x+art.w/2,art.y+92,{align:"center",baseline:"middle",size:72,weight:950,color});
    ctx.restore();
  }
  r.roundRect(art.x+20,art.y+196,art.w-40,34,14,"rgba(0,0,0,.72)",color,1.5);
  r.text(`🪙 ${card.cost || 0}`,art.x+art.w/2,art.y+213,{align:"center",baseline:"middle",size:17,weight:950,color:"#fff6d6"});
  r.text(card.points ? `+${card.points} branch point${card.points>1?"s":""}` : "Branch points base",art.x+art.w/2,art.y+240,{align:"center",size:11,weight:900,color:"#cfc4dd"});

  const dx=x+262, dy=y+98, dw=w-294;
  r.text("EFFETTO",dx,dy,{size:12,weight:950,color:T.gold});
  const desc = card.desc || card.legacyEffect || "Nessuna descrizione.";
  const endY = r.wrap(desc,dx,dy+24,dw,19,{size:13.2,weight:760,color:"#f1e7ff"});

  let yy = Math.max(endY + 10, dy + 98);
  if(card.legacyEffect && card.legacyEffect !== card.desc){
    r.text("TESTO LEGACY",dx,yy,{size:11,weight:950,color:"#c77dff"});
    yy = r.wrap(card.legacyEffect,dx,yy+21,dw,17,{size:11.5,weight:650,color:"#cfc4dd"}) + 8;
  }

  const entries = effectEntries(card).slice(0,8);
  if(entries.length){
    r.text("MECCANICHE RUNTIME",dx,yy,{size:11,weight:950,color:T.green});
    yy += 21;
    entries.forEach((line,i)=>{
      const cy=yy+i*24;
      r.roundRect(dx,cy,dw,19,8,"rgba(255,255,255,.045)","rgba(255,255,255,.06)");
      r.text(line,dx+10,cy+4,{size:10.8,weight:850,color:"#dff7ea"});
    });
  }

  const statusText = owned ? "Carta già acquistata / livello massimo" : affordable ? "Pronta da comprare" : `Ti mancano ${Math.max(0,(card.cost||0)-(state.gold||0))} coins`;
  r.text(statusText,x+30,y+h-56,{size:12,weight:900,color:owned?"#888":affordable?T.green:"#ff9aa7"});

  const buy={x:x+w-204,y:y+h-70,w:174,h:44};
  drawGlassPanel(r,buy.x,buy.y,buy.w,buy.h,{cut:16,fill:canBuy?"rgba(160,90,0,.92)":"rgba(70,70,82,.55)",accent:canBuy?"rgba(255,202,58,.76)":"rgba(255,255,255,.14)",lineWidth:1.8});
  r.text(owned?"ACQUISTATA":affordable?"COMPRA":"NON BASTA GOLD",buy.x+buy.w/2,buy.y+buy.h/2,{align:"center",baseline:"middle",size:13.5,weight:950,color:canBuy?"#fff6d6":"#b8adc9"});

  return { close, buy: canBuy ? buy : null, backdrop:{x:0,y:0,w:1366,h:768} };
}

function drawRoundRecapOverlay(r, recap, state, phase = 0, open = true) {
  const pill = { x:602, y:104, w:162, h:30 };
  if(!recap) return { pill:null, close:null };

  if(!open){
    drawGlassPanel(r,pill.x,pill.y,pill.w,pill.h,{
      cut:12, fill:"rgba(6,8,18,.72)", accent:"rgba(155,92,255,.38)", lineWidth:1.3
    });
    r.text(`Round ${recap.round} Recap`,pill.x+pill.w/2,pill.y+pill.h/2,{
      align:"center",baseline:"middle",size:11.5,weight:950,color:"#e7d8ff"
    });
    return { pill, close:null };
  }

  const x=384, y=104, w=598, h=78;
  const win=recap.victory;
  const accent=win ? "rgba(255,202,58,.72)" : "rgba(239,35,60,.62)";
  drawGlassPanel(r,x,y,w,h,{
    cut:20, fill:"rgba(5,8,18,.80)", accent, lineWidth:2
  });
  drawCornerOrnaments(r.ctx,x,y,w,h,win?T.gold:"#ef233c",10);

  const pulse=0.55+0.25*Math.sin(phase*Math.PI*2);
  r.ctx.save();
  r.ctx.shadowColor=win?T.gold:"#ef233c";
  r.ctx.shadowBlur=14*pulse;
  r.text(win?"VICTORY":"DEFEAT",x+24,y+19,{
    size:20,weight:950,color:win?T.gold:"#ff5c6c",shadow:true
  });
  r.ctx.restore();

  const hpLine = win
    ? `${recap.opponentName} -${recap.hpLost || 0} HP`
    : `Tu -${recap.hpLost || 0} HP`;
  const goldDelta=recap.goldDelta||0;
  const goldText=`${goldDelta>=0?"+":""}${goldDelta} gold`;
  const rankText=`Rank #${recap.rank || "?"} · vivi ${recap.aliveCount || "?"}`;

  r.text(`${recap.opponentHero || "Opponent"} · ${hpLine}`,x+24,y+45,{
    size:12.5,weight:850,color:"#f6e6b8"
  });
  r.text(goldText,x+250,y+20,{
    size:15,weight:950,color:goldDelta>=0?T.green:"#ef233c"
  });
  r.text(`HP ${recap.playerHp ?? state.life} · ${rankText}`,x+250,y+45,{
    size:12.5,weight:850,color:"#cfc4dd"
  });

  const dmg=recap.recap||{};
  const rows=[
    ["⚔",Math.round(dmg.physical||0),"#ffca3a"],
    ["✦",Math.round(dmg.magic||0),"#9b5cff"],
    ["☠",Math.round(dmg.dot||0),"#70e000"],
    ["💔",Math.round(dmg.taken||0),"#ef233c"]
  ];
  rows.forEach(([label,val,color],i)=>{
    const bx=x+410+i*38;
    r.roundRect(bx,y+16,30,34,10,"rgba(255,255,255,.055)","rgba(255,255,255,.08)");
    r.text(label,bx+15,y+23,{align:"center",size:10});
    r.text(String(val),bx+15,y+40,{align:"center",size:9.5,weight:950,color});
  });

  const close={x:x+w-34,y:y+9,w:24,h:24};
  r.roundRect(close.x,close.y,close.w,close.h,8,"rgba(255,255,255,.08)","rgba(255,255,255,.16)");
  r.text("×",close.x+12,close.y+12,{align:"center",baseline:"middle",size:16,weight:950,color:"#fff"});
  return { pill:null, close };
}


function drawCollectionPanel(r, state, page = 0, assets = null){
  if(!state.ui?.collectionOpen) return { close:null, prev:null, next:null };
  const ctx=r.ctx;
  const owned=CardSystem.ownedCards(state).sort((a,b)=>String(a.name).localeCompare(String(b.name)));
  const perPage=12;
  const maxPage=Math.max(0,Math.ceil(owned.length/perPage)-1);
  const safePage=clamp(page,0,maxPage);
  const cards=owned.slice(safePage*perPage,safePage*perPage+perPage);
  const x=286, y=118, w=794, h=500;

  ctx.save();
  ctx.fillStyle="rgba(0,0,0,.44)";
  ctx.fillRect(0,0,1366,768);
  ctx.restore();

  drawGlassPanel(r,x,y,w,h,{cut:24,fill:"rgba(5,8,18,.92)",accent:"rgba(177,156,217,.68)",lineWidth:2.2});
  drawCornerOrnaments(ctx,x,y,w,h,"#b19cd9",16);
  r.text("COLLEZIONE CARTE",x+28,y+30,{size:20,weight:950,color:"#f1d6ff",shadow:true});
  r.text("Consulta la tua build: le carte acquistate restano nella run e non possono essere vendute.",x+28,y+56,{size:11.5,weight:720,color:"#cfc4dd"});

  const close={x:x+w-42,y:y+14,w:28,h:28};
  r.roundRect(close.x,close.y,close.w,close.h,9,"rgba(255,255,255,.08)","rgba(255,255,255,.18)");
  r.text("×",close.x+14,close.y+14,{align:"center",baseline:"middle",size:17,weight:950,color:"#fff"});

  if(!owned.length){
    r.text("Nessuna carta posseduta.",x+w/2,y+h/2,{align:"center",baseline:"middle",size:18,weight:900,color:"rgba(255,255,255,.45)"});
    return {close,prev:null,next:null};
  }

  const colW=238, rowH=78, gapX=16, gapY=12;
  const gridX=x+28, gridY=y+86;
  cards.forEach((card,i)=>{
    const col=i%3, row=Math.floor(i/3);
    const cx=gridX+col*(colW+gapX);
    const cy=gridY+row*(rowH+gapY);
    const lv=state.cardLevels?.[card.id]||0;
    const color=rarityColor(card);
    drawGlassPanel(r,cx,cy,colW,rowH,{cut:14,fill:"rgba(8,10,20,.78)",accent:"rgba(255,255,255,.13)",lineWidth:1.2});
    ctx.save(); ctx.shadowColor=color; ctx.shadowBlur=8;
    r.roundRect(cx+10,cy+12,32,32,10,"rgba(255,255,255,.06)",color,1.3);
    ctx.restore();
    const br=branchMeta(card);
    const bimg=assets?.images?.get?.("branch_"+(br?.id));
    if(bimg){
      ctx.save(); ctx.globalCompositeOperation="screen"; ctx.drawImage(bimg,cx+15,cy+17,22,22); ctx.restore();
    } else r.text(br?.icon||"◆",cx+26,cy+28,{align:"center",baseline:"middle",size:15,color});
    r.text(fitText(card.name,18),cx+50,cy+15,{size:11.5,weight:950,color:"#f6e6b8"});
    r.text(card.rarity+" · Lv "+lv+"/"+card.max,cx+50,cy+34,{size:9.5,weight:760,color:color});
    r.text(formatBranchNames(card) || "—",cx+50,cy+52,{size:8.6,weight:650,color:"#cfc4dd"});
    r.roundRect(cx+160,cy+46,64,24,9,"rgba(255,255,255,.06)","rgba(255,255,255,.10)");
    r.text("LOCKED",cx+192,cy+58,{align:"center",baseline:"middle",size:8.8,weight:950,color:"rgba(255,255,255,.48)"});
  });

  const prev={x:x+28,y:y+h-48,w:94,h:30};
  const next={x:x+w-122,y:y+h-48,w:94,h:30};
  const prevDisabled=safePage<=0;
  const nextDisabled=safePage>=maxPage;
  drawActionButton(r,prev,{label:"‹ PREV",sub:"",disabled:prevDisabled,accent:"rgba(177,156,217,.44)",fill:"rgba(22,18,42,.82)"});
  drawActionButton(r,next,{label:"NEXT ›",sub:"",disabled:nextDisabled,accent:"rgba(177,156,217,.44)",fill:"rgba(22,18,42,.82)"});
  r.text("Pagina "+(safePage+1)+"/"+(maxPage+1)+" · "+owned.length+" carte · niente vendita",x+w/2,y+h-30,{align:"center",size:11.5,weight:850,color:"#cfc4dd"});

  return {close,prev:prevDisabled?null:prev,next:nextDisabled?null:next};
}

// ═══════════════════════════════════════════════════════════════════════════
// MARKET SCENE
// ═══════════════════════════════════════════════════════════════════════════

export class MarketScene {
  constructor(app){
    this.app=app;
    this.message=null;
    this.didAutoReady=false;
    this.arena=null;
    this.arenaReady=false;
    this.barRects=null;
    this.toggleRect=null;
    this.cardRects=[];
    this.infoRects=[];
    this.inspectCardId=null;
    this.inspectRects={ close:null, buy:null, backdrop:null };
    this.boughtThisRound=new Set();
    this.freeRerollPending=false;
    this._phase=0; // animation phase 0→1 for breathing effects
    this.recapOpen=!!(app.state.lastRoundRecap && !app.state.lastRoundRecap.seen);
    this.recapAutoLife=this.recapOpen ? 4.6 : 0;
    this.recapRects={ pill:null, close:null };
    this.collectionPage=0;
    this.collectionRects={ close:null, prev:null, next:null };

    app.state.ui??={};
    app.state.ui.cardsOpen=true;
    app.state.ui.collectionOpen=false;
    app.state.startPreparation?.();
    LeagueSystem.ensure(app.state,app.rng);
    if(!app.state.shop.length||!app.state.shopLocked){
      CardSystem.rollShop(app.state,app.rng,3,true);
      this.boughtThisRound.clear();
    }
  }

  async enter(){
    try{
      const {config,images}=await loadArena("data/arenas/arena01_beast_crucible.json");
      this.arena=new ParallaxArena(config,images,{showDebug:false});
      this.arenaReady=true;
    }catch(e){ console.warn("Arena load failed",e); }
  }

  get cardsOpen(){ return this.app.state.ui?.cardsOpen!==false; }
  set cardsOpen(v){ this.app.state.ui??={}; this.app.state.ui.cardsOpen=!!v; }

  getInspectCard(){
    if(!this.inspectCardId) return null;
    return (this.app.state.shop||[]).find(c=>c.id===this.inspectCardId) || null;
  }

  openInspect(card){
    if(!card) return;
    this.inspectCardId=card.id;
    this.app.audio.beep(520,.05,"triangle");
  }

  closeInspect(){ this.inspectCardId=null; }

  buyCard(card){
    if(this.boughtThisRound.has(card.id)) return;
    const res=CardSystem.buy(this.app.state,card.id);
    if(res.ok){
      this.boughtThisRound.add(card.id);
      this.app.audio.beep(720,.08,"triangle");
      this.toast(`${card.name} acquistata`);
      if(this.inspectCardId===card.id) this.inspectCardId=null;
      this._checkAutoReroll();
    } else this.toast(res.reason);
  }

  _checkAutoReroll(){
    const ids=(this.app.state.shop||[]).slice(0,3).map(c=>c.id);
    if(ids.length>0&&ids.every(id=>this.boughtThisRound.has(id))&&!this.freeRerollPending){
      this.freeRerollPending=true;
      setTimeout(()=>{
        CardSystem.rollShop(this.app.state,this.app.rng,3,true);
        this.boughtThisRound.clear();
        this.freeRerollPending=false;
        this.toast("🎉 Reroll gratuito!");
      },450);
    }
  }

  reroll(){
    const cost=ECONOMY.reroll_cost??20;
    const miss=missingGold(this.app.state,cost);
    if(miss>0){ this.toast("Ti mancano "+miss+" coins per il reroll"); return; }
    const res=CardSystem.reroll(this.app.state,this.app.rng,3);
    if(res.ok){ this.boughtThisRound.clear(); this.app.audio.beep(360); this.toast("Shop aggiornato · -"+cost+" 🪙"); }
    else this.toast(res.reason);
  }

  randomCard(){
    const cost=ECONOMY.random_card_cost??100;
    const miss=missingGold(this.app.state,cost);
    if(miss>0){ this.toast("Ti mancano "+miss+" coins per Random"); return; }
    const res=CardSystem.randomBuy(this.app.state,this.app.rng,cost);
    if(res.ok){
      this.app.audio.beep(660,.07,"triangle");
      this.toast("Random: "+res.card.name+" · -"+cost+" 🪙");
      this._checkAutoReroll();
    } else this.toast(res.reason);
  }

  undoPurchase(){
    const res=CardSystem.undoLastPurchase(this.app.state);
    if(res.ok){
      this.boughtThisRound.delete(res.card.id);
      this.app.audio.beep(300,.07,"sine");
      this.toast("Undo: "+res.card.name+" · +"+res.refunded+" 🪙");
    } else this.toast(res.reason);
  }

  toggleCollection(){
    const count=CardSystem.ownedCards(this.app.state).length;
    if(!count){ this.toast("Nessuna carta da mostrare"); return; }
    this.app.state.ui??={};
    this.app.state.ui.collectionOpen=!this.app.state.ui.collectionOpen;
    if(this.app.state.ui.collectionOpen){
      this.inspectCardId=null;
      this.collectionPage=0;
      this.app.audio.beep(520,.05,"triangle");
    } else this.app.audio.beep(320,.05,"triangle");
  }

  toggleLock(){
    this.app.state.shopLocked=!this.app.state.shopLocked;
    this.toast(this.app.state.shopLocked?"Shop bloccato: resta al prossimo market":"Shop sbloccato: prossimo market nuovo");
  }

  ready(){
    if(this.didAutoReady) return;
    this.didAutoReady=true;
    LeagueSystem.prepareRound(this.app.state,this.app.rng);
    this.app.audio.beep(560);
    this.app.scenes.set(CombatScene);
  }

  toast(text){ this.message={text,life:2.2}; }

  update(dt){
    this._phase=(this._phase+dt*0.6)%1; // breathing cycle ~1.7s
    if(this.arena) this.arena.update(dt);
    if(this.message){ this.message.life-=dt; if(this.message.life<=0)this.message=null; }
    if(this.recapOpen && this.recapAutoLife>0){
      this.recapAutoLife-=dt;
      if(this.recapAutoLife<=0){
        this.recapOpen=false;
        if(this.app.state.lastRoundRecap) this.app.state.lastRoundRecap.seen=true;
      }
    }
    if(this.app.state.marketTimer!==undefined){
      this.app.state.marketTimer-=dt;
      if(this.app.state.marketTimer<=0)this.ready();
    }
  }

  handleInput(events){
    for(const ev of events){
      if(ev.type!=="up") continue;
      const {x,y}=ev;
      if(this.app.state.ui?.collectionOpen){
        if(pointInRect(x,y,this.collectionRects?.close)){ this.app.state.ui.collectionOpen=false; continue; }
        if(pointInRect(x,y,this.collectionRects?.prev)){ this.collectionPage=Math.max(0,this.collectionPage-1); continue; }
        if(pointInRect(x,y,this.collectionRects?.next)){ this.collectionPage+=1; continue; }
        if(!pointInRect(x,y,{x:286,y:118,w:794,h:500})){ this.app.state.ui.collectionOpen=false; continue; }
        continue;
      }
      const inspectCard=this.getInspectCard();
      if(inspectCard){
        if(pointInRect(x,y,this.inspectRects?.close)){ this.closeInspect(); continue; }
        if(pointInRect(x,y,this.inspectRects?.buy)){ this.buyCard(inspectCard); continue; }
        if(!pointInRect(x,y,{x:354,y:112,w:658,h:486})){ this.closeInspect(); continue; }
        continue;
      }
      if(pointInRect(x,y,this.recapRects?.close)){
        this.recapOpen=false;
        this.recapAutoLife=0;
        if(this.app.state.lastRoundRecap) this.app.state.lastRoundRecap.seen=true;
        continue;
      }
      if(pointInRect(x,y,this.recapRects?.pill)){
        this.recapOpen=true;
        this.recapAutoLife=0;
        continue;
      }
      if(pointInRect(x,y,this.toggleRect)){
        this.cardsOpen=!this.cardsOpen;
        this.app.audio.beep(this.cardsOpen?460:320,.05,"triangle");
        continue;
      }
      let handledInfo=false;
      for(const rect of this.infoRects||[]){
        if(rect.card&&pointInRect(x,y,rect)){ this.openInspect(rect.card); handledInfo=true; break; }
      }
      if(handledInfo) continue;
      if(this.barRects){
        if(pointInRect(x,y,this.barRects.reroll)){ this.reroll(); continue; }
        if(pointInRect(x,y,this.barRects.random)){ this.randomCard(); continue; }
        if(pointInRect(x,y,this.barRects.collection)){ this.toggleCollection(); continue; }
        if(pointInRect(x,y,this.barRects.undo)){ this.undoPurchase(); continue; }
        if(pointInRect(x,y,this.barRects.lock))  { this.toggleLock(); continue; }
        if(pointInRect(x,y,this.barRects.ready)) { this.ready(); continue; }
      }
      if(this.cardsOpen){
        for(const rect of this.cardRects){
          if(rect.card&&pointInRect(x,y,rect)){ this.buyCard(rect.card); break; }
        }
      }
    }
  }

  branchData(){
    const s=this.app.state;
    return BranchSystem.activeBranchObjects(s).map(b=>{
      const pts=BranchSystem.points(s,b.id);
      return {...b,points:pts,next:BranchSystem.nextThreshold(pts)};
    });
  }

  drawArenaBg(r){
    if(this.arenaReady&&this.arena){
      this.arena.draw(r.ctx,1366,768,null);
    } else {
      drawSceneArt(r,this.app.assets.get("final_market_bg")||this.app.assets.get("final_arena_bg"),{
        alpha:.68,overlayTop:"rgba(6,8,16,.04)",overlayBottom:"rgba(6,5,10,.18)"
      });
    }
    if(this.cardsOpen) drawVignette(r,.50);
    else {
      const ctx=r.ctx, g=ctx.createLinearGradient(0,0,0,768);
      g.addColorStop(0,"rgba(0,0,0,.08)"); g.addColorStop(1,"rgba(0,0,0,.22)");
      ctx.fillStyle=g; ctx.fillRect(0,0,1366,768);
    }
  }

  drawCards(r){
    this.cardRects=[];
    this.infoRects=[];
    if(!this.cardsOpen) return;
    const shop=(this.app.state.shop||[]).slice(0,3);
    for(let i=0;i<3;i++){
      const card=shop[i];
      const x=CARDS_X+i*(CARD_W+CARD_GAP);
      this.cardRects.push({x,y:CARDS_Y,w:CARD_W,h:CARD_H,card});
      if(card){
        const info={x:x+CARD_W-42,y:CARDS_Y+10,w:28,h:28,card};
        drawCardFull(r,card,x,CARDS_Y,CARD_W,CARD_H,{
          bought:this.boughtThisRound.has(card.id),
          levels:this.app.state.cardLevels||{},
          assets:this.app.assets,
          affordable:cardAffordable(this.app.state,card),
          selected:this.inspectCardId===card.id,
          gold:this.app.state.gold||0
        });
        this.infoRects.push(info);
        r.roundRect(info.x,info.y,info.w,info.h,10,"rgba(0,0,0,.72)","rgba(255,255,255,.22)");
        r.text("i",info.x+info.w/2,info.y+info.h/2,{align:"center",baseline:"middle",size:15,weight:950,color:"#fff"});
      } else {
        drawGlassPanel(r,x,CARDS_Y,CARD_W,CARD_H,{cut:20,fill:"rgba(5,7,15,.68)",accent:"rgba(255,255,255,.08)"});
        r.text("—",x+CARD_W/2,CARDS_Y+CARD_H/2,{align:"center",baseline:"middle",size:28,color:"rgba(255,255,255,.18)"});
      }
    }
  }

  drawCardsToggle(r){
    const open=this.cardsOpen;
    const rect={x:596,y:606,w:174,h:82};
    drawAssetButton(r, rect, this.app.assets, "ui_market_btn_market", {
      active:open,
      glow:"rgba(72,202,228,.32)",
      filter: open ? "brightness(1.06)" : "none"
    });
    const ctx=r.ctx;
    ctx.save();
    ctx.shadowColor="rgba(72,202,228,.40)";
    ctx.shadowBlur=10;
    r.text(open ? "▲" : "▼", rect.x+rect.w/2, rect.y+rect.h-10,{
      align:"center",baseline:"middle",size:12,weight:950,color:"#e9f8ff"
    });
    ctx.restore();
    return rect;
  }

  drawToast(r){
    if(!this.message) return;
    const tw=332,th=36,tx=683-tw/2,ty=604;
    r.ctx.save();
    r.ctx.shadowColor=T.gold; r.ctx.shadowBlur=14;
    r.roundRect(tx,ty,tw,th,14,"rgba(0,0,0,.82)","rgba(255,202,58,.45)");
    r.ctx.restore();
    r.text(this.message.text,683,ty+th/2,{
      align:"center",baseline:"middle",size:13,weight:950,color:"#fff"
    });
  }

  draw(r){
    const state=this.app.state;
    const players=state.league?.players||[];
    const branches=this.branchData();
    const activeIds=branches.map(b=>b.id);

    this.drawArenaBg(r);
    drawMarketTimer(r,state.round,state.marketTimer??30,this._phase,this.app.assets,state);
    drawLeaderboard(r,players,state,this.app.assets);
    drawBannedBranches(r,BRANCHES||[],activeIds,this.app.assets);
    drawBranchReport(r,branches,this.app.assets);
    drawDamageStats(r,state.lastRoundRecap?.recap || state.stats,this.app.assets);
    drawCharacterPanel(r,state.hero,state,this.app.assets);
    this.drawCards(r);
    this.toggleRect=this.drawCardsToggle(r);
    this.barRects=drawBottomBar(r,state,this.cardsOpen,this._phase,this.app.assets);
    this.recapRects=drawRoundRecapOverlay(r,state.lastRoundRecap,state,this._phase,this.recapOpen);
    this.collectionRects=drawCollectionPanel(r,state,this.collectionPage,this.app.assets);
    this.drawToast(r);
    this.inspectRects=drawCardInspectPanel(r,this.getInspectCard(),state,this._phase,this.boughtThisRound,this.app.assets);
  }
}
