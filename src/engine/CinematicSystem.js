/**
 * CinematicSystem — macchina a stati per le fasi cinematiche del combat.
 *
 * Fasi:
 *   INTRO   (1.8s) — hero/enemy entrano dai bordi, combat in pausa
 *   FIGHT          — combat normale
 *   KO      (1.5s) — death animation, flash bianco, banner "KO"
 *   VICTORY (2.0s) — vincitore in loop victory, banner
 *   DONE           — attesa conferma / recap attivo
 */
export class CinematicSystem {
  static INTRO_DUR   = 1.8;
  static KO_DUR      = 1.5;
  static VICTORY_DUR = 2.0;

  constructor() {
    this.phase = 'INTRO';
    this.t     = 0;
  }

  update(dt) {
    this.t += dt;
    switch (this.phase) {
      case 'INTRO':
        if (this.t >= CinematicSystem.INTRO_DUR) { this.phase = 'FIGHT'; this.t = 0; }
        break;
      case 'KO':
        if (this.t >= CinematicSystem.KO_DUR) { this.phase = 'VICTORY'; this.t = 0; }
        break;
      case 'VICTORY':
        if (this.t >= CinematicSystem.VICTORY_DUR) { this.phase = 'DONE'; }
        break;
    }
  }

  /** Chiamato quando combat.result viene settato. */
  triggerKO() {
    if (this.phase === 'FIGHT') { this.phase = 'KO'; this.t = 0; }
  }

  isCombatPaused() { return this.phase === 'INTRO'; }
  isInIntro()      { return this.phase === 'INTRO'; }
  isInKO()         { return this.phase === 'KO'; }
  isInVictory()    { return this.phase === 'VICTORY' || this.phase === 'DONE'; }
  isDone()         { return this.phase === 'DONE'; }
  isFighting()     { return this.phase === 'FIGHT'; }

  /** Progresso 0→1 nella fase corrente. */
  get progress() {
    const dur = { INTRO: CinematicSystem.INTRO_DUR, KO: CinematicSystem.KO_DUR,
                  VICTORY: CinematicSystem.VICTORY_DUR }[this.phase] ?? 1;
    return Math.min(1, this.t / dur);
  }

  /**
   * Ritorna il nome dello stato animazione per una unità.
   * @param {object} unit       — oggetto fighter (hp, attackPulse, castPulse)
   * @param {string} result     — 'win'|'loss'|null
   * @param {boolean} isPlayer
   */
  getAnimState(unit, result, isPlayer) {
    const isWinner = result ? (isPlayer ? result === 'win' : result === 'loss') : false;

    switch (this.phase) {
      case 'INTRO':
        return 'intro';
      case 'FIGHT':
        if (unit.hp <= 0)                         return 'death';
        if ((unit.castPulse   || 0) > 0.55)       return 'skill';
        if ((unit.attackPulse || 0) > 0.55)       return 'attack';
        return 'idle';
      case 'KO':
        return isWinner ? 'idle' : 'death';
      case 'VICTORY':
      case 'DONE':
        return isWinner ? 'victory' : 'death';
      default:
        return 'idle';
    }
  }

  /**
   * X screen-coordinate durante l'intro (entrata dai bordi).
   * @param {boolean} isPlayer
   * @param {number}  targetX   — posizione finale del fighter
   * @param {number}  canvasW
   */
  introX(isPlayer, targetX, canvasW = 1366) {
    const ease = 1 - Math.pow(1 - this.progress, 3); // ease-out cubic
    if (isPlayer) {
      const startX = canvasW + 140;
      return startX + (targetX - startX) * ease;
    } else {
      const startX = -140;
      return startX + (targetX - startX) * ease;
    }
  }

  /** Alpha del flash bianco al momento del KO (0→1→0). */
  get koFlashAlpha() {
    if (this.phase !== 'KO') return 0;
    const p = this.t / CinematicSystem.KO_DUR;
    return Math.max(0, Math.sin(p * Math.PI) * 0.85);
  }
}
