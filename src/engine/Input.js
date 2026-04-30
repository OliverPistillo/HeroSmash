export class Input {
  constructor(canvas, renderer) {
    this.r = renderer;
    this.events = [];
    this.pointer = { x:0, y:0, down:false };
    this.last = null;
    for (const t of ["pointerdown","pointermove","pointerup","pointercancel"]) {
      canvas.addEventListener(t, e => this.on(e, t), { passive:false });
    }
    canvas.addEventListener("contextmenu", e => e.preventDefault());
  }

  on(e, t) {
    e.preventDefault?.();
    const p = this.r.toWorld(e.clientX, e.clientY);
    const type = t.includes("down") ? "down" : t.includes("move") ? "move" : "up";
    const dx = this.last ? p.x - this.last.x : 0;
    const dy = this.last ? p.y - this.last.y : 0;
    this.pointer = { x:p.x, y:p.y, down:type !== "up" };
    this.events.push({ type, x:p.x, y:p.y, dx, dy, raw:e });
    if (type === "up") this.last = null;
    else this.last = p;
  }

  consume() {
    const out = this.events;
    this.events = [];
    return out;
  }
}
