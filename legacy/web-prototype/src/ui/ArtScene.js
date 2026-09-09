export function drawSceneArt(r, img, opts = {}) {
  const {
    alpha = 0.72,
    overlayTop = "rgba(10,8,22,.28)",
    overlayBottom = "rgba(6,5,11,.84)",
    fallback = true
  } = opts;
  if (img) {
    r.ctx.save();
    r.ctx.globalAlpha = alpha;
    r.ctx.drawImage(img, 0, 0, 1366, 768);
    r.ctx.restore();
  } else if (fallback) {
    r.bg();
  }
  const g = r.ctx.createLinearGradient(0,0,0,768);
  g.addColorStop(0, overlayTop);
  g.addColorStop(1, overlayBottom);
  r.ctx.fillStyle = g;
  r.ctx.fillRect(0,0,1366,768);
}

export function artPanel(r, x, y, w, h, title, img, opts = {}) {
  r.roundRect(x, y, w, h, opts.radius || 24, opts.fill || "rgba(13,17,32,.74)", opts.stroke || "rgba(255,255,255,.12)", 1.5);
  if (img) {
    r.ctx.save();
    r.roundRect(x+10, y+38, w-20, h-48, Math.max(12, (opts.radius || 24)-8), null);
    r.ctx.clip();
    r.ctx.globalAlpha = opts.imageAlpha || .50;
    r.ctx.drawImage(img, x+10, y+38, w-20, h-48);
    r.ctx.restore();
    r.roundRect(x+10, y+38, w-20, h-48, Math.max(12, (opts.radius || 24)-8), "rgba(7,8,16,.26)");
  }
  if (title) r.text(title, x+20, y+14, { size: 15, weight: 950, color: "#ffca3a" });
}
