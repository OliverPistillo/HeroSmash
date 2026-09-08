// Execute preserved JS modules read-only. These tests identify divergence, not canonical rules.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const legacy = path.join(root, 'legacy/web-prototype');
globalThis.fetch = async p => ({ok:true, json:async()=>JSON.parse(await fs.readFile(path.join(legacy,p),'utf8'))});
const data = await import(pathToFileURL(path.join(legacy,'src/game/GameData.js')));
await data.loadGameData();
const {CombatSystem} = await import(pathToFileURL(path.join(legacy,'src/game/CombatSystem.js')));
const {BranchSystem} = await import(pathToFileURL(path.join(legacy,'src/game/BranchSystem.js')));
const {CardSystem} = await import(pathToFileURL(path.join(legacy,'src/game/CardSystem.js')));
const levels = JSON.parse(await fs.readFile(path.join(root,'game/data/generated/v1_17/card_levels.json'),'utf8'));
let assertions = 0;
function eq(a,b) { assert.deepEqual(a,b); assertions++; }
function near(a,b) { assert.ok(Math.abs(a-b)<1e-9, `${a} != ${b}`); assertions++; }
for (const row of levels.records) {
  const card = data.CARDS.find(c=>c.legacyId===Number(row.cardId.slice(7)));
  assert.ok(card);
  const state = {cardLevels:{[card.id]:row.level}, activeBranches:[],gold:100000, stats:{spent:0,bought:0},purchaseHistory:[]};
  const effects = BranchSystem.effects(state);
  eq(Object.keys(effects).sort(),Object.keys(row.legacyOracleValues).sort());
  for (const key of Object.keys(effects)) near(effects[key],row.legacyOracleValues[key]);
  const buy = CardSystem.buy(state,card.id);
  eq(buy.ok,row.level<card.max);
  eq(state.cardLevels[card.id],Math.min(card.max,row.level+1));
}
const effectsOriginal = BranchSystem.effects;
let fixtureEffects = {};
BranchSystem.effects = ()=>fixtureEffects; // in-memory operator isolation; no files edited
const hero = data.HEROES[0];
function combat() {
  fixtureEffects = {};
  const state = {hero, cardLevels:{}, activeBranches:[], currentOpponent:{hero,name:'BOT',cardLevels:{}},round:1};
  const c = new CombatSystem(state,()=>0.99);
  for (const a of [c.player,c.enemy]) {a.crit=0;a.dodge=0;a.basic=99;a.skillCd=99;a.hp=500;}
  return c;
}
const observations = {};
let c = combat();
fixtureEffects={hpRegen:10};
c.act(c.player,c.enemy,1,true); c.act(c.enemy,c.player,1,false);
eq([c.player.hp,c.enemy.hp],[510,500]); observations.player_only_regen=[510,500];
c=combat(); fixtureEffects={healBoost:0.5};
c.heal(c.player,10); c.heal(c.enemy,10);
eq([c.player.hp,c.enemy.hp],[515,510]); observations.player_only_heal_boost=[515,510];
c=combat(); fixtureEffects={dodgeReflect:0.5}; c.rng=()=>0;
c.player.dodge=1; c.enemy.dodge=1;
c.take(c.player,20,c.enemy,false,'phys'); c.take(c.enemy,20,c.player,true,'phys');
eq([c.player.hp,c.enemy.hp],[500,490]); observations.player_only_half_reflection=[500,490];
c=combat(); c.player.openingCritsLeft=1;c.enemy.openingCritsLeft=1;
eq([c.damage(c.player,c.enemy,20,'phys',true).crit,c.damage(c.enemy,c.player,20,'phys',false).crit],[true,false]);
observations.player_only_opening_crit=true;
c=combat(); fixtureEffects={toxinHit:1,toxinTick:6};c.rng=()=>0.5;
c.basic(c.player,c.enemy,true);c.basic(c.enemy,c.player,false);
eq([c.player.status.length,c.enemy.status.length],[0,1]); observations.player_only_onhit=true;
c=combat();fixtureEffects={skillPower:1};
const plain={...hero.skill,status:null};
c.skill(c.player,c.enemy,plain,true);c.skill(c.enemy,c.player,plain,false);
assert.ok(c.enemy.taken>c.player.taken);assertions++;observations.player_only_skill_power=true;
c=combat(); c.player.status=[{type:'shield',val:5,dur:3},{type:'shield',val:3,dur:3}];
eq(c.take(c.player,10,c.enemy,false,'magic'),5);eq(c.player.status[1].val,3);
observations.first_shield_only={hpLoss:5,unusedSecondShield:3};
c=combat();c.player.arm=6;c.player.status=[{type:'wound',amp:0.05,stacks:1,dur:3}];
near(c.damage(c.enemy,c.player,20,'phys',false).amount,14.7);
observations.armor_before_wound=14.7;
c=combat();c.player.status=[{type:'wound',amp:0.05,stacks:1,dur:3},{type:'toxin',tick:14,stacks:1,dur:3}];
c.tickStatus(c.player,1);eq(c.player.hp,486);observations.dot_bypasses_wound={hpLoss:14,source:null};
c=combat();c.player.deathShieldCharges=1;c.take(c.player,1000,c.enemy,false,'magic');
eq(c.player.hp,1);eq(c.player.status[0].val,Math.round(c.player.max*0.35));eq(c.player.status[0].dur,3);
observations.last_stand_approximation={survivingHp:1,shield:c.player.status[0].val,duration:3};
c=combat();c.player.hp=1;eq(c.take(c.player,100,c.enemy,false,'magic'),100);
observations.overkill_reported_as_actual=true;
c=combat();c.player.dodge=1;c.rng=()=>0;
c.skill(c.enemy,c.player,{...hero.skill,type:'phys',status:'burn'},false);
eq(c.player.status[0].type,'burn');observations.skill_status_even_when_dodged=true;
BranchSystem.effects=effectsOriginal;
console.log(JSON.stringify({status:'pass',assertions,levelRecords:levels.records.length,classification:'legacy divergence / approximation, not canonical parity',observations}));
