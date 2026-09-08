import { HEROES, ECONOMY, heroFavoredBranches } from "./GameState.js";
import { CardSystem } from "./CardSystem.js";
import { BranchSystem } from "./BranchSystem.js";

const BOT_NAMES = ["Ash Bot", "Frost Bot", "Toxin Bot", "Shield Bot", "Rage Bot", "Wound Bot", "Void Bot"];

export class BotSystem {
  static names() { return BOT_NAMES; }

  static createBots(activeBranches, rng = Math.random, usedHeroId = null) {
    const active = new Set(activeBranches || []);
    const eligible = HEROES.filter(h => h.id !== usedHeroId && heroFavoredBranches(h).some(b => active.has(b)));
    const heroes = (eligible.length ? eligible : HEROES.filter(h => h.id !== usedHeroId)).sort(() => rng() - .5);
    return BOT_NAMES.map((name, i) => {
      const hero = heroes[i % heroes.length];
      return {
        id:`bot_${i+1}`,
        name,
        isHuman:false,
        heroId:hero.id,
        hero,
        life:ECONOMY.starting_player_hp ?? 100,
        gold:ECONOMY.starting_coins ?? 300,
        preGold:ECONOMY.starting_coins ?? 300,
        activeBranches:[...activeBranches],
        cardLevels:{},
        shop:[],
        shopLocked:false,
        purchaseHistory:[],
        sellHistory:[],
        winStreak:0,
        lossStreak:0,
        eliminated:false,
        lastResult:"—",
        lastOpponent:"—",
        lastHpLost:0,
        stats:{ wins:0, losses:0, damage:0, taken:0, healing:0, bought:0, sold:0, hpLost:0, spent:0, refunded:0 }
      };
    });
  }

  static prepBot(bot, rng = Math.random) {
    if (bot.eliminated) return;
    bot.preGold = bot.gold;
    // Bots prefer their hero branch, then nearby thresholds, otherwise random weighted cards.
    for (let attempt = 0; attempt < 5; attempt++) {
      const pool = CardSystem.pool(bot);
      if (!pool.length) break;
      const favorites = heroFavoredBranches(bot.hero);
      const preferred = pool.filter(c => c.branches.some(b => favorites.includes(b)));
      const near = pool.filter(c => c.branches.some(b => {
        const pts = BranchSystem.points(bot, b);
        const next = BranchSystem.nextThreshold(pts);
        return next - pts <= c.points;
      }));
      let choicePool = near.length && rng() < .65 ? near : preferred.length && rng() < .72 ? preferred : pool;
      choicePool = choicePool.filter(c => bot.gold >= c.cost);
      if (!choicePool.length) break;
      const card = choicePool[Math.floor(rng() * choicePool.length)];
      CardSystem.buy(bot, card.id, "bot");
      if (bot.gold < 100) break;
    }
  }

  static powerScore(player, round = 1) {
    const h = player.hero;
    const e = BranchSystem.effects(player);
    let score = h.stats.hp * .018 + h.stats.atk * 2.5 + h.stats.focus * 1.8 + h.stats.arm * 8 + h.stats.spd * 42 + h.stats.crit * 160 + h.stats.dodge * 120;
    for (const [k,v] of Object.entries(e)) {
      if (typeof v !== "number") continue;
      if (["hp","startShield"].includes(k)) score += v * .025;
      else if (["attack","focus","armor"].includes(k)) score += v * 4;
      else if (k.includes("Hit") || k.includes("crit") || k.includes("dodge") || k.includes("Boost") || k.includes("Power") || k.includes("Pct")) score += v * 120;
      else score += v * 1.5;
    }
    score += Object.values(player.cardLevels).reduce((a,b)=>a+b,0) * 18;
    score += round * 5;
    return score;
  }
}
