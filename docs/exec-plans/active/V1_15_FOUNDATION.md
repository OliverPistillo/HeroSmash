# v1.15 — Revival / Foundation Execution Plan

## Goal

Turn the existing repository + legacy archive into a clean, reproducible, agent-ready production workspace without losing working behavior or historical data.

## Rule zero

**Inventory before movement. Movement before deletion.**

## Phase A — Environment and baseline

- [ ] Verify Git working tree is clean.
- [ ] Record `main` baseline SHA.
- [ ] Confirm branch is `revival/v1.15-foundation`.
- [ ] Detect installed Godot, Blender, Python, Git, Android tooling.
- [ ] Record exact versions.
- [ ] Do not auto-upgrade tools without reporting.

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

The old local source is expected near:
`C:\Users\olive\OneDrive\Desktop\Progetti\HeroSmash`

If accessible, inventory it without modifying it.

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
