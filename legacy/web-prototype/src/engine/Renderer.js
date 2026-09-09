export class Renderer {
  constructor(canvas, w = 1366, h = 768) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.logicalWidth = w;
    this.logicalHeight = h;
    this.scale = 1;
    this.ox = 0;
    this.oy = 0;
    this.isPortrait = false;
    this.resize();
    addEventListener("resize", () => this.resize());
    addEventListener("orientationchange", () => setTimeout(() => this.resize(), 120));
  }

  resize() {
    const dpr = Math.max(1, Math.min(3, devicePixelRatio || 1));
    const w = innerWidth;
    const h = innerHeight;
    this.isPortrait = h > w;
    this.canvas.width = Math.floor(w * dpr);
    this.canvas.height = Math.floor(h * dpr);
    this.canvas.style.width = w + "px";
    this.canvas.style.height = h + "px";
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    this.scale = Math.min(w / this.logicalWidth, h / this.logicalHeight);
    this.ox = (w - this.logicalWidth * this.scale) / 2;
    this.oy = (h - this.logicalHeight * this.scale) / 2;
  }

  toWorld(x, y) {
    return { x: (x - this.ox) / this.scale, y: (y - this.oy) / this.scale };
  }

  begin() {
    this.ctx.save();
    this.ctx.clearRect(0, 0, innerWidth, innerHeight);
    this.ctx.fillStyle = "#05040a";
    this.ctx.fillRect(0, 0, innerWidth, innerHeight);
    this.ctx.translate(this.ox, this.oy);
    this.ctx.scale(this.scale, this.scale);
  }

  end() {
    this.ctx.restore();
    if (this.isPortrait) this.drawRotateOverlay();
  }

  drawRotateOverlay() {
    const c = this.ctx;
    c.save();
    c.fillStyle = "rgba(5,4,10,.94)";
    c.fillRect(0, 0, innerWidth, innerHeight);
    c.fillStyle = "#ffb703";
    c.font = "900 58px system-ui, sans-serif";
    c.textAlign = "center";
    c.textBaseline = "middle";
    c.fillText("↻", innerWidth / 2, innerHeight / 2 - 92);
    c.fillStyle = "#fff";
    c.font = "900 24px system-ui, sans-serif";
    c.fillText("Ruota il dispositivo", innerWidth / 2, innerHeight / 2 - 32);
    c.fillStyle = "#b8adc9";
    c.font = "700 15px system-ui, sans-serif";
    c.fillText("Hero Smash ora usa layout orizzontale.", innerWidth / 2, innerHeight / 2 + 6);
    c.fillText("Come un auto-battler serio, non come un menu da ascensore.", innerWidth / 2, innerHeight / 2 + 34);
    c.restore();
  }

  bg() { this.clearGradient(); }

  clearGradient() {
    const c = this.ctx;
    const g = c.createRadialGradient(683, 0, 80, 683, 420, 1100);
    g.addColorStop(0, "#31205a");
    g.addColorStop(0.48, "#111524");
    g.addColorStop(1, "#06050b");
    c.fillStyle = g;
    c.fillRect(0, 0, this.logicalWidth, this.logicalHeight);

    // arena-like ground
    const floor = c.createLinearGradient(0, 120, 0, 768);
    floor.addColorStop(0, "rgba(115,155,112,.20)");
    floor.addColorStop(.45, "rgba(180,158,112,.14)");
    floor.addColorStop(1, "rgba(49,35,61,.40)");
    c.fillStyle = floor;
    c.fillRect(0, 80, 1366, 688);

    c.strokeStyle = "rgba(255,255,255,.045)";
    c.lineWidth = 1;
    for (let x = 80; x < 1300; x += 72) {
      c.beginPath(); c.moveTo(x, 110); c.lineTo(x - 95, 768); c.stroke();
    }
    for (let y = 140; y < 760; y += 58) {
      c.beginPath(); c.moveTo(0, y); c.lineTo(1366, y + 18); c.stroke();
    }

    c.strokeStyle = "rgba(255,183,3,.16)";
    c.lineWidth = 4;
    c.beginPath();
    c.ellipse(690, 392, 330, 218, 0, 0, Math.PI * 2);
    c.stroke();
    c.lineWidth = 2;
    c.beginPath();
    c.ellipse(690, 392, 215, 142, 0, 0, Math.PI * 2);
    c.stroke();
  }

  topBar(title = "", subtitle = "") {
    this.roundRect(18, 14, 1330, 58, 20, "rgba(14,18,35,.82)", "rgba(255,255,255,.10)");
    if (title) this.text(title, 683, 25, { align:"center", size:22, weight:950, color:"#fff" });
    if (subtitle) this.text(subtitle, 683, 51, { align:"center", size:12, weight:850, color:"#ffb703" });
  }

  panel(x, y, w, h, alpha = .74) {
    this.roundRect(x, y, w, h, 22, `rgba(20,24,44,${alpha})`, "rgba(255,255,255,.10)");
  }

  roundRect(x, y, w, h, r, fill, stroke = null, lineWidth = 1) {
    const c = this.ctx;
    c.beginPath();
    c.moveTo(x + r, y);
    c.arcTo(x + w, y, x + w, y + h, r);
    c.arcTo(x + w, y + h, x, y + h, r);
    c.arcTo(x, y + h, x, y, r);
    c.arcTo(x, y, x + w, y, r);
    c.closePath();
    if (fill) { c.fillStyle = fill; c.fill(); }
    if (stroke) { c.strokeStyle = stroke; c.lineWidth = lineWidth; c.stroke(); }
  }

  text(t, x, y, o = {}) {
    const c = this.ctx;
    c.save();
    c.fillStyle = o.color || "#fff";
    c.font = `${o.weight || 700} ${o.size || 16}px ${o.family || "system-ui,sans-serif"}`;
    c.textAlign = o.align || "left";
    c.textBaseline = o.baseline || "top";
    if (o.shadow) {
      c.shadowColor = "rgba(0,0,0,.65)";
      c.shadowBlur = 8;
      c.shadowOffsetY = 2;
    }
    c.fillText(String(t), x, y);
    c.restore();
  }

  wrap(t, x, y, w, lh, o = {}) {
    const words = String(t).split(" ");
    let line = "", yy = y;
    this.ctx.font = `${o.weight || 600} ${o.size || 14}px system-ui`;
    for (const word of words) {
      const test = line ? line + " " + word : word;
      if (this.ctx.measureText(test).width > w && line) {
        this.text(line, x, yy, o);
        line = word;
        yy += lh;
      } else line = test;
    }
    if (line) this.text(line, x, yy, o);
    return yy + lh;
  }

  img(img, x, y, w, h, r = 0) {
    const c = this.ctx;
    if (!img) {
      this.roundRect(x, y, w, h, r, "rgba(255,255,255,.08)", "rgba(255,255,255,.10)");
      return;
    }
    if (!r) { c.drawImage(img, x, y, w, h); return; }
    c.save();
    this.roundRect(x, y, w, h, r, null);
    c.clip();
    c.drawImage(img, x, y, w, h);
    c.restore();
  }

  drawImage(img, x, y, w, h, r = 0) { this.img(img, x, y, w, h, r); }
  clearGradientAlias() { this.clearGradient(); }

