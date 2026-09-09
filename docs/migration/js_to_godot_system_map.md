# JS → Godot system and parity map

All JS paths below are relative to `legacy/web-prototype/src/` after isolation. The full JS subtree is retained unmodified. Port behavior/specifications in later phases; do not port Canvas drawing calls.

| JS source | Reusable specification / behavior | Godot destination | Required parity checks |
|---|---|---|---|
| `game/GameData.js`, `data/*.json` | Load complete definitions before state construction; retain IDs | `game/data/`, typed loaders | 150-card metadata comparison, 12 branches, missing source failure, alias validation |
| `game/GameState.js`, `scenes/HeroSelectScene.js` | 8/4 branch pool, 3 eligible choices, 2 slot rerolls, 20s auto-pick leftmost/selection | `scripts/core`, `scenes/heroes` | Seeded pool and draft; unique choices; reroll limits; UI timer/default selection |
| `game/BranchSystem.js` | Level×points; tiers 4/10/20/40; bonus accumulation | `scripts/branches` | Threshold boundaries and dual-branch points; separate tier config from code |
| `game/CardSystem.js`, `scenes/MarketScene.js` | Active branches, max levels, any-branch unlock, weighted unique shop; lock, forced reroll, random buy, last-20 undo; collection without selling | `scripts/cards`, `scenes/market` | Eligible pool, unique slots, caps, funds, exact refund, lock, consumed RNG; clarify approximate odds before port |
| `game/EconomySystem.js` | Income, caps, streak transitions, loss HP compensation | `scripts/economy` | 300/100 start; win/loss and cap boundaries; zero preGold fallback; distinct bot/human HP formulas |
| `game/BotSystem.js`, `LeagueSystem.js` | 1 human + 7 bots, hero affinities, 5 buy attempts, pairings/byes, alive standings, one income application per round | `scripts/bots`, `scripts/league` | Seeded 8-player rounds; no duplicate income; elimination/bye fixtures in v1.17 |
| `game/CombatSystem.js` | Fixed-step behavior oracle: attacks, skills, armor, DoT, shields, dodge, death prevention, timeout tie policy and recap | `scripts/combat`, event stream consumed by presentation | Seeded fixed-1/60 fight outcomes and aggregates; later explicit event-order and individual effect tests |
| `game/RunSystem.js`, `scenes/CombatScene.js`, `SummaryScene.js` | Combat→recap→market directly; end on HP/alive/max-round; profile totals | `scripts/core`, `scenes/app` | Three-round snapshots, preparation reset, run completion and profile in later save work |
| `engine/SaveSystem.js` | Profile key `hs_custom_v17`, fallback `hs_custom_v07`, malformed JSON fallback | Documented save service only | Legacy-key migration, default merge, malformed payload; no active-run save assumed |
| `main.js`, `engine/SceneManager.js`, `Input.js`, `Renderer.js` | Scene lifecycle, 1366×768 layout, pointer coordinate mapping, landscape flow | `scenes/app`, `scenes/ui` | Actual browser boot before/after move; screenshot at reference/phone landscape; Godot viewport/safe-area smoke |
| `arena/ArenaLoader.js`, `ParallaxArena.js` | Layer order, floor/camera framing, crystal, shake and fallback | `scenes/arenas`, `scripts/presentation` | Relative asset URLs resolve; layer sizes/alpha; authored Godot camera evidence |
| `engine/AnimationSystem.js`, `CinematicSystem.js`, `Particles.js`, `Audio.js`, `ui/` | Presentation state/event intent only | AnimationPlayer/AnimationTree, VFX/audio/UI | Animation names/timing and no damage owned by presentation, after real fighters exist |
| Legacy `tools/*.py` | Import provenance, static HTTP server, asset checks | Keep inside web root; new tools at root | Start from any cwd; byte preservation; audit stale checks before relying on them |

## Foundation baseline contract

`tools/validation/web_oracle.mjs` is recorded **before movement**, using the original ES modules without editing them. Eight seeds × three rounds are repeated; fixtures cover draft, 8/4, shop, lock, buy/undo, economy caps/zero fallback, 8-player league, combat outcomes/recap, direct preparation and save-key fallback. Compare the same fixture after `git mv`. Additional static checks validate all local module/data/asset links, and a browser smoke confirms actual loading.

This is relocation parity, not proof that all cards are correctly implemented. Visual-only `Math.random()` floaters are excluded. Fixed seed+step is repeatable on the pinned Node engine; random-comparator shuffle is not a cross-engine production specification.

Known coupled behavior: `CombatSystem` mutates presentation fields; `phaseCooldown` decrements in visual update; selected procs/passives are player-only even when enemy loadout stats are applied; bot-vs-bot uses power-score approximation. Preserve these observations and require explicit v1.16/v1.17 decisions before changing rules.

## Pre-movement failures

`tools/combat_readability_check.py` already fails `status_icons` and `combat_log`: it searches stale identifiers `STATUS_ICONS`/`drawEventLog` in the newer scene. Retain the script unchanged and record the baseline failure; use current-component and runtime evidence in the new harness. This is not a regression introduced by relocation.
