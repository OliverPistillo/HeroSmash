import { ECONOMY } from "./GameState.js";

export class EconomySystem {
  static lifeDamage(state, enemyLevel) {
    const streak = state.winStreak;
    let base = 3;
    if (streak >= 2 && streak <= 3) base = 5;
    if (streak >= 4 && streak <= 5) base = 10;
    if (streak >= 6 && streak <= 7) base = 16;
    if (streak >= 8) base = 20;
    return base + Math.ceil(enemyLevel / 2);
  }

  static income(state, won, hpLost = 0) {
    const interest = Math.min(ECONOMY.interest_cap, Math.floor((state.preGold || state.gold || 0) / 100) * ECONOMY.interest_per_100);
    const win = won ? ECONOMY.win_reward : 0;
    const winStreak = won ? Math.min(ECONOMY.win_streak_cap, state.winStreak * ECONOMY.win_streak_per_win) : 0;
    const loss = !won ? Math.min(180, hpLost * ECONOMY.loss_hp_compensation) : 0;
    const loseStreak = !won ? Math.min(ECONOMY.lose_streak_cap, state.lossStreak * ECONOMY.lose_streak_per_loss) : 0;
    const total = ECONOMY.base_income + interest + win + winStreak + loss + loseStreak;
    state.gold += total;
    state.lastIncome = { base: ECONOMY.base_income, interest, win, winStreak, loss, loseStreak, total, won };
    return state.lastIncome;
  }
}
