# Reproducible v1.15 validation

No scripts install tools or global dependencies. Detect and report available executables first. This machine's paths/versions are recorded in `docs/migration/ENVIRONMENT.md`.

## Full local foundation profile

From the repository root, using installed tools:

```powershell
python -X utf8 tools/validation/foundation.py `
  --archive .work/legacy-source `
  --godot .work/tools/godot-4.7.2/Godot_v4.7.2-stable_win64_console.exe `
  --blender 'C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe' `
  --pillow-python 'C:\Users\olive\AppData\Local\Programs\Python\Python312\python.exe' `
  --visual
```

Exit 0 means the requested profile passed. The report's `profile` and `limitations` distinguish a full local run from CI/partial validation; a partial run does not close the macro phase. Missing explicitly requested executables fail. Each subprocess is bounded to 60 seconds and errors are recorded; Godot error text fails even if the engine exits 0.

Output defaults to `.work/reports/foundation.json` and two GPU screenshots. Repeated reports/logs/caches are ignored. Curated closeout evidence is copied to `docs/qa/evidence/v1.15/` and committed. CI uploads its own report as an artifact.

## Individual checks

```powershell
node --experimental-default-type=module tools/validation/web_oracle.mjs
python -X utf8 tools/validation/data_parity.py --archive .work/legacy-source
python -X utf8 tools/validation/glb_check.py art/exports/props/foundation_sample.glb
python -X utf8 legacy/web-prototype/tools/asset_pipeline.py validate
& .work/tools/godot-4.7.2/Godot_v4.7.2-stable_win64_console.exe --headless --path game --editor --import
& .work/tools/godot-4.7.2/Godot_v4.7.2-stable_win64_console.exe --headless --path game --quit-after 10
& .work/tools/godot-4.7.2/Godot_v4.7.2-stable_win64_console.exe --headless --path game --script res://tests/foundation_test.gd
```

The fixed Node 20.19.6 oracle contains eight seeds × three rounds, repeated, captured before relocation in commit `e2f6720`. Do not regenerate its fixture to make a regression pass. It verifies relocation behavior, not the exact semantics of every card. Godot checks three known RNG vectors plus 1,000 repeated values, bootstrap, imported mesh/skeleton/idle.

Full census reproduction command: `python -X utf8 tools/migration/inventory.py --output .work/reports/inventory-recheck`. The committed census freezes the initial baseline and disk hashes; later governance edits mean a newly generated `working_sha256` may differ for retained docs. Never overwrite that initial evidence blindly. The validator checks baseline coverage, unchanged moved Git blobs and archive hashes.

## Baseline exception and gate applicability

The old `combat_readability_check.py` returns 1 for `STATUS_ICONS` and `drawEventLog`, which were already replaced in the v1.14.3 scene. Keep the old script unchanged. The harness explicitly checks that this known failure is unchanged and verifies the actual `StatusIconBar` and current event text path, HTTP resources and browser smoke. This documented foundation exception does not claim the old test passes or prove general combat readability.

Metadata parity, seeded tests, headless boot/import and sample asset gates apply. Browser/Godot screenshots at 1366×768 and 844×390 apply to relocation/bootstrap. Safe-area margins are inspected at those desktop viewports; physical device notches and touch ergonomics remain device QA debt. No final characters/VFX exist, so their synchronization and representative performance budgets do not apply yet.

Android export/install/device performance cannot run: SDK/build-tools/platform-tools/templates were not found/configured. iOS export/signing requires the Apple toolchain. These are release/device gates, not mandatory v1.15 bootstrap gates. No multiplayer, card-effect rewrite, mobile package or store release is claimed.
