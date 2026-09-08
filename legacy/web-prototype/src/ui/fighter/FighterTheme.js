export const FighterTheme = {
  colors: {
    obsidian:"#080a10", panel:"rgba(9,12,20,.84)", gold:"#ffca3a", ivory:"#f6e6b8",
    red:"#ef233c", green:"#70e000", blue:"#168aad", cyan:"#48cae4", violet:"#9b5cff", muted:"#b8adc9"
  },
  rarity: { Normale:"#38bdf8", Normal:"#38bdf8", Comune:"#8a8f98", Rara:"#38bdf8", Epica:"#c77dff", Leggendaria:"#ffca3a", Legendary:"#ffca3a", Mythic:"#06d6a0" }
};
export function drawBeveledPanel(r,x,y,w,h,o={}){const c=r.ctx,cut=o.cut??16;c.save();c.beginPath();c.moveTo(x+cut,y);c.lineTo(x+w-cut,y);c.lineTo(x+w,y+cut);c.lineTo(x+w,y+h-cut);c.lineTo(x+w-cut,y+h);c.lineTo(x+cut,y+h);c.lineTo(x,y+h-cut);c.lineTo(x,y+cut);c.closePath();c.fillStyle=o.fill??FighterTheme.colors.panel;c.fill();c.strokeStyle=o.stroke??"rgba(255,202,58,.34)";c.lineWidth=o.lineWidth??1.5;c.stroke();const g=c.createLinearGradient(x,y,x,y+h);g.addColorStop(0,"rgba(255,255,255,.08)");g.addColorStop(.32,"rgba(255,255,255,.02)");g.addColorStop(1,"rgba(0,0,0,.34)");c.fillStyle=g;c.fill();c.restore();}
export function drawSlantedBar(r,x,y,w,h,pct,fill,o={}){const c=r.ctx,p=Math.max(0,Math.min(1,pct)),cut=o.cut??12;c.save();c.beginPath();c.moveTo(x+cut,y);c.lineTo(x+w,y);c.lineTo(x+w-cut,y+h);c.lineTo(x,y+h);c.closePath();c.fillStyle=o.bg??"rgba(0,0,0,.58)";c.fill();c.strokeStyle=o.stroke??"rgba(255,255,255,.16)";c.stroke();if(p>0){const fw=Math.max(cut,w*p);c.beginPath();c.moveTo(x+cut,y+2);c.lineTo(x+fw,y+2);c.lineTo(x+Math.max(0,fw-cut),y+h-2);c.lineTo(x+2,y+h-2);c.closePath();const g=c.createLinearGradient(x,y,x+w,y);g.addColorStop(0,fill);g.addColorStop(1,o.fill2??fill);c.fillStyle=g;c.fill();}c.restore();}
export function drawHexPortrait(r,img,x,y,size,o={}){const c=r.ctx,s=size,pts=[[x+s*.22,y],[x+s*.78,y],[x+s,y+s*.28],[x+s*.88,y+s],[x+s*.12,y+s],[x,y+s*.28]];c.save();c.beginPath();pts.forEach((p,i)=>i?c.lineTo(p[0],p[1]):c.moveTo(p[0],p[1]));c.closePath();c.fillStyle=o.fill??"rgba(0,0,0,.55)";c.fill();c.strokeStyle=o.stroke??FighterTheme.colors.gold;c.lineWidth=o.lineWidth??3;c.stroke();c.clip();if(img)c.drawImage(img,x,y,s,s);c.restore();}
export function fitText(t,max=14){t=String(t||"");return t.length>max?t.slice(0,max-1)+"…":t;}
