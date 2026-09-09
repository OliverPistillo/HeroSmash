export class AssetManager {
  constructor() {
    this.images = new Map();
    this.records = new Map();
    this.failed = new Set();
    this.pending = 0;
    this.loaded = 0;
    this.fallbacks = new Map();
  }

  async loadImages(manifest) {
    const entries = Object.entries(manifest);
    this.pending = entries.length;
    this.loaded = 0;
    await Promise.all(entries.map(([key, url]) => this.loadImage(key, url)));
  }

  async loadFromRegistry(registry) {
    const manifest = {};
    for (const [key, rec] of Object.entries(registry.images || {})) {
      manifest[rec.id] = rec.path;
      this.records.set(rec.id, rec);
    }
    await this.loadImages(manifest);
  }

  loadImage(key, url) {
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => {
        this.images.set(key, img);
        this.loaded += 1;
        resolve(img);
      };
      img.onerror = () => {
        console.warn("Asset failed:", key, url);
        this.failed.add(key);
        this.images.set(key, this.makeFallback(key));
        this.loaded += 1;
        resolve(this.images.get(key));
      };
      img.src = url;
    });
  }

  makeFallback(key) {
    if (this.fallbacks.has(key)) return this.fallbacks.get(key);
    const c = document.createElement("canvas");
    c.width = 256;
    c.height = 384;
    const ctx = c.getContext("2d");
    const g = ctx.createLinearGradient(0,0,256,384);
    g.addColorStop(0, "#2b1745");
    g.addColorStop(1, "#08060d");
    ctx.fillStyle = g;
    ctx.fillRect(0,0,256,384);
    ctx.strokeStyle = "#ffb703";
    ctx.lineWidth = 8;
    ctx.strokeRect(8,8,240,368);
    ctx.fillStyle = "#fff";
    ctx.font = "900 42px system-ui";
    ctx.textAlign = "center";
    ctx.fillText("?", 128, 176);
    ctx.fillStyle = "#ffb703";
    ctx.font = "800 18px system-ui";
    ctx.fillText("MISSING", 128, 220);
    ctx.fillStyle = "#b8adc9";
    ctx.font = "700 12px system-ui";
    ctx.fillText(String(key).slice(0,24), 128, 248);
    this.fallbacks.set(key, c);
    return c;
  }

  get(key) {
    return this.images.get(key) || this.makeFallback(key);
  }

  has(key) {
    return this.images.has(key) && !this.failed.has(key);
  }

  get progress() {
    if (!this.pending) return 1;
    return this.loaded / this.pending;
  }

  get report() {
    return {
      pending: this.pending,
      loaded: this.loaded,
      failed: [...this.failed],
      ok: this.pending - this.failed.size
    };
  }

// ── Sprite Sheets ─────────────────────────────────────────────────────────

  /**
   * Carica un manifest JSON + la sua PNG e li registra nell'AnimationSystem.
   * @param {string}          heroId
   * @param {string}          jsonUrl  — percorso del manifest canonico
   * @param {AnimationSystem} anim
   */
  async loadSpriteSheet(heroId, jsonUrl, anim) {
    try {
      const res      = await fetch(jsonUrl);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const manifest = await res.json();
      const image    = await new Promise((resolve, reject) => {
        const img  = new Image();
        img.onload = () => resolve(img);
        img.onerror= () => reject(new Error(`Image load failed: ${manifest.meta.image}`));
        img.src    = manifest.meta.image;
      });
      anim.register(heroId, image, manifest);
      this.images.set(`sprite_${heroId}`, image);
    } catch (e) {
      console.warn(`[AssetManager] Sprite sheet non trovato per ${heroId}:`, e.message);
      // Graceful degradation: il hero userà il fallback cerchio
    }
  }

  /**
   * Carica tutti gli sprite sheets registrati nel manifest globale.
   * @param {object}          spritesManifest — { heroes: { id: { manifest } } }
   * @param {AnimationSystem} anim
   */
  async loadAllSpriteSheets(spritesManifest, anim) {
    const entries = Object.entries(spritesManifest.heroes || {});
    await Promise.all(
      entries.map(([heroId, def]) => this.loadSpriteSheet(heroId, def.manifest, anim))
    );
  }
}
