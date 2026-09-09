import { BRANCHES, CARDS, HEROES, ENEMIES, ECONOMY, RUNTIME, requireGameData } from "./GameData.js";

function shuffleCopy(items, rng = Math.random) {
  return [...items].sort(() => rng() - 0.5);
}

function pickActiveBranches(rng = Math.random) {
  return shuffleCopy(BRANCHES, rng).slice(0, 8).map(b => b.id);
}

export function heroFavoredBranches(hero) {
  const raw = Array.isArray(hero?.favoredBranches)
    ? hero.favoredBranches
    : [hero?.favoredBranch].filter(Boolean);
  return [...new Set(raw.filter(Boolean))].slice(0, 2);
}

export class GameState {
  constructor(save) {
    requireGameData();
    this.save = save;
    this.profile = save.load({ runs: 0, bestRound: 0, bestWins: 0, totalCoins: 0 });
    this.reset();
  }

  reset() {
    this.hero = null;
    this.round = 1;
    this.maxRound = 12;
    this.life = ECONOMY.starting_player_hp ?? 100;
    this.gold = ECONOMY.starting_coins ?? 300;
    this.preGold = this.gold;
    this.activeBranches = [];
    this.cardLevels = {};
    this.shop = [];
    this.shopLocked = false;
    this.marketTimer = 35;
    this.prepTimerMax = 35;
    this.purchaseHistory = [];
    this.sellHistory = [];
    this.winStreak = 0;
    this.lossStreak = 0;
    this.lastIncome = null;
    this.stats = { wins:0, losses:0, damage:0, taken:0, healing:0, bought:0, sold:0, hpLost:0, spent:0, refunded:0 };

    this.league = null;
    this.currentOpponent = null;
    this.currentPairings = [];
    this.roundResults = [];
    this.lastRoundRecap = null;
    this.roundPrepared = false;
    this.heroDraft = { choices: [], rerollsLeft: 2 };
    this.ui = { cardsOpen: true, collectionOpen: false };
  }

  beginHeroDraft(rng = Math.random) {
    this.reset();
    this.activeBranches = pickActiveBranches(rng);
    this.rollHeroDraft(rng);
  }

  bannedBranches() {
    const active = new Set(this.activeBranches || []);
    return BRANCHES.filter(b => !active.has(b.id)).map(b => b.id);
  }

  eligibleHeroes() {
    const active = new Set(this.activeBranches || []);
    const eligible = HEROES.filter(h => heroFavoredBranches(h).some(b => active.has(b)));
    return eligible.length ? eligible : HEROES;
  }

  rollHeroDraft(rng = Math.random, count = 3) {
    const pool = shuffleCopy(this.eligibleHeroes(), rng);
    this.heroDraft = {
      choices: pool.slice(0, Math.min(count, pool.length)).map(h => h.id),
      rerollsLeft: 2
    };
    return this.heroDraft.choices;
  }

  rerollHeroSlot(slotIndex, rng = Math.random) {
    if (!this.heroDraft || this.heroDraft.rerollsLeft <= 0) return false;
    if (slotIndex < 0 || slotIndex >= this.heroDraft.choices.length) return false;

    const current = new Set(this.heroDraft.choices);
    const pool = shuffleCopy(this.eligibleHeroes(), rng).filter(h => !current.has(h.id));
    if (!pool.length) return false;

    this.heroDraft.choices[slotIndex] = pool[0].id;
    this.heroDraft.rerollsLeft -= 1;
    return true;
  }

  startRun(heroId, rng = Math.random) {
    if (!this.activeBranches?.length) this.activeBranches = pickActiveBranches(rng);
    this.hero = HEROES.find(h => h.id === heroId);
    this.heroDraft = { choices: [], rerollsLeft: 0 };
    this.ui = { cardsOpen: true, collectionOpen: false };
    this.startPreparation();
  }

  startPreparation() {
    this.marketTimer = this.prepTimerMax;
    this.roundPrepared = false;
    this.ui = { ...(this.ui || {}), cardsOpen: true, collectionOpen: false };
  }

  startBattle() {
    this.ui = { ...(this.ui || {}), cardsOpen: false, collectionOpen: false };
  }

  finishRun() {
    this.profile.runs += 1;
    this.profile.bestRound = Math.max(this.profile.bestRound, this.round);
    this.profile.bestWins = Math.max(this.profile.bestWins, this.stats.wins);
    this.profile.totalCoins += this.gold;
    this.save.save(this.profile);
  }
}

export { BRANCHES, CARDS, HEROES, ENEMIES, ECONOMY, RUNTIME };
