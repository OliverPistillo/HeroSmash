import { HEROES } from "./GameState.js";
import { BotSystem } from "./BotSystem.js";
import { EconomySystem } from "./EconomySystem.js";
import { CardSystem } from "./CardSystem.js";

function clone(obj) { return JSON.parse(JSON.stringify(obj)); }
function shuffle(arr, rng) { return [...arr].sort(() => rng() - .5); }

export class LeagueSystem {
  static ensure(state, rng = Math.random) {
    if (state.league) return;
    const human = {
      id:"you",
      name:"Tu",
      isHuman:true,
      heroId:state.hero.id,
      hero:state.hero,
      life:state.life,
      gold:state.gold,
      preGold:state.preGold,
      activeBranches:state.activeBranches,
      cardLevels:state.cardLevels,
      shop:state.shop,
      shopLocked:state.shopLocked,
      purchaseHistory:state.purchaseHistory,
      sellHistory:state.sellHistory,
      winStreak:state.winStreak,
      lossStreak:state.lossStreak,
      eliminated:false,
      lastResult:"—",
      lastOpponent:"—",
      lastHpLost:0,
      stats:state.stats
    };
    const bots = BotSystem.createBots(state.activeBranches, rng, state.hero.id);
    state.league = { players:[human, ...bots], pairings:[], history:[] };
  }

  static syncHumanToLeague(state) {
    if (!state.league) return;
    const p = state.league.players.find(x => x.id === "you");
    if (!p) return;
    p.hero = state.hero; p.heroId = state.hero.id; p.life = state.life; p.gold = state.gold; p.preGold = state.preGold;
    p.activeBranches = state.activeBranches; p.cardLevels = state.cardLevels; p.shop = state.shop; p.shopLocked = state.shopLocked;
    p.purchaseHistory = state.purchaseHistory; p.sellHistory = state.sellHistory; p.winStreak = state.winStreak; p.lossStreak = state.lossStreak; p.stats = state.stats;
    p.eliminated = state.life <= 0;
  }

  static syncLeagueToHuman(state) {
    const p = state.league?.players.find(x => x.id === "you");
    if (!p) return;
    state.life = p.life; state.gold = p.gold; state.preGold = p.preGold; state.cardLevels = p.cardLevels; state.shop = p.shop;
    state.shopLocked = p.shopLocked; state.purchaseHistory = p.purchaseHistory; state.sellHistory = p.sellHistory;
    state.winStreak = p.winStreak; state.lossStreak = p.lossStreak; state.stats = p.stats;
  }

  static prepareRound(state, rng = Math.random) {
    LeagueSystem.ensure(state, rng);
    LeagueSystem.syncHumanToLeague(state);
    for (const bot of state.league.players.filter(p => !p.isHuman)) BotSystem.prepBot(bot, rng);

    const alive = state.league.players.filter(p => !p.eliminated && p.life > 0);
    let pool = shuffle(alive, rng);
    const human = pool.find(p => p.id === "you");
    const pairings = [];

    if (human) {
      pool = pool.filter(p => p.id !== "you");
      const opponent = pool.shift() || state.league.players.filter(p => p.id !== "you")[0];
      pairings.push({ a:human.id, b:opponent.id, hasHuman:true });
      state.currentOpponent = opponent;
    } else {
      state.currentOpponent = null;
    }

    while (pool.length >= 2) {
      const a = pool.shift(), b = pool.shift();
      pairings.push({ a:a.id, b:b.id, hasHuman:false });
    }
    if (pool.length === 1) pairings.push({ a:pool[0].id, b:null, bye:true, hasHuman:false });

    state.league.pairings = pairings;
    state.currentPairings = pairings;
    state.roundPrepared = true;
    return pairings;
  }

  static player(state, id) { return state.league?.players.find(p => p.id === id); }

  static simpleLifeDamage(winner, loser, round = 1) {
    const streak = winner?.winStreak || 0;
    let base = 3;
    if (streak >= 2 && streak <= 3) base = 5;
    if (streak >= 4 && streak <= 5) base = 10;
    if (streak >= 6 && streak <= 7) base = 16;
    if (streak >= 8) base = 20;
    return base + Math.ceil(round / 3);
  }

