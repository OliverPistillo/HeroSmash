# Hero Smash — Project Master

**Status:** Authoritative product master  
**Revival baseline:** v1.15 Foundation  
**Last master decision date:** 2026-09-08

## 1. Product vision

Hero Smash is a mobile-first auto-battler presented like an arcade fighting game.

The player builds power strategically in a preparation/market phase, then watches a visually expressive automatic duel between two 3D fighters inside a 2.5D arena.

The intended identity is:

> **Auto-battler brain, arcade-fighter face.**

Hero Smash may be inspired by the pacing and strategic appeal of auto-battlers such as Dota Auto Gladiators, but its characters, art, UI, terminology, assets and production identity must remain original.

## 2. Platform and format

Primary:
- Android;
- iOS;
- landscape;
- touch-first.

Secondary:
- Windows development/debug build.

Future:
- online accounts;
- normal PvP;
- ranked;
- private lobbies;
- seasons.

The first production milestone is an excellent offline/bot experience, not multiplayer.

## 3. Locked production stack

### Engine
- Godot 4.7.2 stable.
- Typed GDScript.
- Godot Mobile renderer by default.

### 3D
- Blender 5.2 LTS.
- glTF 2.0 / GLB exchange.
- Real-time 3D characters.
- Real-time skeletal animation.
- 2.5D hybrid arenas using 3D geometry, planes, lighting and controlled depth.

### Camera/gameplay presentation
- Camera3D with tightly controlled framing.
- Fighters primarily operate along a readable combat axis/lane.
- Depth exists for staging, VFX, dodge/impact and environmental composition, not free-roaming exploration.
- Combat readability has priority over physical realism.

## 4. Core loop

Target flow:

1. Home.
2. Generate active/banned branch pool.
3. Hero Draft.
4. Preparation / Market.
5. Automatic 1v1 combat.
6. Compact round recap.
7. Return directly to preparation.
8. Repeat until elimination/end.
9. Final summary.

## 5. League

Initial production mode:
- 8 participants;
- 1 human player;
- 7 bots;
- 100 run HP baseline;
- bots have hero, gold, build, card levels, streaks and league state.

Bot-vs-bot fights may be simulated headlessly when no visual presentation is required.

## 6. Branch system

Canonical branches:

1. Assault
2. Guardian
3. Essence
4. Rage
5. Ice
6. Toxin
7. Shield
8. Healing
9. Power
10. Precision
11. Wound
12. Dodge

Run rule:
- 8 active;
- 4 banned.

Canonical aliases to normalize from experimental material:
- `Arcane` → `Essence`
- `Venom` → `Toxin`
- `Frost` → `Ice`

No thirteenth branch is introduced by legacy/reference material without an explicit master change.

## 7. Card system

The legacy imported deck of **150 cards** is the current authoritative card list.

Known legacy distribution:
- 90 Normal;
- 36 Epic;
- 24 Legendary;
- 84 single-branch;
- 66 dual-branch.

Legacy IDs 1–150 must be preserved through migration.

Card effects must eventually be implemented explicitly rather than relying only on broad branch/keyword approximations.

No new production card is added merely to fill content.

## 8. Hero direction

The revival should evaluate the newer anthropomorphic roster found in the legacy archive as the preferred visual/product direction.

Examples include:
- Solkael Lionheart;
- Fenrox Bloodhowl;
- Kitsara Moonveil;
- Aethryon Stormwing;
- Brumgar Earthhide;
- Sylvex Venomkiss;
- Rajuro Strikefang;
- Morvayne Blackquill;
- Karchar Reefbreaker;
- Elunor Lifethorn;
- and the remaining roster in the legacy character source.

The roster is **candidate-authoritative**, pending the dedicated Hero Roster macro phase.

Before mass production, every final hero needs:
- identity sheet;
- front / 3/4 / side / back reference;
- silhouette;
- scale;
- weapon/fighting style;
- material palette;
- expression sheet;
- animation list;
- VFX language;
- branch relationship.

## 9. 3D character animation minimum

Production character baseline:

- idle;
- intro;
- attack_light;
- attack_heavy;
- skill_cast;
- hit_react;
- dodge;
- stun/freeze reaction where needed;
- KO;
- victory;
- breathing/secondary idle.

Animation events must expose gameplay timing markers such as:
- windup;
- hit;
- cast;
- recover;
- projectile spawn;
- VFX spawn.

## 10. Arena direction

Arenas are 2.5D hybrid scenes.

Desired ingredients:
- strong background silhouette;
- layered depth;
- foreground occlusion props;
- readable fighting plane;
- limited camera drift;
- hit shake;
- atmospheric particles;
- lighting accents;
- one or more animated focal elements;
- mobile-friendly geometry/material budget.

The existing Beast Crucible artwork is a reference/migration candidate, not automatically final production art.

## 11. UI / Brand language

The product should feel:
- premium arcade;
- fantasy-tech;
- bold;
- high contrast;
- readable at phone distance;
- tactile;
- not like a generic web dashboard;
- not like an AI collage.

Core layout language:
- fighter HUD;
- slanted/beveled shapes;
- strong central timer;
- clear rarity language;
- restrained glow;
- consistent branch iconography;
- short labels;
- large touch targets.

Detailed visual truth belongs in the reference library and brand/UI specs, not in this file.

## 12. Economy baseline

Current prototype baseline to preserve until balance work:
- starting coins: 300;
- starting run HP: 100;
- preparation and combat timers as documented in current runtime/state;
- interest/streak/income rules migrate from the existing prototype and must be verified before rebalance.

Balance changes must be driven by simulation data, not intuition alone.

## 13. Simulation-first combat architecture

Combat rules must be separable from animation/rendering.

Required properties:
- seeded deterministic simulation where practical;
- serializable combat inputs;
- combat event stream;
- headless simulation;
- ability to run thousands of fights without rendering;
- replay/debug hooks.

This is essential for Codex-assisted testing and balancing.

## 14. Visual references

The reference library is organized by:
- characters;
- arenas;
- cards;
- brand-ui;
- expressions;
- fx;
- ux.

Every reference item should have:
- origin;
- author/owner if known;
- rights status;
- purpose;
- approved/reference-only status;
- tags;
- notes.

Reference is not permission to copy.

## 15. Project governance

`PROJECT_MASTER.md` changes only when a product/architecture decision is intentionally changed.

`PROJECT_STATE.md` changes at the end of each macro phase and records reality.

ADRs record major technical decisions and their rationale.

Execution plans describe active implementation work.

## 16. Macro roadmap

1. v1.15 — Revival / Foundation / inventory.
2. v1.16 — Canonical data migration + exact card semantics framework.
3. v1.17 — Combat simulation + automated balance lab.
4. v1.18 — Final hero roster + visual reference lock.
5. v1.19 — Blender shared rig + character pipeline.
6. v1.20 — Production 3D combat presentation.
7. v1.21 — Arenas / FX / audio / game feel.
8. v1.22 — Mobile performance + device QA.
9. v1.23 — progression / tutorial / save migration.
10. v1.24 — Android/iOS release candidate.

Online multiplayer is a later product phase and should not destabilize the offline core.
