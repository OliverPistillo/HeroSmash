# v1.15 canonical source decision

Baseline: `4ef9eeb503c3c1c69efa36b7b1a3ae5d23cc4816`; paths below use the proposed isolated web root. No gameplay data is rewritten in v1.15. `PROJECT_MASTER.md` and `docs/product-specs/CANONICAL_DATA.md` govern these selections.

| Domain | Authoritative input now | Future target | Decision / conflicts |
|---|---|---|---|
| Branch identity | Master 12 names + `legacy/web-prototype/data/branches.json` IDs | `game/data/canonical/branches.json` in v1.16 | Preserve lowercase IDs and 8 active / 4 banned. Candidate hero aliases Arcane→Essence, Venom→Toxin, Frost→Ice; legacy card typo Guadian→Guardian. No other inferred aliases admitted. |
| Card identities and original metadata | `legacy/web-prototype/data/legacy_deck_source.json` | One canonical JSON with source provenance in v1.16 | 150 IDs 1–150; preserve names, text, costs, levels, rarity, membership and original asset paths. This is the committed imported deck mandated by Master. |
| Playable card approximation | `legacy/web-prototype/data/cards.json` + `src/game/BranchSystem.js`, `CombatSystem.js` | Separate semantics specification and handlers in v1.16/v1.17 | Runtime IDs `legacy_001`…`legacy_150`. Numeric effects are behavior-oracle values, not proof of exact text semantics. Do not rerun the old importer: it would replace later hand-adjusted effects. |
| Alternate card sources | `.work/legacy-source/vecchio/deck.json`, `cards.json`, `cards_updated.json` | Provenance/comparison only | All have 150 cards. deck differs from committed source in all 150 image paths only. The other two also differ in 24 level records. Retain all; imported deck wins without merging metadata. |
| Current heroes and enemies | `legacy/web-prototype/data/heroes.json`, `enemies.json` | Baseline simulation fixtures only | 16 runtime heroes are an oracle, not final roster approval. |
| Candidate hero direction | `.work/legacy-source/hero.json.txt` (`characters`, 20 records) | Candidate registry in v1.16; approval v1.18 | Preserve concept IDs/text and trace aliases; do not replace the 16 runtime heroes or create final characters. |
| Economy | `legacy/web-prototype/data/economy.json` and `src/game/EconomySystem.js`, `CardSystem.js`, `LeagueSystem.js` | `game/data/canonical/economy.json` + typed pure rules | Start 300 coins/100 HP; base income 300; reroll 20; random 100; interest 10/100 capped 100; win 50; streak caps 100/60; loss compensation capped 180 in code. No rebalance. |
| Timers and run length | `GameState.js`, `HeroSelectScene.js`, `CombatSystem.js` | Explicit versioned config after parity review | Draft 20s, preparation 35s, combat 45s; max round 12. These are in code, not economy JSON. |
| Arena definition | `legacy/web-prototype/data/arenas/*.json`, `src/arena/` | Authored 2.5D scene and camera specification | Beast Crucible composition is a reference. No automatic production-art approval. |
| UI / character references | Indexed paths in `docs/references/visual/reference_manifest.json` | `references/visual/` category catalogs | Binary files stay at their inventoried source paths; rights unknown; reference-only. |

## Recorded conflicts to resolve in later specs

1. Old docs claim “100%” effect coverage, but this describes numeric handler coverage, not 150 exact card semantics. E.g. lethal immunity text and 45% lifesteal differ from shield substitution and 22% in the runtime.
2. `CardSystem.sell()` exists but the v1.11.1 UI removed selling. Preserve the callable oracle; production must not expose selling without an approved economy change.
3. Shop odds label uses independent-draw approximation although the shop rejects duplicates. Do not canonize it as exact probability.
4. Player loss damage uses its pre-loss win streak and enemy level; bot loss damage uses winner streak and round. Capture both, decide parity versus intentional correction before porting.
5. `preGold || gold` treats zero as absent in interest calculation. Preserve as an explicit oracle edge case, not a new design rule.
6. Random-comparator sorting is JS-engine-dependent; fixed seeds in Node preserve this baseline only. Production needs a specified shuffle/RNG contract.
7. `.work/legacy-source` includes 299 original asset/data files, a 405-file nested web checkout and 448 Git metadata files. The former “299 total” statement applied only to the original asset/data portion. The external OneDrive original is not read or modified.
8. `MarketScene` explicitly requests **3 shop slots**, while `CardSystem` helper defaults and its displayed-at-least-one probability formula use **4**. The seeded foundation fixture exercises the helper API; the actual three-card UI is evidenced in browser captures. v1.16 must distinguish UI behavior from helper defaults before defining a production shop contract.

The v1.16 validator must fail on unknown aliases, ID loss, mismatched texts/costs/levels, changed distributions, or ambiguous source selection. It must never silently assign an unknown branch to Power as the old importer can do.
