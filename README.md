# Hero Smash

Production workspace: **Godot 4.7.2 stable**, typed GDScript, **Blender 5.2 LTS**, real-time 3D characters and 2.5D arenas, Android/iOS landscape first. The current Godot scene is a foundation pipeline sample, not migrated gameplay.

Read `AGENTS.md`, `PROJECT_STATE.md`, `PROJECT_MASTER.md`, `ARCHITECTURE.md`, then `docs/index.md`.

## Run

Open `game/project.godot` in Godot 4.7.2, or:

```powershell
& .work/tools/godot-4.7.2/Godot_v4.7.2-stable_win64_console.exe --path game
```

The portable local tool is ignored by Git. Other machines must supply their own verified executable. No command in the validation harness installs tools.

The preserved JS prototype remains runnable:

```powershell
python -X utf8 legacy/web-prototype/tools/serve.py
```

Open `http://127.0.0.1:8000/`. Serve this isolated root to preserve its relative URLs and localStorage origin. Historical docs inside it describe the old prototype, not production decisions.

## Verify

```powershell
python -X utf8 tools/validation/foundation.py --godot .work/tools/godot-4.7.2/Godot_v4.7.2-stable_win64_console.exe
```

This is the portable CI profile. Full local closeout also checks archive preservation, existing Blender/Pillow, and actual GPU rendering. Exact commands and evidence: `docs/qa/FOUNDATION_VALIDATION.md`.

Migration inputs and decisions: `docs/migration/`. The conceptual read-only legacy copy is `.work/legacy-source/`; never alter it or the external original. There is one authoritative imported 150-card deck, retained in the web prototype until v1.16; no new manually maintained gameplay copies live in `game/data/` yet.
