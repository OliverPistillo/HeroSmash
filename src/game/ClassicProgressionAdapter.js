import { GladiatorProgressionSystem as P } from "./GladiatorProgressionSystem.js";
import { CARDS } from "./GameState.js";

/** Adattatore runtime: la progressione classica è opt-in per evitare regressioni. */
export function classicProgressionSnapshot(state) {
  return P.snapshot(state, CARDS);
}
