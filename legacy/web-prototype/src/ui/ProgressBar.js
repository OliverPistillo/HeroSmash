export function bar(r, x, y, w, h, value, max, fill = "#06d6a0", label = "") {
  const pct = Math.max(0, Math.min(1, value / Math.max(1, max)));
  r.roundRect(x, y, w, h, h/2, "rgba(255,255,255,.12)");
  r.roundRect(x, y, w * pct, h, h/2, fill);
  if (label) r.text(label, x+w/2, y+h/2, { align:"center", baseline:"middle", size:10, weight:900, color:"#fff", shadow:true });
}

export function drawProgressBar(r, x, y, w, h, value, max, fill = "#06d6a0") {
  bar(r, x, y, w, h, value, max, fill);
}
