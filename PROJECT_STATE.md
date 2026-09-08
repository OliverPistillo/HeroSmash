# Hero Smash — Project State

**State date:** 2026-09-08
**Macro phase completed:** v1.15 Revival/Foundation
**Phase status:** COMPLETE
**Branch:** `revival/v1.15-foundation`
**Validated implementation:** `022cc023865ffcba73a36e26101858e35df24aec`
**Committed evidence / next-phase scope:** `3b8778b768757a110da30759562d54b3b88746be`
**Main unchanged:** `66a5ba67f0691b7d50a11fa873f4ed24c80a14ef`

This state update is the documentation-only macro closeout after all applicable foundation gates passed. The closeout commit is identified by `docs: close v1.15 foundation and update project state`; its own SHA cannot be embedded in the same commit and is recorded in the task completion report. No remote push or main merge was performed.

## 1. Current production reality

`D:\Dev\HeroSmash` is the production workspace. `game/project.godot` boots in Godot **4.7.2 stable**, uses typed GDScript, the **Mobile renderer**, landscape settings and a 2.5D sample floor/camera. The original pipeline fixture is a one-bone, one-material, 1-meter animated cube, not a final hero. No gameplay rewrite has been undertaken.

Blender **5.2.1 LTS** → GLB → Godot is validated, including skeleton, `idle`, material/texture counts, scale/origin and runtime loading. Blender source, validated export and generated runtime copy are separate, with matching GLB hashes. The new source/runtime binaries total 103,023 bytes.

Technology/product decisions changed: **none**. Godot 4.7.2, Blender 5.2 LTS, real-time 3D characters, 2.5D arenas and Android/iOS landscape remain locked. No final characters, 150-card effect rewrite or multiplayer was started.

## 2. Preserved legacy and inventory

The v1.14.3 JS/Canvas prototype is now `legacy/web-prototype/`. **393 files** moved using `git mv`; all original Git blobs remain identical. The prototype remains bootable with:

```powershell
python -X utf8 legacy/web-prototype/tools/serve.py
```

Open `http://127.0.0.1:8000/`. Home, draft, market, combat and direct return to preparation were observed in the browser. The reference includes economy, bot league, card import and saved-profile behavior.

The initial repository census covers **427** tracked paths. The read-only `.work/legacy-source/` census covers **1,152 files**: 299 original asset/data/reference files, 405 nested web-checkout files and 448 nested Git metadata files. All archive paths and SHA-256 hashes remain unchanged. The original external OneDrive source was not accessed or modified.

**86 exact duplicate groups / 193 paths**: 68 cross-source, 17 within archive, 1 within repo. All retained. The reference registry indexes 832 image origins in 736 byte-hash groups; no legacy image is cleared for final production. Binaries remain at indexed legacy paths.

Inventory, classifications, exact move list, canonical selections and conflicts are committed under `docs/migration/`. Governance remained at root/docs; the finished v1.15 execution plan is now under `docs/exec-plans/completed/`.

## 3. Canonical data and unresolved semantics

The 12 master branches and 8 active / 4 banned rule remain intact. The committed imported `legacy/web-prototype/data/legacy_deck_source.json` is the authoritative identity/metadata source for all 150 cards. IDs, names, effect text, rarity, cost, levels, memberships and legacy paths pass comparison with the runtime derivative; distributions remain 90 Normal / 36 Epic / 24 Legendary and 84 single / 66 dual branch.

Archive `vecchio/deck.json` differs in 150 image paths only; the other two old card sources also differ in 24 level records. No merge/rebalance was performed. Current economy constants and code behavior remain the baseline, including edge cases documented in the source map.

The 16 JS runtime heroes remain a behavior oracle. `hero.json.txt` contains 20 candidate anthropomorphic concepts, preferred direction but still pending v1.18 approval. Candidate aliases Arcane→Essence, Venom→Toxin and Frost→Ice are documented, not a roster replacement. No manually maintained duplicate gameplay dataset was added under `game/data/`.

## 4. Toolchain status

- Godot: verified **4.7.2.stable.official.ed1daf0bf**, portable at `.work/tools/godot-4.7.2/`, downloaded from the official release only after environment detection/reporting and SHA-256 verification.
- Blender: existing Steam installation **5.2.1 LTS**, hash `9e2066aef7ef`; no installation/upgrade.
- Python 3.14.7, Node 20.19.6, Git 2.55.0.windows.3 and Java 17.0.15 available. Existing Python 3.12/Pillow 12.1.0 used for arena validation.
- Android: `ANDROID_HOME` points to a missing SDK; no ADB/sdkmanager/build tools found in checked locations, including Unity roots. Godot export-template directory is empty. No SDK installed or package/device check claimed.
- No global packages, MCPs or toolchain upgrades installed. Exact paths and detection: `docs/migration/ENVIRONMENT.md`.

## 5. Validation and evidence

Full local foundation profile passed **18 checks** from a clean detached checkout with no prior Godot cache; the checkout remained clean after import and tests. Evidence commit above includes exact commands/output in `docs/qa/evidence/v1.15/foundation.json`.

Coverage: archive and relocation integrity; canonical metadata; five negative validator cases; reference registry; 45 JS modules and 300 HTTP resources; eight seeds × three rounds repeated; asset checks; Blender/GLB structure/provenance; arena dimensions/alpha; pinned engines; headless import/boot; three known RNG vectors and 1,000 repeated values; imported skeleton/idle; actual Vulkan Forward Mobile rendering at 1366×768 and 844×390 on Radeon RX 7900 XT.

Screenshots and limits: `docs/qa/evidence/v1.15/REVIEW.md`. Run commands: `docs/qa/FOUNDATION_VALIDATION.md`. GitHub Actions skeleton is committed and locally parsed; no remote CI execution is claimed.

Known baseline failure: retained `combat_readability_check.py` fails two stale identifier searches already failing before migration. New current-component/HTTP/browser checks pass; the old failure is explicitly recorded, not reported as a successful old test.

Not run/applicable yet: Android/iOS exports, install/launch on devices, physical-notch safe-area QA, representative mobile performance and final animation/VFX sync. These remain device/release-phase gates. No final performance budgets invented.

## 6. Remaining debt

- All 150 exact card semantics still require specification/implementation; numeric-handler coverage is not exact-card coverage.
- Player/bot proc asymmetry, JS random-comparator shuffle, zero-preGold interest fallback and differing HP-loss formulas need explicit porting decisions.
- Actual market UI uses three slots; helper defaults/probability formulas use four. No-selling UI coexists with a latent sell API.
- Legacy UI is dense at phone scale. Reference image rights/subjects and final visual direction require review.
- Shared production rig/animation conventions, final roster, representative mobile profiling, SDK/export/signing configuration remain deferred.
- Blender 5.2 reports a `Material.use_nodes` future-deprecation warning; successful pinned export is unaffected.

## 7. Next macro phase

**v1.16 — Canonical Data Migration + Exact Card Semantics Framework**.

Active plan: `docs/exec-plans/active/V1_16_CANONICAL_DATA.md`. Next work is schemas, deterministic generation of canonical datasets/provenance, typed loaders and exact field comparison, followed by an effect contract and honest 150-ID semantics registry with a small specified pilot. Preserve the web oracle; do not jump to all effects, final heroes or multiplayer.
