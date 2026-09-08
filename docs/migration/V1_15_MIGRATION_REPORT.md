# v1.15 migration report

Technical foundation validated from a clean checkout at `022cc023865ffcba73a36e26101858e35df24aec`, branch `revival/v1.15-foundation`. Macro closeout is recorded in the final `PROJECT_STATE.md` update and completed execution plan. `main` remains `66a5ba67f0691b7d50a11fa873f4ed24c80a14ef`; no push or merge performed.

## Commits

| Commit | Result |
|---|---|
| `4ef9eeb` | Pre-existing foundation documentation baseline; not created by this execution |
| `e2f6720` | Full inventories, classifications, canonical/system/asset maps, proposal and pre-movement behavior fixture |
| `39ac756` | 393 `git mv` relocations, 0 content insertions and 0 content deletions |
| `fbd62e9` | Godot Mobile shell, typed GDScript, original Blender/GLB sample and validation |
| `637ea08` | Validation entry point, CI skeleton, 736 reference groups / 832 source image paths, usage documentation |
| `022cc02` | Stable LF Godot metadata on Windows; clean-import verification |

Evidence and macro closeout are subsequent documentation commits. The exact final closeout SHA is included in the task completion report; a commit cannot contain its own hash. `PROJECT_STATE.md` names the exact validated implementation/evidence revision rather than a circular self-reference.

## Resulting structure

```text
game/                  Godot 4.7.2 project, bootstrap, typed scripts/tests, runtime GLB
  data/                canonical/schemas/generated scaffolds; no duplicated gameplay data
  scenes/              app plus combat/market/heroes/arenas/ui scaffolds
  scripts/             core/presentation plus domain scaffolds
art/
  blender/shared/      procedural foundation_sample.blend
  exports/props/       validated GLB and provenance
  pipeline/            repeatable Blender authoring script
references/visual/     seven category catalogs; source images stay at indexed paths
docs/                  authoritative specs, migration reports, QA evidence, execution plans
tools/                 migration, validation, asset_pipeline and simulation scaffold
.github/workflows/     foundation CI skeleton
legacy/
  web-prototype/       complete, bootable v1.14.3 oracle
  archive-index/       pointers to the read-only census
.work/                 ignored archive, portable Godot, scratch checkouts and generated reports
```

## Moved and retained

The exhaustive old→new list is `repo_inventory.csv` (`disposition=git-mv`): 285 asset files, 45 JS modules, 16 data JSON files, 20 historical docs, 7 tools, 16 patch notes, historical README, HTML, web manifest and one preview. All relative paths remain intact inside the new web root. Every moved file preserves its original Git blob and working content.

All **427** baseline tracked paths were inventoried. **34** governance/scaffold paths stayed at isolation; the active v1.15 plan is archived separately on macro completion. No original data/card/hero asset was dropped. Root `README.md` is now production navigation, with its historical version preserved inside the prototype. Master/architecture/AGENTS decisions are unchanged.

The read-only copy retains **1,152 files / 549,296,468 bytes**: **299** original asset/data references, **405** nested web-checkout files and **448** nested Git metadata files. All paths and hashes pass retention validation. The external OneDrive original was never accessed or modified. No archive binary was imported wholesale or deleted.

## Duplicates and references

**86 exact disk-byte duplicate groups**, **193 member paths**: 68 cross-source groups, 17 within archive and 1 within repository. All retained. CSV includes representative comparison paths, not deletion approval or automatic canonical-source selection.

Git-normalized text hashes are recorded separately from working disk hashes; CRLF/LF-only copies are not falsely called byte-identical. The reference manifest preserves **832 image origins in 736 byte-hash groups** with rights unknown/reference-only. Unnamed images retain a provisional source-group category; they are not silently assigned to a hero. No legacy image was approved for final production.

## Canonical selections

- Branches: 12 master names and committed lowercase branch IDs; run rule 8/4.
- Cards: retained `data/legacy_deck_source.json` is the imported canonical identity/metadata source. Runtime `cards.json` is its behavior derivative. All 150 IDs, names, original effects, costs, rarity, levels, membership and legacy paths pass comparison; 90/36/24 rarities and 84/66 single/dual branches.
- Archive `vecchio/deck.json` differs only in 150 image paths; the other two old card files also differ in 24 level records. Retain these variants without merging them.
- Heroes: 16 existing runtime heroes remain the oracle; `hero.json.txt` has 20 candidate anthropomorphic concepts, with final approval deferred. Candidate aliases remain explicit.
- Economy/timers: JSON constants plus documented JS rules, including zero-preGold behavior and differing human/bot damage formulas. No balance changes.
- Arena/UI: retained manifests and indexed reference artwork; no final production asset approval.

Detailed choices/conflicts: `data_source_map.md`, `asset_source_map.md`, `js_to_godot_system_map.md`.

## Toolchain and validation

Godot **4.7.2.stable.official.ed1daf0bf** downloaded portably into `.work/tools` only after detecting/reporting installed tools and verifying the official ZIP digest. Blender **5.2.1 LTS** was already installed through Steam. Python **3.14.7**, Node **20.19.6**, Git **2.55.0.windows.3**, Java **17.0.15** detected. Existing Python 3.12/Pillow 12.1.0 used for the legacy arena gate. Android SDK/build tools/ADB and Godot export templates are absent; no global install/upgrade.

Full local foundation profile: **18 checks pass** on fresh checkout, including 393 unchanged relocations, all 1,152 archive hashes, 150-card metadata parity, five negative validator cases, 45 JS modules / 300 HTTP resources, eight seeds × three rounds repeated, asset validation, GLB structure/provenance, 2048×1152 arena layers/alpha, engine versions, headless import/boot, deterministic Godot vectors, skeleton/idle and real Mobile Vulkan captures at 1366×768 and 844×390.

Added source/runtime pipeline binaries total **103,023 bytes** (93,495-byte blend and two 4,764-byte GLBs); repeated reports/caches/tools are ignored. The intentional second GLB is generated and hash-checked for Godot's `res://` root. Screenshots are curated QA evidence, not copied legacy asset packs.

One pre-existing legacy grep-based readability test remains failed, explicitly recognized as a baseline exception; its modern component paths and browser behavior are checked separately. Android/iOS release and device-performance gates are not executable here; remote CI was not run. Exact commands/output, screenshots and visual review: `docs/qa/evidence/v1.15/` and `docs/qa/FOUNDATION_VALIDATION.md`.

## Debt and exact next step

Unresolved: exact semantics for 150 cards, player/bot effect asymmetry, biased JS shuffle, approximate shop probability labels, zero-preGold fallback, differing loss-HP formulas, latent sell API versus no-selling UI, legacy small-screen density, unknown visual rights/subjects, final rig/hero choices, SDK/device and export configuration.

Next is **v1.16 — Canonical Data Migration + Exact Card Semantics Framework**, with its executable scope in `docs/exec-plans/active/V1_16_CANONICAL_DATA.md`. Migrate portable canonical data and provenance with schemas/comparison reports first; define effect contracts and a semantics coverage registry without rewriting all 150 effects. Keep the web oracle unchanged. No final characters or multiplayer.
