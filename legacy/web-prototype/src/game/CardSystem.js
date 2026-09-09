import { CARDS, ECONOMY } from "./GameState.js";
import { BranchSystem } from "./BranchSystem.js";

export class CardSystem {
  static pool(state) {
    return CARDS.filter(card => {
      if (!card.branches.every(b => state.activeBranches.includes(b))) return false;
      if ((state.cardLevels[card.id] || 0) >= card.max) return false;
      return card.branches.some(b => BranchSystem.points(state, b) >= card.unlock);
    });
  }

  static weightedBag(state) {
    const pool = CardSystem.pool(state);
    const bag = [];
    for (const card of pool) for (let i=0;i<card.weight;i++) bag.push(card);
    return { pool, bag };
  }

  static rollShop(state, rng = Math.random, count = 4, force = false) {
    if (state.shopLocked && state.shop?.length && !force) return state.shop;
    const { pool, bag } = CardSystem.weightedBag(state);
    const result = [];
    const used = new Set();
    while (result.length < count && used.size < pool.length && bag.length) {
      const c = bag[Math.floor(rng() * bag.length)];
      if (!used.has(c.id)) { used.add(c.id); result.push(c); }
    }
    state.shop = result;
    state.shopLocked = false;
    return result;
  }

  static reroll(state, rng = Math.random, count = 4) {
    if (state.gold < ECONOMY.reroll_cost) return { ok:false, reason:"Coins insufficienti" };
    state.gold -= ECONOMY.reroll_cost;
    state.stats.spent += ECONOMY.reroll_cost;
    state.shopLocked = false;
    CardSystem.rollShop(state, rng, count, true);
    return { ok:true };
  }

  static buy(state, cardId, source = "shop") {
    const card = CARDS.find(c => c.id === cardId);
    if (!card) return { ok:false, reason:"Card inesistente" };
    const level = state.cardLevels[cardId] || 0;
    if (level >= card.max) return { ok:false, reason:"Card al massimo" };
    if (state.gold < card.cost) return { ok:false, reason:"Coins insufficienti" };
    const before = CardSystem.previewBranches(state, card);
    state.gold -= card.cost;
    state.stats.spent += card.cost;
    state.cardLevels[cardId] = level + 1;
    state.stats.bought += 1;
    state.purchaseHistory.push({ type:"buy", source, cardId, cost:card.cost, previousLevel:level, nextLevel:level+1, before, after:CardSystem.previewBranches(state, card, 0) });
    if (state.purchaseHistory.length > 20) state.purchaseHistory.shift();
    return { ok:true, card };
  }

  static addFree(state, cardId) {
    const card = CARDS.find(c => c.id === cardId);
    if (!card) return { ok:false, reason:"Card inesistente" };
    const level = state.cardLevels[cardId] || 0;
    if (level >= card.max) return { ok:false, reason:"Card al massimo" };
    state.cardLevels[cardId] = level + 1;
    state.stats.bought += 1;
    return { ok:true, card };
  }

  static randomBuy(state, rng = Math.random, cost = ECONOMY.random_card_cost) {
    if (state.gold < cost) return { ok:false, reason:"Coins insufficienti" };
    const pool = CardSystem.pool(state);
    if (!pool.length) return { ok:false, reason:"Pool vuoto" };
    const card = pool[Math.floor(rng() * pool.length)];
    const level = state.cardLevels[card.id] || 0;
    if (level >= card.max) return { ok:false, reason:"Card al massimo" };
    const before = CardSystem.previewBranches(state, card);
    state.gold -= cost;
    state.stats.spent += cost;
    state.cardLevels[card.id] = level + 1;
    state.stats.bought += 1;
    state.purchaseHistory.push({ type:"random", source:"random", cardId:card.id, cost, previousLevel:level, nextLevel:level+1, before, after:CardSystem.previewBranches(state, card, 0) });
    if (state.purchaseHistory.length > 20) state.purchaseHistory.shift();
    return { ok:true, card };
  }

  static undoLastPurchase(state) {
    const tx = state.purchaseHistory.pop();
    if (!tx) return { ok:false, reason:"Nessun acquisto da annullare" };
    const card = CARDS.find(c => c.id === tx.cardId);
    if (!card) return { ok:false, reason:"Card non trovata" };
    state.cardLevels[tx.cardId] = tx.previousLevel;
    if (state.cardLevels[tx.cardId] <= 0) delete state.cardLevels[tx.cardId];
    state.gold += tx.cost;
    state.stats.bought = Math.max(0, state.stats.bought - 1);
    state.stats.spent = Math.max(0, state.stats.spent - tx.cost);
    return { ok:true, card, refunded:tx.cost };
  }

  static sell(state, cardId) {
    const card = CARDS.find(c => c.id === cardId);
    if (!card) return { ok:false, reason:"Card inesistente" };
    const level = state.cardLevels[cardId] || 0;
    if (level <= 0) return { ok:false, reason:"Non possiedi questa carta" };
    const refund = Math.floor(card.cost * 0.5);
    state.cardLevels[cardId] = level - 1;
    if (state.cardLevels[cardId] <= 0) delete state.cardLevels[cardId];
    state.gold += refund;
    state.stats.sold += 1;
    state.stats.refunded += refund;
    state.sellHistory.push({ cardId, refund, previousLevel:level, nextLevel:level-1 });
    if (state.sellHistory.length > 20) state.sellHistory.shift();
    return { ok:true, card, refund };
  }

  static previewBranches(state, card, deltaLevels = 1) {
    return card.branches.map(branchId => {
      const before = BranchSystem.points(state, branchId);
      const after = before + card.points * deltaLevels;
      const beforeTier = BranchSystem.tier(before);
      const afterTier = BranchSystem.tier(after);
      return { branchId, before, after, beforeTier, afterTier, next:BranchSystem.nextThreshold(after), crossed:afterTier > beforeTier };
    });
  }

  static probabilityInfo(state, card) {
    const { bag } = CardSystem.weightedBag(state);
    if (!bag.length) return { perSlot:0, shopAtLeastOne:0 };
    const same = bag.filter(c => c.id === card.id).length;
    const perSlot = same / bag.length;
    return { perSlot, shopAtLeastOne:1 - Math.pow(1 - perSlot, 4) };
  }

  static ownedCards(state) { return CARDS.filter(c => (state.cardLevels[c.id] || 0) > 0); }
}
