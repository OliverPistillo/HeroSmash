function lerp(a, b, t) { return a + (b - a) * t; }
function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }

export class ParallaxArena {
  constructor(config, images, options = {}) {
    this.config = config;
    this.images = images;
    this.time = 0;
    this.camera = {
      x: 0,
      y: 0,
      zoom: config.camera?.combat?.zoom ?? 1,
      shakeX: 0,
      shakeY: 0,
      phase: 'combat',
      targetX: 0,
      targetY: 0
    };
    this.design = config.sourceResolution || { width: 2048, height: 1152 };
    this.showDebug = options.showDebug ?? false;
    this.dust = this.makeDust();
  }

  makeDust() {
    const fx = this.config.runtimeFx?.dust;
    if (!fx?.enabled) return [];
    const area = fx.spawnArea;
    return Array.from({ length: fx.count || 24 }, (_, i) => ({
      x: area.x + Math.random() * area.w,
      y: area.y + Math.random() * area.h,
      r: 1 + Math.random() * 2.5,
      speed: 0.15 + Math.random() * 0.35,
      phase: Math.random() * Math.PI * 2,
      alpha: (fx.alpha || 0.18) * (0.35 + Math.random() * 0.65)
    }));
  }

  update(dt) {
    this.time += dt;
    const drift = this.config.camera?.idleDrift;
    if (drift?.enabled) {
      this.camera.x = Math.sin(this.time * drift.speed) * drift.x;
      this.camera.y = Math.cos(this.time * drift.speed * 0.8) * drift.y;
    }
    this.camera.shakeX *= Math.pow(0.001, dt);
    this.camera.shakeY *= Math.pow(0.001, dt);
  }

  impact(kind = 'small') {
    const impact = this.config.camera?.impact || {};
    const amount = kind === 'heavy' ? impact.shakeHeavy : kind === 'medium' ? impact.shakeMedium : impact.shakeSmall;
    const a = amount || 4;
    this.camera.shakeX = (Math.random() * 2 - 1) * a;
    this.camera.shakeY = (Math.random() * 2 - 1) * a * 0.55;
  }

  draw(ctx, canvasWidth, canvasHeight, drawRuntime = null) {
    const sx = canvasWidth / this.design.width;
    const sy = canvasHeight / this.design.height;

    ctx.save();
    ctx.scale(sx, sy);
    this.drawInDesignSpace(ctx, drawRuntime);
    ctx.restore();
  }

  drawInDesignSpace(ctx, drawRuntime) {
    const layers = [...(this.config.layers || [])].sort((a, b) => a.z - b.z);
    for (const layer of layers) {
      if (layer.type === 'runtime') {
        drawRuntime?.(ctx, layer.id, this.config, this.time);
        continue;
      }
      this.drawLayer(ctx, layer);
    }
    this.drawLighting(ctx);
    if (this.showDebug) this.drawDebug(ctx);
  }

  drawLayer(ctx, layer) {
    const img = this.images.get(layer.asset);
    if (!img) return;

    const parallax = layer.parallax ?? 1;
    const px = -(this.camera.x + this.camera.shakeX) * parallax;
    const py = -(this.camera.y + this.camera.shakeY) * parallax;
    const scale = layer.scale ?? 1;
    const alpha = layer.alpha ?? 1;

    let animY = 0;
    if (layer.animation?.type === 'float_glow') {
      animY = Math.sin(this.time * layer.animation.speed) * layer.animation.amplitudeY;
      this.drawGlow(ctx, layer, px, py, animY);
    }

    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(
      img,
      (layer.x || 0) + px,
      (layer.y || 0) + py + animY,
      img.width * scale,
      img.height * scale
    );
    ctx.restore();
  }

  drawGlow(ctx, layer, px, py, animY) {
    const a = layer.animation;
    const pulse = (Math.sin(this.time * a.speed * 1.7) + 1) / 2;
    const alpha = lerp(a.glowAlphaMin ?? 0.08, a.glowAlphaMax ?? 0.22, pulse);
    const radius = a.glowRadius ?? 180;
    const x = (layer.x || 0) + px + (this.design.width * (layer.scale || 1)) / 2;
    const y = (layer.y || 0) + py + animY + 180;
    const g = ctx.createRadialGradient(x, y, 0, x, y, radius);
    g.addColorStop(0, a.glowColor || '#42aaff');
    g.addColorStop(1, 'rgba(66,170,255,0)');
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.globalCompositeOperation = 'lighter';
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  drawLighting(ctx) {
    const l = this.config.lighting || {};
    for (const key of ['sunGlow', 'crystalGlow', 'floorGlow']) {
      const glow = l[key];
      if (!glow?.enabled) continue;
      const g = ctx.createRadialGradient(glow.x, glow.y, 0, glow.x, glow.y, glow.radius);
      g.addColorStop(0, glow.color);
      g.addColorStop(1, 'rgba(255,255,255,0)');
      ctx.save();
      ctx.globalAlpha = glow.alpha ?? 0.1;
      ctx.globalCompositeOperation = 'lighter';
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, this.design.width, this.design.height);
      ctx.restore();
    }
    this.drawAmbientDust(ctx);
  }

  drawAmbientDust(ctx) {
    const fx = this.config.runtimeFx?.dust;
    if (!fx?.enabled) return;
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    ctx.fillStyle = fx.color || '#ffd36a';
    for (const d of this.dust) {
      const x = d.x + Math.sin(this.time * d.speed + d.phase) * 18;
      const y = d.y + Math.cos(this.time * d.speed * 0.7 + d.phase) * 8;
      ctx.globalAlpha = d.alpha;
      ctx.beginPath();
      ctx.arc(x, y, d.r, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  }

  drawDebug(ctx) {
    const fp = this.config.fightPlane;
    if (!fp) return;
    ctx.save();
    ctx.strokeStyle = 'rgba(0,255,255,.65)';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.ellipse(fp.floorEllipse.x, fp.floorEllipse.y, fp.floorEllipse.radiusX, fp.floorEllipse.radiusY, 0, 0, Math.PI * 2);
    ctx.stroke();
    ctx.strokeStyle = 'rgba(255,0,0,.65)';
    ctx.beginPath();
    ctx.moveTo(0, fp.baselineY);
    ctx.lineTo(this.design.width, fp.baselineY);
    ctx.stroke();
    ctx.restore();
  }
}
