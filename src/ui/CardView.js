export class CardView {
  constructor(card, x, y, w, h, level = 0, mode = "row") {
    Object.assign(this, { card, x, y, w, h, level, mode });
  }

  contains(x, y) {
    return x >= this.x && x <= this.x + this.w && y >= this.y && y <= this.y + this.h;
  }

  draw(r, a) {
    if (this.mode === "large") return this.drawLarge(r, a);
    r.roundRect(this.x, this.y, this.w, this.h, 18, "rgba(255,255,255,.075)", "rgba(255,255,255,.10)");
    r.img(a.get(this.card.id), this.x+8, this.y+8, 72, 105, 14);
    r.text(this.card.name, this.x+90, this.y+12, { size:15, weight:900 });
    r.text(`${this.card.rarity} · +${this.card.points}`, this.x+90, this.y+34, { size:12, color:"#ffb703", weight:800 });
    r.wrap(this.card.desc, this.x+90, this.y+54, this.w-102, 15, { size:12, color:"#cfc4dd", weight:600 });
    r.text(`Lv ${this.level}/${this.card.max}`, this.x+90, this.y+this.h-22, { size:12, color:"#06d6a0", weight:900 });
    r.text(`${this.card.cost}`, this.x+this.w-14, this.y+this.h-22, { size:12, align:"right", color:"#ffb703", weight:900 });
  }

  drawLarge(r, a) {
    r.roundRect(this.x, this.y, this.w, this.h, 20, "rgba(20,24,44,.86)", "rgba(255,255,255,.14)", 1.2);
    r.img(a.get(this.card.id), this.x+10, this.y+10, this.w-20, this.h-58, 16);
    r.text(this.card.name, this.x+this.w/2, this.y+this.h-42, { align:"center", size:14, weight:950, color:"#fff" });
    r.text(`${this.card.rarity} · Lv ${this.level}/${this.card.max}`, this.x+this.w/2, this.y+this.h-22, { align:"center", size:11, weight:850, color:"#ffb703" });
  }
}
