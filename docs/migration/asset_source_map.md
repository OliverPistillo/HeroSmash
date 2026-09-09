# v1.15 asset classification and admission

Inventory first: `repo_inventory.csv`, `archive_inventory.csv`, `duplicate_report.csv`, and `asset_candidates.csv` identify every path and SHA-256. Exact duplicates are byte matches, not visual similarity or permission to delete. No archive binary is copied into Git in this phase.

| Group | Source before isolation | Classification | Retention / candidate destination |
|---|---|---|---|
| Beast Crucible layers | `assets/arenas/`, archive `arena1/`, loose floor PNG | Reference; potential production input only after review | Web copies move together to `legacy/web-prototype/assets/arenas/`; archive stays read-only. Future `art/blender/arenas` and validated runtime textures require admission. |
| Branch icons | `assets/branches/`, archive `rami/` | Reference; legacy UI dependency | Preserve exact bytes; index under brand-ui. |
| Card frames | `assets/cards/frames`, `assets/ui/market`, archive `carte/`, `vecchio/` | Reference; legacy UI dependency | Keep all variants, including duplicate frames. No rarity redesign. |
| 150 card SVGs / other branch SVGs | `assets/cards/` | Generated placeholders | Keep for the web prototype. Do not mistake them for final illustrations. |
| 150 old numbered card images | archive `vecchio/immaggg/` | Reference-only, rights unverified | Index without importing; file-number correspondence is a candidate link, not approved production art. |
| Hero SVGs and sprite PNG/JSON pairs | `assets/heroes`, `assets/sprites` | Generated placeholder presentation | Preserve in isolated web runtime. Do not promote to the real-time 3D pipeline. |
| Character sheets / generated image files | archive `sheet sprite/`, loose PNGs, `Nuova cartella/` | Visual reference; semantic subject requires review where unnamed | Character category with original names/hashes. No guessed hero identity from filenames. |
| UI / style sheets | `assets/final/`, old generated archive folders | Visual reference; “final” in a legacy path is not approval | Categorize in brand-ui, ux, arenas where identifiable; retain source location. |
| `.import` sidecars / nested `.git` | archive | Generated metadata / obsolete for production | Inventory and retain in place; no runtime import. |
| Foundation pipeline cube | New procedural Blender source script | Original safe pipeline sample | Explicitly allow `.blend` under `art/blender/`, `.glb` under exports/runtime; validate geometry, origin, material and idle animation. Not a hero or a final rig convention. |

## Reference library policy

`docs/references/visual/reference_manifest.json` indexes inventoried images with source path, hash, owner unknown, rights unknown, reference-only status, intended use and tags. `references/visual/<category>/README.md` points to the registry; binaries are not duplicated just to fill folders. Archive references require the local read-only archive. No third-party production asset or Dota asset is admitted.

No reusable production image has been approved in v1.15. This deliberately conservative classification preserves all candidates for later rights/style review. Per-file candidate list is `asset_candidates.csv`.
