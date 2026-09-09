# v1.15 evidence review — 2026-09-08

Validated implementation: `022cc023865ffcba73a36e26101858e35df24aec` on `revival/v1.15-foundation`. A fresh detached checkout at `.work/validation-final` started clean without `.godot` cache. Full local profile passed **18 checks**; `git status --porcelain` remained empty after import/testing.

`foundation.json` contains exact subprocess arguments, versions, outputs, result markers, counts, source-integrity results and applicability limits. It records a clean working tree at the start. `blender_sample.json` records the completed Blender build; export provenance is in `art/exports/props/foundation_sample.provenance.json`.

## Actual visual checks

- `web-before.png`: original root prototype, Home loaded at 1366×768 before relocation.
- `web-after.png`: same Home layout after serving `legacy/web-prototype/`, 1366×768. No browser console warnings/errors were captured. Visual smoke is not a pixel-identical golden test; the old animated background and capture timing can differ.
- `web-draft.png`: Home → three-hero draft, 8 active / 4 banned branches and 20-second timer visibly present.
- `web-market-loop.png`: preserved run reached round 5 and returned directly to preparation after combat; no browser console warnings/errors captured.
- `web-phone-viewport.png`: full 844×390 browser viewport. DOM inspection confirmed viewport and Canvas backing dimensions 844×390. The legacy renderer retains its 1366×768 design aspect with letterboxing; its dense small text remains UX debt for the native production UI. No legacy UI redesign was attempted.
- `godot-mobile-1366x768.png` and `godot-mobile-844x390.png`: actual Vulkan **Forward Mobile**, AMD Radeon RX 7900 XT. Safe-area margins and title/sample/floor visible, no overlap or clipping at these sizes. This is desktop GPU validation of the Mobile renderer, not Android device performance.

Browser viewport overrides were reset and the temporary browser tab closed after testing. The legacy server can be restarted with its documented command.

## Failed / unavailable / resolved

- Retained legacy readability script still returns 1: stale `STATUS_ICONS` / `drawEventLog` checks. Its same failure was recorded before relocation. Current `StatusIconBar` / event text, HTTP loading, actual browser flow and the seeded oracle pass. The harness labels the expected baseline exception explicitly.
- First new Godot test compared a human-readable version string with CLI formatting; corrected to numeric version and status fields. Final headless/runtime checks pass.
- Blender initial default-scene orphan material warnings were removed by purging unused data before authoring. Remaining `Material.use_nodes` warning concerns Blender 6.0 deprecation; pinned Blender 5.2 export succeeds.
- Original default Python lacks Pillow; an existing Python 3.12 with Pillow 12.1.0 ran the old arena validator successfully. No dependency installed.
- Android SDK/ADB/build tools not found in PATH, standard locations or checked Unity editor roots. Godot export-template directory exists but is empty. Java 17.0.15 is available. No Android export/device profiling or iOS signing/build was run.
- GitHub workflow is a committed CI skeleton; it was parsed locally and its portable gates were exercised locally. No push was made and no remote Actions run is claimed.
- Physical device safe areas, representative fighter performance, final character animation/VFX sync and release gates are deferred to their relevant phases.
