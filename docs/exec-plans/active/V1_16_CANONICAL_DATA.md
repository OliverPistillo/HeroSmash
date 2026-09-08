# v1.16 — Canonical Data Migration + Exact Card Semantics Framework

Status: executing on `revival/v1.16-canonical-data`, baseline tag
`v1.15-foundation`, commit `80c098b256f5855d4c5dfb9869135fd2bad6c709`.

Current task overrides the illustrative pilot size below with 15 representative
cards. Scope and unresolved product decisions are specified in
`docs/architecture/ADR-0003-canonical-data-and-effect-contracts.md`.
Python 3.14.7 and Godot 4.7.2 were detected before changes. `jsonschema` was absent;
dependencies are isolated under `.work/venvs/canonical-data/`, never installed
globally. Android, Blender, MCP and global engine installations are unchanged.

## Preconditions

- v1.15 state is COMPLETE, with `docs/migration/V1_15_MIGRATION_REPORT.md` and reproducible Godot bootstrap.
- Read root governance in order, canonical data policy, v1.15 source/system maps and QA gates.
- Preserve the unmodified web oracle at relocation commit `39ac756` and the recorded behavior fixture. Do not rerun its legacy importer.
- Use Godot 4.7.2, typed GDScript and existing tooling; detect/report before adding dependencies.

## A — Lock portable data contracts before transformation

- [ ] Define versioned JSON schemas in `game/data/schemas/` for branches, cards, economy and candidate hero provenance.
- [ ] Extend `docs/product-specs/CANONICAL_DATA.md` with exact field names, normalization rules, provenance fields, schema version and ownership (authored versus generated).
- [ ] Source cards from `legacy/web-prototype/data/legacy_deck_source.json`; retain source SHA and every raw field. Do not merge alternate archive levels or image paths.
- [ ] Preserve 150 IDs 1–150 plus stable `legacy_NNN` links, original names/effect text, costs, rarity, branch membership, level metadata and original image paths.
- [ ] Define only the documented normalization set: canonical branch casing, Guadian→Guardian for the known card typo, and Arcane→Essence / Venom→Toxin / Frost→Ice for candidate concepts. Unknown values must fail validation.

## B — Generate canonical datasets and comparison reports

- [ ] Build a deterministic, dry-run-capable importer under `tools/migration/`; write canonical outputs only after schema and source checks pass.
- [ ] Generate `game/data/canonical/branches.json`, `cards.json`, `economy.json`; each derived dataset records its source/provenance and has exactly one generation path. Old raw files remain archival input, not a second editable production source.
- [ ] Preserve the 16 runtime heroes as oracle fixtures. Import the 20-character file only as a clearly marked candidate dataset if needed, without final roster approval or gameplay replacement.
- [ ] Add typed Godot loaders with explicit errors for malformed/unknown records, and tests that work without rendering.
- [ ] Compare counts (150 cards, 12 branches, 90/36/24 rarities, 84/66 branch membership), unique IDs, all raw metadata, normalized memberships and schema validation.
- [ ] Report alternate-source differences and a no-loss source→canonical field mapping. Do not silently fix wording, rebalance or delete legacy records.

## C — Specify semantics and preserve unresolved choices

- [ ] Define an effect contract covering triggers, conditions, targets, numeric values/units, durations, stacks, limits, event ordering, source-card provenance and deterministic RNG ownership.
- [ ] Create a semantics registry for all 150 IDs with honest statuses such as `unreviewed`, `specified`, `implemented`, `tested`, plus links to specification and tests. Numeric-key coverage must never imply exact card coverage.
- [ ] Resolve/document contracts separately for 3 UI shop slots versus 4 helper/probability defaults, zero-preGold interest, no-selling UI versus latent sell API, player/bot effect asymmetry and differing HP-loss formulas. No behavior correction without an explicit accepted spec decision.
- [ ] Use `legacy_002` (SHARP EDGE) as the first simple passive specification candidate. Use `legacy_009` (BERSERKER FRENZY) and `legacy_111` (LAST STAND) to expose trigger/death-order questions; do not invent missing semantics or claim their approximate JS implementations are exact.
- [ ] Implement only the minimum typed framework and a small approved pilot needed to prove contracts. Do **not** implement all 150 effects in this phase.

## D — Validation and closeout

- [ ] Full foundation profile remains green; no web blob or archive hash changes.
- [ ] Run schema/metadata comparison, malformed-input/unknown-alias rejection, deterministic import repeatability, Godot loader tests and seed/event tests for any implemented pilot.
- [ ] Publish `docs/migration/V1_16_DATA_COMPARISON.md` with exact differences and semantics coverage; no unexplained changed records.
- [ ] Update state only when the phase is complete; record commits, chosen rules, tests and remaining semantics debt.
- [ ] Prepare v1.17: deterministic combat simulation, player/bot symmetry decisions, event/replay contract, and automated balance lab before rebalancing.

## Excluded

Final heroes/rig production, final arenas, full 150-effect combat rewrite, multiplayer, economy/rarity rebalance without specification, mobile store packaging, and global toolchain upgrades.
