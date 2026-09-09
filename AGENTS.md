# Hero Smash — Codex Map

This file is intentionally short. It is a **map**, not the project encyclopedia.

## Read order before substantial work

1. `PROJECT_STATE.md` — what is true right now.
2. `PROJECT_MASTER.md` — product decisions and non-negotiables.
3. `ARCHITECTURE.md` — target technical structure.
4. The relevant file under `docs/`.
5. Legacy code/data only after the authoritative docs above.

## Source-of-truth priority

When information conflicts, use this order:

1. Current human task/instruction.
2. `PROJECT_MASTER.md`.
3. `PROJECT_STATE.md`.
4. Canonical product/data specs in `docs/product-specs/`.
5. Accepted ADRs in `docs/architecture/`.
6. Current production code and tests.
7. Legacy web/Godot/archive material as reference only.

Never silently resolve a conflict by inventing a new rule. Record the conflict in `PROJECT_STATE.md` or the active execution plan.

## Locked technology direction

- Runtime: Godot 4.7.2 stable.
- Language: typed GDScript.
- 3D authoring: Blender 5.2 LTS.
- Character rendering: real-time 3D.
- Arena presentation: 2.5D hybrid 3D.
- Primary target: Android/iOS landscape.
- Renderer target: Godot Mobile renderer unless profiling proves otherwise.
- Exchange format: glTF 2.0 / `.glb`.
- The JS/Canvas build is a migration/reference prototype, not the final runtime.

## Non-negotiable game data

- 12 canonical branches:
  `Assault`, `Guardian`, `Essence`, `Rage`, `Ice`, `Toxin`,
  `Shield`, `Healing`, `Power`, `Precision`, `Wound`, `Dodge`.
- A run activates 8 branches and bans 4.
- The imported legacy deck contains 150 cards and stays authoritative until an explicit spec changes it.
- Do not invent or delete cards, branches, heroes, economy rules, or rarity rules without updating the authoritative spec first.

## Migration safety

- Do not delete legacy sources until inventory + migration validation are complete.
- Do not overwrite `main` during revival work.
- Prefer `git mv` when relocating tracked files.
- Preserve legacy IDs when migrating data.
- Every migration must have a validator or comparison report where practical.

## Godot coding rules

- Prefer typed GDScript and explicit public interfaces.
- Core simulation must be deterministic when supplied a seed.
- Keep gameplay rules independent from presentation where practical.
- Do not hard-code card/hero/branch definitions into scene scripts.
- Avoid global mutable state except documented autoload services.
- Use signals/events for presentation reactions to combat simulation.
- Mobile performance budgets are part of correctness.

## Art pipeline rules

- Blender source and runtime exports are separate concepts.
- Production runtime consumes validated `.glb`/textures, not arbitrary working files.
- Shared skeleton/animation conventions must be documented before mass-producing characters.
- Reference imagery must be indexed in the reference manifest.
- Third-party/proprietary reference assets are **reference-only** unless rights are explicitly cleared.
- Never copy Dota 2 or other proprietary production art/UI into Hero Smash.

## Quality gates

After code changes, run the relevant checks defined in `docs/qa/QUALITY_GATES.md`.

For gameplay changes, prefer:
- unit tests;
- seeded simulation;
- headless Godot checks;
- snapshot/statistical comparison when applicable.

For UI/3D changes, add:
- runtime screenshot/video evidence;
- target-resolution checks;
- mobile performance evidence when material.

## Project-state discipline

`PROJECT_STATE.md` is updated at the end of each **macro phase**, not after every tiny commit.

A macro-phase update must include:
- phase completed;
- exact branch/commit;
- decisions changed;
- files/systems migrated;
- tests and validation status;
- known debt;
- next macro phase.

## Task completion report

Every substantial Codex task should end with:
- what changed;
- files touched;
- tests/commands executed;
- failures or skipped checks;
- screenshots/artifacts if relevant;
- follow-up debt discovered.

Do not claim success when a required validation was not run.
