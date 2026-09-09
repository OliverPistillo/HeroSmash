# v1.15 — Revival / Foundation Execution Plan

## Goal

Turn the existing repository + legacy archive into a clean, reproducible, agent-ready production workspace without losing working behavior or historical data.

## Rule zero

**Inventory before movement. Movement before deletion.**

## Phase A — Environment and baseline

- [x] Verify Git working tree is clean.
- [x] Record `main` baseline SHA.
- [x] Confirm branch is `revival/v1.15-foundation`.
- [x] Detect installed Godot, Blender, Python, Git, Android tooling.
- [x] Record exact versions.
- [x] Do not auto-upgrade tools without reporting.

## Phase B — Repository inventory

Create a machine-readable inventory of every tracked path.

Classify each item:
- current JS behavior prototype;
- canonical data;
- reusable production asset;
- generated asset;
- reference;
- obsolete;
- unknown.

Do not move files during the first inventory pass.

## Phase C — Legacy archive inventory

Current human override: inventory only `.work/legacy-source/` as the read-only legacy copy. The original external OneDrive location is not accessed or modified.

Hash files to detect duplicates against the Git repository.

Generate:
- archive inventory;
- duplicate report;
- candidate asset list;
- candidate visual-reference list.

## Phase D — Canonical source map

For each domain, identify current source of truth and migration target:

- branches;
- cards;
- heroes;
- economy;
- arena definitions;
- UI references;
- character references.

Explicitly flag conflicts.

## Phase E — Target tree

Create the target folders described in `ARCHITECTURE.md`.

Relocate legacy tracked content only after the inventory reports exist.

Use `git mv`.

Keep the web prototype bootable inside `legacy/web-prototype/` if reasonably possible.

## Phase F — Minimal Godot production shell

Create `game/` using Godot 4.7.2.

Requirements:
- landscape mobile project settings;
- Mobile renderer;
- bootstrap scene;
- deterministic test entry point;
- headless boot test;
- no gameplay rewrite yet.

## Phase G — Blender pipeline spike

Using Blender 5.2 LTS:
- create/use a tiny test rigged object or safe sample;
- export GLB;
- import into Godot;
- validate via command/script;
- record exact command path and output.

Do not mass-produce hero assets yet.

## Phase H — Codex/CI harness

Create:
- validation command entry point;
- baseline tests;
- CI skeleton;
- generated reports folder strategy;
- clear local commands in docs.

## Phase I — Closeout

Before declaring v1.15 complete:
- all foundation gates pass;
- inventory reports committed;
- no accidental binary explosion;
- `PROJECT_STATE.md` updated;
- final commit SHA recorded;
- next plan for v1.16 created.

## Deliverables

Expected committed outputs:
- clean project structure;
- inventory reports;
- migration source map;
- minimal Godot shell;
- sample GLB pipeline;
- test/CI skeleton;
- updated project state.

## Explicitly out of scope

- rewriting all combat;
- implementing all 150 exact effects;
- final hero modeling;
- final arenas;
- multiplayer;
- monetization;
- production store release.

## Completion record — 2026-09-08

Status: COMPLETE. Branch `revival/v1.15-foundation`. Validated implementation `022cc023865ffcba73a36e26101858e35df24aec`; evidence and next-phase plan committed at `3b8778b768757a110da30759562d54b3b88746be`. This documentation-only closeout updates PROJECT_STATE and archives the plan after all applicable foundation checks passed.

393 legacy paths moved unchanged, 1,152 archive files preserved, 86 exact duplicate groups retained. Full local profile: 18 checks pass from a clean checkout; see `docs/qa/evidence/v1.15/foundation.json` and `REVIEW.md`. The pre-existing stale legacy readability check remains an explicit baseline exception. Android/iOS export and physical device checks are deferred, as documented in `docs/qa/FOUNDATION_VALIDATION.md`.

Final tree follows ARCHITECTURE.md; execution was authorized by the current human task. Inventory/classification/proposal committed in e2f6720 before migration in 39ac756. No product decisions changed. Exact move list and debt: `docs/migration/V1_15_MIGRATION_REPORT.md`. Next phase is `docs/exec-plans/active/V1_16_CANONICAL_DATA.md`, not yet executed.
