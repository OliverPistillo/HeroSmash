import { BRANCHES, CARDS, ECONOMY } from "./GameState.js";

export class BranchSystem {
  static thresholds() { return ECONOMY.branch_thresholds || [4, 10, 20, 40]; }

  static points(state, branchId) {
    let total = 0;
    for (const card of CARDS) {
      const level = state.cardLevels?.[card.id] || 0;
      if (level && card.branches.includes(branchId)) total += level * card.points;
    }
    return total;
  }

  static tier(points) {
    if (points >= 40) return 5;
    if (points >= 20) return 4;
    if (points >= 10) return 3;
    if (points >= 4)  return 2;
    return 1;
  }

  static nextThreshold(points) { return BranchSystem.thresholds().find(t => t > points) || 40; }
  static activeBranchObjects(state) { return BRANCHES.filter(b => state.activeBranches.includes(b.id)); }
  static branchById(id) { return BRANCHES.find(b => b.id === id); }

  static effects(state) {
    const out = {};
    const add = (k, v) => out[k] = (out[k] || 0) + v;

    // ── Card-level effects (accumulated by card level) ──────────────────────
    for (const card of CARDS) {
      const l = state.cardLevels?.[card.id] || 0;
      if (!l) continue;
      for (const [k, v] of Object.entries(card.effects || {})) add(k, v * l);
    }

    // ── Branch tier bonuses ─────────────────────────────────────────────────
    for (const branch of state.activeBranches || []) {
      const t = BranchSystem.tier(BranchSystem.points(state, branch));
      if (t < 2) continue;
      const scale = [0, 0, .5, 1, 1.7, 2.8][t];

      if (branch === "wound")    { add("woundAmp", .04 * scale); add("woundHit", .06 * scale); }
      if (branch === "essence")  { add("manaRegen", 1.5 * scale); add("skillPower", .05 * scale); }
      if (branch === "rage")     { add("speedPct", .05 * scale); }
      if (branch === "ice")      { add("slow", .06 * scale); add("stunHit", .02 * scale); add("iceHit", .04 * scale); }
      if (branch === "toxin")    { add("toxinHit", .08 * scale); add("toxinBoost", .08 * scale); }
      if (branch === "shield")   { add("startShield", 60 * scale); add("shieldReduction", .02 * scale); add("shieldRegen", 5 * scale); }
      if (branch === "healing")  { add("hpRegen", 3 * scale); add("healBoost", .04 * scale); }
      if (branch === "power")    { add("powerDamage", 8 * scale); add("execute", .05 * scale); }
      if (branch === "precision"){ add("crit", .03 * scale); add("critD", .08 * scale); }
      if (branch === "guardian") { add("hp", 80 * scale); add("armor", 2 * scale); }
      if (branch === "assault")  { add("attack", 6 * scale); add("multiHit", .02 * scale); }
      if (branch === "dodge")    { add("dodge", .025 * scale); }
    }
    return out;
  }
}
