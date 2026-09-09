// Uses unmodified ES modules. Run with --experimental-default-type=module on Node 20.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const arg = name => { const i = process.argv.indexOf(name); return i < 0 ? null : process.argv[i + 1]; };
const root = path.resolve(repo, arg('--root') ?? 'legacy/web-prototype');
globalThis.fetch = async name => {
  const text = await fs.readFile(path.join(root, String(name)), 'utf8');
  return { ok: true, json: async () => JSON.parse(text) };
};
const imp = name => import(pathToFileURL(path.join(root, 'src', name)).href);
const { loadGameData } = await imp('game/GameData.js');
await loadGameData();
const { GameState, CARDS, BRANCHES } = await imp('game/GameState.js');
const { CardSystem } = await imp('game/CardSystem.js');
const { BranchSystem } = await imp('game/BranchSystem.js');
const { EconomySystem } = await imp('game/EconomySystem.js');
const { LeagueSystem } = await imp('game/LeagueSystem.js');
const { CombatSystem } = await imp('game/CombatSystem.js');
const { RunSystem } = await imp('game/RunSystem.js');
const { SaveSystem } = await imp('engine/SaveSystem.js');
const memory = new Map();
globalThis.localStorage = {getItem: k => memory.get(k) ?? null, setItem: (k,v) => memory.set(k,v), removeItem: k => memory.delete(k)};
memory.set('hs_custom_v07', '{"runs":7}');
const save = new SaveSystem();
assert.equal(save.load().runs, 7);
assert.equal(memory.get('hs_custom_v17'), '{"runs":7}');
memory.set('hs_custom_v17', 'invalid JSON');
assert.deepEqual(save.load({runs: 0}), {runs: 0});
save.reset();
assert.equal(memory.size, 0);
assert.equal(CARDS.length, 150);
assert.equal(BRANCHES.length, 12);
assert.deepEqual([0,3,4,9,10,19,20,39,40].map(BranchSystem.tier), [1,1,2,2,3,3,4,4,5]);

function rngFor(seed) {
  let a = seed >>> 0;
  return () => { a += 0x6D2B79F5; let t=a; t=Math.imul(t^t>>>15,t|1); t^=t+Math.imul(t^t>>>7,t|61); return ((t^t>>>14)>>>0)/4294967296; };
}
function run(seed) {
  const rng = rngFor(seed), state = new GameState({load: x=>x, save: ()=>{}});
  state.beginHeroDraft(rng);
  assert.equal(new Set(state.activeBranches).size, 8);
  assert.equal(state.bannedBranches().length, 4);
  assert.equal(new Set(state.heroDraft.choices).size, 3);
  const initialDraft = structuredClone(state.heroDraft);
  assert.equal(state.rerollHeroSlot(0, rng), true);
  assert.equal(state.rerollHeroSlot(1, rng), true);
  assert.equal(state.rerollHeroSlot(2, rng), false);
  state.startRun(state.heroDraft.choices[0], rng);
  assert.equal(state.gold, 300); assert.equal(state.life, 100);
  const rounds = [];
  for (let round = 1; round <= 3; round++) {
    const shop = CardSystem.rollShop(state, rng).map(c=>c.id);
    assert.equal(new Set(shop).size, shop.length);
    for (const card of state.shop) assert(card.branches.every(b=>state.activeBranches.includes(b)));
    state.shopLocked = true;
    assert.deepEqual(CardSystem.rollShop(state, rng).map(c=>c.id), shop);
    const before = {gold:state.gold, levels:structuredClone(state.cardLevels), stats:structuredClone(state.stats)};
    assert(CardSystem.buy(state, shop[0]).ok);
    assert(CardSystem.undoLastPurchase(state).ok);
    assert.deepEqual({gold:state.gold, levels:state.cardLevels, stats:state.stats}, before);
    assert(CardSystem.randomBuy(state, rng).ok);
    assert(CardSystem.reroll(state, rng).ok);
    LeagueSystem.prepareRound(state, rng);
    assert.equal(state.league.players.length, 8);
    state.preGold = state.gold; state.startBattle();
    const combat = new CombatSystem(state, rng);
    let frames = 0;
    while (!combat.result && frames++ < 3000) combat.update(1/60);
    assert(combat.result, 'Combat must terminate within 50 seconds');
    const results = LeagueSystem.resolveRound(state, combat.result === 'win', combat.hpLost, rng);
    const snap = {round, shop, levels: structuredClone(state.cardLevels), frames,
      result:combat.result, hpLost:combat.hpLost, playerHp:combat.player.hp, enemyHp:combat.enemy.hp,
      recap:combat.recap, income:structuredClone(state.lastIncome), life:state.life, gold:state.gold,
      results, standings:LeagueSystem.standings(state).map(p=>({id:p.id,life:p.life,gold:p.gold,wins:p.stats.wins,losses:p.stats.losses}))};
    rounds.push(structuredClone(snap));
    RunSystem.advanceRound(state);
    assert.equal(state.marketTimer, 35); assert.equal(state.ui.cardsOpen, true);
  }
  return {seed, active:state.activeBranches, initialDraft, hero:state.hero.id, rounds};
}
const seeds = [1,7,42,150,115,116,2026,4294967295];
const runs = seeds.map(run);
assert.deepEqual(seeds.map(run), runs, 'Fixed seed and timestep gameplay must repeat');
const economics = [
  {preGold:0,gold:200,winStreak:0,lossStreak:0,won:true,hpLost:0},
  {preGold:9999,gold:0,winStreak:9,lossStreak:0,won:true,hpLost:0},
  {preGold:100,gold:0,winStreak:0,lossStreak:9,won:false,hpLost:100},
].map(s=>EconomySystem.income({...s}, s.won, s.hpLost));
assert.deepEqual(economics.map(x=>x.total), [370,550,550]);
const snapshot = {schema_version:1, baseline:'4ef9eeb503c3c1c69efa36b7b1a3ae5d23cc4816',
  timestep:1/60, excludes:'visual-only Math.random floaters; browser-dependent sort order is not a portable RNG contract', economics, runs};
const fixture = path.join(repo, 'tools/validation/fixtures/web_baseline.json');
if (process.argv.includes('--record')) {
  await fs.mkdir(path.dirname(fixture), {recursive:true});
  await fs.writeFile(fixture, JSON.stringify(snapshot,null,2)+'\n');
  console.log('RECORDED baseline: '+fixture);
} else {
  assert.deepEqual(snapshot, JSON.parse(await fs.readFile(fixture,'utf8')), 'Behavior changed from pre-migration oracle');
}
console.log('PASS: 8 seeds x 3 rounds, repeated; draft, 8/4, shop, lock, buy/undo, RNG, economy caps, league, combat, direct preparation, save fallback.');
