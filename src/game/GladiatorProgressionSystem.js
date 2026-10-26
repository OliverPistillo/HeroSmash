/**
 * Progressione delle scuole ispirata alle regole documentate della versione
 * classica (marzo 2024). Dati originali: 1/2/4 XP per carta comune/epica/
 * leggendaria e soglie 4/10/20/40.
 *
 * Modulo PURO: nessuna dipendenza da Canvas, DOM o GameData. I dati sono passati
 * esplicitamente per consentire test, simulatori e futuri engine adapter.
 *
 * Fonti: https://www.iyingdi.com/tz/post/5358014
 * Nota: non descrive necessariamente la versione S11 del 2026.
 */
export const CLASSIC_THRESHOLDS = Object.freeze([4, 10, 20, 40]);
export const CLASSIC_TALENT_LEVELS = Object.freeze([5, 10, 15]);
export const CLASSIC_ARTIFACT_ROUNDS = Object.freeze([3, 8, 13]);
export const CLASSIC_CREEP_ROUNDS = Object.freeze([5, 10, 15]);

const XP_BY_RARITY = Object.freeze({
  Normale: 1,
  Epica: 2,
  Leggendaria: 4,
  Normal: 1,
  Epic: 2,
  Legendary: 4
});

export class GladiatorProgressionSystem {
  /** XP guadagnata da UN livello della carta in ciascuno dei suoi rami. */
  static cardXp(card) {
    const xp = XP_BY_RARITY[card?.rarity];
    if (xp !== undefined) return xp;
    const fallback = Number(card?.points);
    return Number.isFinite(fallback) && fallback > 0 ? fallback : 1;
  }

  static points(state, branchId, cards = []) {
    let total = 0;
    for (const card of cards) {
      if (!Array.isArray(card.branches) || !card.branches.includes(branchId)) continue;
      const levels = Math.max(0, Math.floor(Number(state?.cardLevels?.[card.id]) || 0));
      total += levels * GladiatorProgressionSystem.cardXp(card);
    }
    return total;
  }

  /** I livelli di scuola sono 0,1,2,3,4: NON il tier UI legacy 1..5. */
  static branchLevel(xp, thresholds = CLASSIC_THRESHOLDS) {
    const n = Number(xp) || 0;
    return thresholds.reduce((level, threshold) => level + (n >= threshold ? 1 : 0), 0);
  }

  /** Somma dei livelli di tutte le scuole ATTIVE, non numero di carte. */
  static heroLevel(state, cards = [], thresholds = CLASSIC_THRESHOLDS) {
    const branches = new Set(state?.activeBranches || []);
    let total = 0;
    for (const branchId of branches) {
      const points = GladiatorProgressionSystem.points(state, branchId, cards);
      total += GladiatorProgressionSystem.branchLevel(points, thresholds);
    }
    return total;
  }

  /** Soglie disponibili; la scelta di talento è un sistema separato. */
  static unlockedTalentMilestones(state, cards = []) {
    const level = GladiatorProgressionSystem.heroLevel(state, cards);
    return CLASSIC_TALENT_LEVELS.filter(milestone => level >= milestone);
  }

  static rewardTypeAtRound(round) {
    if (CLASSIC_ARTIFACT_ROUNDS.includes(round)) return "artifact";
    if (CLASSIC_CREEP_ROUNDS.includes(round)) return "creep_equipment";
    return null;
  }

  static snapshot(state, cards = [], thresholds = CLASSIC_THRESHOLDS) {
    const branches = [...new Set(state?.activeBranches || [])].map(id => {
      const xp = GladiatorProgressionSystem.points(state, id, cards);
      const level = GladiatorProgressionSystem.branchLevel(xp, thresholds);
      return {
        id, xp, level,
        nextThreshold: thresholds.find(t => t > xp) ?? null,
        epicUnlocked: level >= 2,
        legendaryUnlocked: level >= 3
      };
    });
    const heroLevel = branches.reduce((sum, b) => sum + b.level, 0);
    return {
      heroLevel, branches,
      unlockedTalentMilestones: CLASSIC_TALENT_LEVELS.filter(level => level <= heroLevel),
      nextTalentMilestone: CLASSIC_TALENT_LEVELS.find(level => level > heroLevel) ?? null
    };
  }
}
