export class Button {
  constructor(o) {
    Object.assign(this, o);
    this.variant ??= "primary";
    this.p = false;
    this.disabled ??= false;
  }

  contains(x, y) {
    return x >= this.x && x <= this.x + this.w && y >= this.y && y <= this.y + this.h;
  }

  handle(ev) {
    if (this.disabled) return false;
    for (const e of ev) {
      if (e.type === "down" && this.contains(e.x, e.y)) this.p = true;
      if (e.type === "up") {
        const was = this.p;
        this.p = false;
        if (was && this.contains(e.x, e.y)) {
          try { navigator.vibrate?.(8); } catch {}
          this.onClick?.();
          return true;
        }
      }
    }
    return false;
  }

  draw(r) {
    const primary = this.variant === "primary";
    const danger = this.variant === "danger";
    const fill = this.disabled ? "rgba(255,255,255,.05)" :
      danger ? "#ef476f" : primary ? "#ffb703" : "rgba(255,255,255,.09)";
    const col = this.disabled ? "#777" : (primary || danger) ? "#171014" : "#fff";
    r.roundRect(this.x, this.y + (this.p ? 2 : 0), this.w, this.h, Math.min(18, this.h/2), fill, "rgba(255,255,255,.13)", 1.2);
    r.text(this.label, this.x + this.w/2, this.y + this.h/2 + (this.p ? 2 : 0), {
      align:"center", baseline:"middle", color:col, weight:950, size:this.size || 15
    });
  }
}
