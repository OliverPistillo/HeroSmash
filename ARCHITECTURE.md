# Hero Smash — Target Architecture

## Target repository shape

```text
HeroSmash/
├── AGENTS.md
├── PROJECT_MASTER.md
├── PROJECT_STATE.md
├── ARCHITECTURE.md
│
├── game/                         # Production Godot project
│   ├── project.godot
│   ├── export_presets.cfg
│   ├── autoload/
│   ├── data/
│   │   ├── canonical/
│   │   ├── schemas/
│   │   └── generated/
│   ├── scenes/
│   │   ├── app/
│   │   ├── combat/
│   │   ├── market/
│   │   ├── heroes/
│   │   ├── arenas/
│   │   └── ui/
│   ├── scripts/
│   │   ├── core/
│   │   ├── combat/
│   │   ├── cards/
│   │   ├── branches/
│   │   ├── economy/
│   │   ├── league/
│   │   ├── bots/
│   │   └── presentation/
│   ├── shaders/
│   ├── assets_runtime/
│   └── tests/
│
├── art/
│   ├── blender/
│   │   ├── shared/
│   │   ├── rigs/
│   │   ├── characters/
│   │   ├── arenas/
│   │   ├── props/
│   │   └── materials/
│   ├── exports/
│   │   ├── characters/
│   │   ├── arenas/
│   │   └── props/
│   └── pipeline/
│
├── references/
│   └── visual/
│       ├── characters/
│       ├── arenas/
│       ├── cards/
│       ├── brand-ui/
│       ├── expressions/
│       ├── fx/
│       └── ux/
│
├── docs/
│   ├── index.md
│   ├── architecture/
│   ├── product-specs/
│   ├── references/
│   ├── migration/
│   ├── codex/
│   ├── qa/
│   └── exec-plans/
│       ├── active/
│       └── completed/
│
├── tools/
│   ├── migration/
│   ├── validation/
│   ├── simulation/
│   └── asset_pipeline/
│
└── legacy/
    ├── web-prototype/
    ├── archive-index/
    └── README.md
```

The v1.15 phase may temporarily retain legacy files in their current locations until inventory is complete.

## Runtime separation

### Simulation layer
Owns:
- deterministic state;
- cards;
- branches;
- economy;
- league;
- bots;
- combat rules;
- seeded RNG;
- event output.

Must be runnable without 3D rendering.

### Presentation layer
Consumes simulation events and owns:
- 3D animation;
- camera;
- VFX;
- UI;
- sound;
- hit pause;
- shake;
- floating numbers;
- presentation timing.

Presentation must not become the source of truth for damage or game rules.

## Combat scene concept

```text
CombatRoot (Node3D)
├── ArenaRoot (Node3D)
├── FighterLeft (CharacterBody3D/Node3D)
├── FighterRight (CharacterBody3D/Node3D)
├── VFXRoot (Node3D)
├── CameraRig (Node3D)
│   └── Camera3D
├── WorldEnvironment
└── UI (CanvasLayer)
```

2.5D rule:
- fighting plane/lane is constrained;
- depth is controlled;
- camera is authored, not player-controlled;
- arena may mix real geometry, billboards/planes and foreground layers.

## Mobile rendering principles

- Mobile renderer first.
- One primary combat camera.
- Tight shadow budget.
- Baked/static lighting where useful.
- Small number of transparent overdraw-heavy effects.
- Texture atlases where they materially help.
- LODs only where useful; avoid complexity for its own sake.
- Profile on real Android devices early.

## Data architecture

Canonical product data should be machine-validatable.

Preferred:
- JSON for portable authored datasets during migration;
- JSON Schema for validation;
- Godot Resources generated/loaded only where they improve runtime/editor ergonomics.

Do not create multiple manually maintained copies of the same card/hero/branch data.

v1.16 implements this boundary with five generated datasets, Draft 2020-12 schemas,
typed definitions and a transactional `CanonicalCatalog`. Schemas and guarded pilot
proposals are authored; canonical JSON and comparison reports have one generator.
See `docs/architecture/ADR-0003-canonical-data-and-effect-contracts.md`.

`EffectRunner` consumes typed definitions and caller-owned events. Its integer
state, seeded RNG, timer ordering, bounded transactions and command log are entirely
headless. `base_text_v1` remains the opt-in v1.16 proposal profile. v1.17 adds the
headless resolver, damage/status/lethal pipeline and exact numbered-level access,
with explicit unresolved effect bindings; see ADR 0004 and the combat product specs.
No final fighter presentation is wired to this laboratory framework yet.

v1.18 adds a separate production identity/reference specification under
`docs/product-specs/roster/` and `docs/art/`. JSON is authored once; identity sheets,
matrices and contract Markdown are generated. This metadata is not loaded as
runtime hero data. Animation markers consume resolver events; they never apply
damage. The 16 oracle IDs and all 150 cards remain unchanged. The four proposed
rig families and Blender/GLB/Godot conventions are validated before final asset work.

## 3D asset flow

```text
Reference library
   ↓
Blender source
   ↓
validation
   ↓
GLB export
   ↓
Godot import
   ↓
runtime scene wrapper
   ↓
device validation
```

Character production should converge on:
- shared scale;
- shared origin conventions;
- shared skeleton when morphology allows;
- animation naming convention;
- material budget;
- texture budget;
- collision/hurtbox conventions.

## Testing architecture

Three layers:

1. **Pure logic tests**
   - cards;
   - branches;
   - economy;
   - combat math.

2. **Simulation tests**
   - seeded fights;
   - thousands of runs;
   - balance/statistical regressions.

3. **Runtime tests**
   - Godot headless scene boot;
   - scene/resource load;
   - screenshots/video for presentation;
   - Android package smoke tests.

## CI principle

Anything Codex can change repeatedly should eventually have a machine-checkable gate.

## Implemented v1.19 character boundary

`art/characters/solkael_lionheart/source/` owns the editable Blender source;
`tools/asset_pipeline/` validates saved source and independently validates its GLB
before copying it to `game/assets/characters/solkael_lionheart/`. Staging exports
are ignored. New source/reference/runtime binaries use scoped Git LFS.

`game/scenes/characters/solkael_lionheart/hero_solkael_lionheart.tscn` wraps the
imported GLB. Typed `SolkaelFighter` and `FighterEventAdapter` consume immutable
resolver IDs/timestamps, maintain presentation playback/seek state and emit only
cosmetic cues. No damage, balance or catalog mutation API crosses this boundary.
The QA viewer is an explicit test script; the foundation main scene is unchanged.
This is one measured pipeline fighter, not a complete arena or physical-phone budget.