  static resolveBotMatch(state, a, b, rng = Math.random) {
    if (!a || !b || a.eliminated || b.eliminated) return null;
    const pa = BotSystem.powerScore(a, state.round) * (0.86 + rng() * 0.28);
    const pb = BotSystem.powerScore(b, state.round) * (0.86 + rng() * 0.28);
    const winner = pa >= pb ? a : b;
    const loser = winner === a ? b : a;
    const hpLost = LeagueSystem.simpleLifeDamage(winner, loser, state.round);

    winner.winStreak += 1; winner.lossStreak = 0; winner.stats.wins += 1; winner.lastResult = "W"; winner.lastOpponent = loser.name; winner.lastHpLost = 0;
    loser.lossStreak += 1; loser.winStreak = 0; loser.stats.losses += 1; loser.life = Math.max(0, loser.life - hpLost); loser.stats.hpLost += hpLost; loser.eliminated = loser.life <= 0; loser.lastResult = "L"; loser.lastOpponent = winner.name; loser.lastHpLost = hpLost;
    EconomySystem.income(winner, true, 0);
    EconomySystem.income(loser, false, hpLost);
    return { winner:winner.id, loser:loser.id, hpLost, text:`${winner.name} batte ${loser.name} (-${hpLost})` };
  }

  static resolveRound(state, humanWon, humanHpLost, rng = Math.random) {
    LeagueSystem.syncHumanToLeague(state);
    const human = LeagueSystem.player(state, "you");
    const opponent = state.currentOpponent;
    const results = [];

    if (human && opponent) {
      if (humanWon) {
        // Il CombatSystem ha già applicato win, streak e income al player.
        // Qui aggiorniamo solo il lato league dell'avversario sconfitto.
        const botLoss = Math.max(3, LeagueSystem.simpleLifeDamage(human, opponent, state.round));
        human.lastResult = "W";
        human.lastOpponent = opponent.name;
        human.lastHpLost = 0;
        human.eliminated = human.life <= 0;

        opponent.lastResult = "L";
        opponent.lastOpponent = human.name;
        opponent.lastHpLost = botLoss;
        opponent.lossStreak += 1;
        opponent.winStreak = 0;
        opponent.stats.losses += 1;
        opponent.life = Math.max(0, opponent.life - botLoss);
        opponent.stats.hpLost += botLoss;
        opponent.eliminated = opponent.life <= 0;
        EconomySystem.income(opponent, false, botLoss);

        results.push({ winner:human.id, loser:opponent.id, hpLost:botLoss, text:`Tu batti ${opponent.name} (-${botLoss})` });
      } else {
        // Il CombatSystem ha già applicato loss, HP loss e income al player.
        // Prima mancavano invece win, streak, stats e income del bot vincitore.
        human.lastResult = "L";
        human.lastOpponent = opponent.name;
        human.lastHpLost = humanHpLost;
        human.eliminated = human.life <= 0;

        opponent.lastResult = "W";
        opponent.lastOpponent = human.name;
        opponent.lastHpLost = 0;
        opponent.winStreak += 1;
        opponent.lossStreak = 0;
        opponent.stats.wins += 1;
        EconomySystem.income(opponent, true, 0);

        results.push({ winner:opponent.id, loser:human.id, hpLost:humanHpLost, text:`${opponent.name} batte te (-${humanHpLost})` });
      }
    }

    for (const pairing of state.league.pairings) {
      if (pairing.hasHuman || pairing.bye) continue;
      const a = LeagueSystem.player(state, pairing.a), b = LeagueSystem.player(state, pairing.b);
      const res = LeagueSystem.resolveBotMatch(state, a, b, rng);
      if (res) results.push(res);
    }

    state.roundResults = results;
    state.league.history.push({ round:state.round, results:clone(results) });
    LeagueSystem.syncLeagueToHuman(state);
    return results;
  }

  static standings(state) {
    if (!state.league) return [];
    return [...state.league.players].sort((a,b) => {
      if ((b.life > 0) !== (a.life > 0)) return (b.life > 0) - (a.life > 0);
      if (b.life !== a.life) return b.life - a.life;
      return (b.stats.wins || 0) - (a.stats.wins || 0);
    });
  }

  static aliveCount(state) { return state.league?.players.filter(p => !p.eliminated && p.life > 0).length || 1; }
}
