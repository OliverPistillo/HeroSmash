/**
 * AnimationSystem — gestisce stati e frame delle sprite sheet per ogni hero.
 *
 * Formato manifest atteso:
 * {
 *   meta: { image, frameW, frameH, sheetW, sheetH },
 *   animations: {
 *     idle:    { row, frames, fps, loop },
 *     attack:  { row, frames, fps, loop },
 *     ...
 *   }
 * }
 *
 * Uso:
 *   app.anim.register(heroId, imageElement, manifest);
 *   app.anim.setState(heroId, 'attack');
 *   app.anim.update(heroId, dt);
 *   const frame = app.anim.getFrame(heroId); // { image, sx, sy, sw, sh, done }
 */
export class AnimationSystem {
  constructor() {
    this._sheets = new Map(); // heroId → { image, manifest }
    this._states = new Map(); // heroId → { name, elapsed }
  }

  /** Registra uno spritesheet per un hero. */
  register(heroId, image, manifest) {
    this._sheets.set(heroId, { image, manifest });
    this._states.set(heroId, { name: 'idle', elapsed: 0 });
  }

  hasSprite(heroId) { return this._sheets.has(heroId); }

  /** Forza una nuova animazione. Se già in corso, no-op. */
  setState(heroId, name) {
    const s = this._states.get(heroId);
    if (!s || s.name === name) return;
    s.name    = name;
    s.elapsed = 0;
  }

  /** Avanza il timer di animazione. */
  update(heroId, dt) {
    const s = this._states.get(heroId);
    if (s) s.elapsed += dt;
  }

  /** Restituisce { image, sx, sy, sw, sh, done } per il frame corrente, o null. */
  getFrame(heroId) {
    const entry = this._sheets.get(heroId);
    const state = this._states.get(heroId);
    if (!entry || !state) return null;

    const { image, manifest } = entry;
    const anim = manifest.animations[state.name] ?? manifest.animations['idle'];
    if (!anim) return null;

    const { row, frames, fps, loop } = anim;
    const { frameW, frameH } = manifest.meta;
    const totalTicks = Math.floor(state.elapsed * fps);
    const frameIdx   = loop ? totalTicks % frames : Math.min(frames - 1, totalTicks);
    const done       = !loop && totalTicks >= frames;

    return {
      image,
      sx: frameIdx * frameW,
      sy: row      * frameH,
      sw: frameW,
      sh: frameH,
      done,
    };
  }

  isDone(heroId) { return this.getFrame(heroId)?.done ?? false; }
  getState(heroId) { return this._states.get(heroId)?.name ?? 'idle'; }
}
