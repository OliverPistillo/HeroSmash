import { LeagueSystem } from "./LeagueSystem.js";

export class RunSystem {
  static isOver(state) {
    return state.life <= 0 || state.round >= state.maxRound || LeagueSystem.aliveCount(state) <= 1;
  }

  static advanceRound(state) { state.round += 1; state.startPreparation?.(); }
}
