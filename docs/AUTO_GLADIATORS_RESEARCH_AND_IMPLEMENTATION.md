# Auto Gladiators → Hero Smash: research & implementation audit (2026-10-26)

## Scope & evidence policy
We are reconstructing genre mechanics, not Dota IP, copyrighted assets, exact UI, or proprietary code. This report separates **C** (confirmed from dated historical guides), **R** (Hero Smash runtime from main), **P** (proposed), and **U** (unverified for current S11).

### Research sources
- [Steam workshop listing / game overview](https://steamcommunity.com/sharedfiles/filedetails/?id=3147450491) — versions, publisher & current features (evidence and dates must be checked against active patch).
- [Chinese historical FAQ](https://www.iyingdi.com/tz/post/5358014) — 2024 classic level/sect system, rewards and gameplay FAQ.
- [2024 abilities guide](https://nobsgameguides.gr/dota-2-auto-gladiators-abilities-guide/) — partial, not an exhaustive authoritative database.
- Hero Smash source of truth: `data/cards.json`, `data/heroes.json`, `data/branches.json`, `data/economy.json`, `src/game/*`, `src/scenes/*`.
- Hero Smash historical preserved source: `data/legacy_deck_source.json` (not evidence of modern live S11).

## Classic gameplay to restore
| Mechanic | Historical | Hero Smash main | Required implementation |
|---|---|---|---|
| Single customizable hero | C | 16 heroes with skill, no independently leveled hero | Derive level from sects; add stat growth; talent selection |
| Sect XP | C: common 1, epic 2, legendary 4 per level | R: normal 1, epic 2, legendary 3 | New progression module; migrate only with balance review |
| Sect milestones | C: 4/10/20/40 | R: 4/10/20/40 but tiers UI internally 1..5 | Add separate 0..4 semantic sect level |
| Hero level | C: sum of sect levels | R: cosmetic derived card-count level in market | Replace UI once progression tested |
| Talents | C: choices at hero levels 5/10/15 | R: no standalone talent-choice system | Talent definitions, picker state, persistent per-run selection, effect hook |
| Artifact reward | C: rounds 3/8/13 (2024) | R: no standalone system | Draft overlays & dynamic modifier semantics |
| PvE equipment reward | C: rounds 5/10/15 (2024); win pick 1/3, loss random | R: no standalone equipment system | Add event scheduling, battle PvE, item inventory |
| Shop | C: rarity availability depends on sect/hero progression | R: rarity filtered by branches, thresholds, static weights | Probability model, offers generation, disclose odds |
| Abilities | C: historic 150; later S11 advertises 170 | R: imported historic 150; 90 normal/36 epic/24 legendary | Keep IDs; audit semantic parity for every description |
| Status effects | C: interacting stacks/triggers | R: 36 recognized handler keys | Add exact trigger graph; test timed/conditional cards |
| Bot battle | C auto-battle core | R: human simulated full combat, bot-v-bot approximate score | Eventually same deterministic simulation for all |
| Multiplayer & seasons | advertised in workshop | R only bot training; other buttons locked | Later authoritative server & anti-cheat |
| 13th sect | S11 advertised | R 12 | Research precise name/rules first; DO NOT invent |
| Cosmetics | Dota source game | R custom manga/anime direction | Entirely original, separate IP and asset provenance |

## Confirmed existing Hero Smash values (R)
- 16 heroes / 12 branches / 150 legacy cards.
- Cards: 90 Normale, 36 Epica, 24 Leggendaria; level caps 5/3/1; rarity prices 100/200/300 in most cards.
- 8 active / 4 banned branches generated at run start; 3 compatible hero draft slots; two rerolls; 20s hero timer.
- 8-participant bot league (player + 7 bots); max 12 rounds; run HP 100; combat max 45 seconds.
- 35s market preparation; 3 shop offers; shop reroll 20; random card 100.
- 300 starting gold; base income 300; interest +10 per 100 up to 100; win +50; streak-related income; **no selling by UX contract**.
- The imported card dataset has legendary `points=3`, conflicting with classic rule of 4 XP. The branch UI tiers are existing technical conventions and should not be globally reinterpreted without migration.

## Key design/risk decisions
1. Preserve current game's playable behavior unless explicitly enabled: new progress module is pure and separate; does **not** yet mutate old scoring.
2. Distinguish **sect XP** (classic 1/2/4) from **legacy branch points** (current 1/2/3). Adoption demands adjusted rarity unlocking, bonus scaling, tests, and balance data.
3. Historic calendar has events after round 12, but current Hero Smash runs end at max 12. Introduce 16+ round mode **before** promising level 15 / round 13 events to users.
4. Defining talent, artifact, and equipment pools requires a new *original* database and effects adapter. No assumption of exact live S11 coefficients.
5. `CardSystem.sell` still exists in code though UI contract disallows selling. Do not re-enable unintentionally.
6. Current bot-v-bot `powerScore` is an estimate not identical to combat engine — affects PvP fairness.
7. S11 counts are promotional not a complete extractable card database; no authoritative current 170-card names/stats found.
8. **Licensing/IP**: mechanics can inspire an original game; Dota names, artwork, sound and proprietary interface should not be copied.

## Recommended milestones
**M0 documented adapter (this PR)**: classic progression pure module, thresholds/bonus, unit tests, runtime adapter. No default balance changes.

**M1 consistency**: opt-in classic game mode config; separate `sectXp` from bonus `points`; update market card availability, UI and tooltips; test level 5/10/15 unlocks; adapt max rounds.

**M2 talent engine**: hero level events, 3-option talent draft, hero-specific definitions, deterministic trigger effects, save schema & tests.

**M3 artifacts + PvE equipment**: reward event scheduling, 3-choice draft, inventory & slots, PvE/creep round mode, combat stats pipeline, event recap.

**M4 card semantic audit**: machine-parse `legacyEffect` vs runtime effects keys and manual verification for all 150; gap report and exact proc lifecycle; balancing simulator.

**M5 bot fidelity & multiplayer**: full bot simulation under deterministic RNG; game state logging, replay, server authority (before ranked).

**M6 original art/UI**: manga/anime authored assets, performance on real mobile, accessibility and localization.

## Acceptance gates
- `node --test tests/gladiator-progression.test.mjs` green (requires project ESM config or compatible Node loader).
- No default market/economy/balance regression.
- Unit tests for rarity XP, dual-branch XP, 0..4 milestones, hero sum, talent milestones, scheduled rounds.
- Combat, bots, UI and reward economy need separate integration tests before release.

## Unverified; do not invent
- Current live S11 list and definition of all 13 sects.
- Names, exact formulas and patches for all 170 S11 abilities.
- Complete equipment and artifact pool, drop rates, shop odds by hero level.
- Current balance coefficients, season server matchmaking, progression resets and monetization details.

Research status: foundational/classic rules verified; **NOT** an exhaustive reverse engineering of current proprietary S11.  