// ── Sprite Sheet ─────────────────────────────────────────────────────────

  /**
   * Disegna un singolo frame da uno spritesheet.
   * @param {HTMLImageElement|HTMLCanvasElement} image
   * @param {number} sx,sy,sw,sh — rect sorgente nel foglio
   * @param {number} dx,dy,dw,dh — rect destinazione sullo schermo
   * @param {boolean} flipX       — specchio orizzontale (per il nemico)
   * @param {number}  alpha       — opacità 0–1
   */
  drawSprite(image, sx, sy, sw, sh, dx, dy, dw, dh, flipX = false, alpha = 1) {
    const c = this.ctx;
    c.save();
    if (alpha < 1) c.globalAlpha = alpha;
    if (flipX) {
      c.translate(dx + dw, dy);
      c.scale(-1, 1);
      c.drawImage(image, sx, sy, sw, sh, 0, 0, dw, dh);
    } else {
      c.drawImage(image, sx, sy, sw, sh, dx, dy, dw, dh);
    }
    c.restore();
  }

  /**
   * Disegna un frame con effetto colore (tint) sovrapposto.
   * Utile per flash di danno, status, etc.
   */
  drawSpriteColored(image, sx, sy, sw, sh, dx, dy, dw, dh, flipX = false, tintColor = null, tintAlpha = 0) {
    this.drawSprite(image, sx, sy, sw, sh, dx, dy, dw, dh, flipX);
    if (tintColor && tintAlpha > 0) {
      const c = this.ctx;
      c.save();
      c.globalAlpha     = tintAlpha;
      c.globalCompositeOperation = 'source-atop';
      // draw sprite again as mask, then fill
      if (flipX) {
        c.translate(dx + dw, dy);
        c.scale(-1, 1);
        c.drawImage(image, sx, sy, sw, sh, 0, 0, dw, dh);
      } else {
        c.drawImage(image, sx, sy, sw, sh, dx, dy, dw, dh);
      }
      c.globalCompositeOperation = 'source-over';
      c.fillStyle = tintColor;
      c.globalAlpha = tintAlpha * 0.5;
      c.fillRect(dx, dy, dw, dh);
      c.restore();
    }
  }
}
