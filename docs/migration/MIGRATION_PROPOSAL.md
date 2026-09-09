# v1.15 migration proposal / execution contract

Prepared after the complete path census and system/data/asset classifications. The current human task authorizes executing v1.15 and the target tree already approved in `ARCHITECTURE.md`; no new product decision is introduced. This document makes the exact move set reviewable before execution.

## Exact move set

`repo_inventory.csv` is the exhaustive 427-path baseline. Its `disposition=git-mv` rows list **393** exact source→target mappings:

- Entire `src/`, `data/`, `assets/`, `previews/` → same relative paths in `legacy/web-prototype/`.
- Root `index.html`, `manifest.webmanifest`, historical `README.md` and 16 `PATCH_NOTES_*.md` → isolated web root.
- 20 historical Markdown files directly under `docs/` → isolated `docs/`; `docs/index.md` and every governance subdirectory stay.
- Seven original root `tools/*.py` → isolated `tools/`. Root tooling README remains governance.

Use `git mv` for each tracked file; preserve bytes and validate Git blob identity. No source deletion or binary deduplication. Keep the 34 governance/scaffold paths in place, updating documentation only where this phase requires it. New root README describes both runtimes.

The archive's **1,152** files remain at `.work/legacy-source/`: **299** original files + **405** nested checkout files + **448** nested Git metadata files. Never run mutating Git commands inside that copy, and never access the original OneDrive source. Archive retention is verified by path set and SHA-256 after migration.

## Additions

Create production folders in `ARCHITECTURE.md`, a small Mobile-renderer Godot bootstrap, deterministic headless test, Blender-generated safe animated cube sample, explicit runtime GLB copy with matching hash, reference catalogs, validators and CI. No gameplay dataset is duplicated into `game/` in v1.15.

New procedural Blender/GLB sample binaries must be small and explicitly admitted through `.gitignore` exceptions. Downloaded tools, caches, exports/packages, logs and repeated test reports stay under ignored `.work/`; committed evidence and inventories live under `docs/migration/` and `docs/qa/evidence/v1.15/`.

## Validation sequence

1. Commit inventory/classification/proposal and pre-movement oracle fixture.
2. Check the six mandatory reports exist and are nonempty; validate all move inputs before any `git mv`.
3. Move only exact manifest rows; verify all 393 Git blobs and archive hashes unchanged.
4. Run the same seeded oracle, asset/link checks and browser smoke after isolation.
5. Run Godot import, headless boot, deterministic test, actual Mobile-renderer screenshot and Blender→GLB→Godot checks.
6. Close only if foundation gates pass. Keep the active plan and leave `PROJECT_STATE.md` unchanged if required gates are unavailable/failing.

## Rollback

The move-only commit is separate. `git revert <move-commit>` restores the historical layout (after reverting dependent production/harness commits if returning the entire branch to baseline). The archive and `main` are unaffected. No push or main merge is part of this task.
