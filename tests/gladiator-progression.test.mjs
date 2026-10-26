import test from "node:test";
import assert from "node:assert/strict";
import { GladiatorProgressionSystem as P } from "../src/game/GladiatorProgressionSystem.js";

const cards=[
  {id:"n",rarity:"Normale",branches:["rage"],points:1},
  {id:"e",rarity:"Epica",branches:["rage","ice"],points:2},
  {id:"l",rarity:"Leggendaria",branches:["rage"],points:3},
  {id:"i",rarity:"Normale",branches:["ice"],points:1}
];
test("XP classica: Normale 1, Epica 2, Leggendaria 4, anche con points legacy 3",()=>{
  assert.equal(P.cardXp(cards[0]),1);
  assert.equal(P.cardXp(cards[1]),2);
  assert.equal(P.cardXp(cards[2]),4);
});
test("Soglie 4/10/20/40: progressione 0..4",()=>{
  for(const [xp,expected] of [[0,0],[3,0],[4,1],[9,1],[10,2],[19,2],[20,3],[39,3],[40,4]]){
    assert.equal(P.branchLevel(xp),expected);
  }
});
test("Hero level somma livelli scuola, non carte; carta bi-ramo dà XP a entrambe",()=>{
  const state={activeBranches:["rage","ice"],cardLevels:{n:2,e:2,l:1,i:2}};
  assert.equal(P.points(state,"rage",cards),10);
  assert.equal(P.points(state,"ice",cards),6);
  assert.equal(P.heroLevel(state,cards),3);
  assert.deepEqual(P.snapshot(state,cards).unlockedTalentMilestones,[]);
});
test("Livelli e talent milestones",()=>{
  const state={activeBranches:["rage","ice"],cardLevels:{n:30,e:10,l:1,i:35}};
  assert.equal(P.heroLevel(state,cards),8);
  assert.deepEqual(P.unlockedTalentMilestones(state,cards),[5]);
});
test("Ricompense round versione classica",()=>{
  assert.equal(P.rewardTypeAtRound(3),"artifact");
  assert.equal(P.rewardTypeAtRound(5),"creep_equipment");
  assert.equal(P.rewardTypeAtRound(12),null);
});
