# Hero Smash — Project State

**State date:** 2026-09-08
**Macro phase completed:** v1.16 Canonical Data + Effect Framework
**Phase status:** COMPLETE
**Branch:** `revival/v1.16-canonical-data`
**Required baseline:** `v1.15-foundation` / `80c098b256f5855d4c5dfb9869135fd2bad6c709`
**Validated implementation:** `e0185b4bb038a5314490e553c9374d6e3437927e`
**Committed evidence / next-phase scope:** `d04e340886487f5a4220120989fa230d284f825c`
**Main unchanged:** `66a5ba67f0691b7d50a11fa873f4ed24c80a14ef`

This is the documentation-only macro closeout after all required v1.16 and full
foundation gates actually passed. The closing commit is identified by `docs: close
v1.16 canonical data phase and update project state`; its own SHA is recorded in the
task completion report. No push or main merge was performed in this task.

## 1. Current production reality

`D:\Dev\HeroSmash` remains the production workspace. Godot **4.7.2 stable**, typed
GDScript, the **Mobile renderer**, real-time 3D characters, 2.5D arenas and
Android/iOS landscape remain locked. Blender **5.2.1 LTS** and the existing one-bone,
one-material animated cube/GLB fixture remain validated. No final art/UI production,
full combat port, full 150-card implementation or multiplayer was started.

Godot now loads **12 branches, 150 cards, 16 legacy-oracle heroes, 14 economy fields
and a 150-ID effect registry** through typed `BranchDefinition`, `CardDefinition`,
`HeroDefinition`, `EconomyDefinition` and `EffectDefinition` APIs. The catalog validates
before publishing and preserves a prior valid catalog on failed reloads. Scenes and
presentation remain independent; the bootstrap sample is unchanged.

Technology/product decisions changed: no engine, roster, card identity, branch,
economy or rarity decision. ADR 0003 adds technical data/validation/event contracts
and a bounded opt-in pilot profile. It does not approve unresolved progression or
combat rules as final game balance.

## 2. Canonical data and ownership

`tools/migration/canonical_data.py` is the sole writer of five generated datasets
under `game/data/canonical/` and two comparison reports. Six authored Draft 2020-12
schemas validate those datasets and the guarded pilot input. Envelope version is
`schemaVersion=1`, logical version `v1.16.1`. Source locking, LF-normalized SHA-256,
JSON pointers and original-text hashes preserve provenance across checkouts.

Authoritative card source remains
`legacy/web-prototype/data/legacy_deck_source.json`. Every raw field and all 582
level records remain intact. IDs 1–150 / `legacy_001`–`legacy_150`, names, original
text, costs, rarities, image paths and branch memberships pass source comparison.
Distributions remain 90 Normal / 36 Epic / 24 Legendary and 84 single / 66 dual
branch. **ID071 HEAVY BASH is Epic/cost300**, an actual source exception retained
without rebalance. The 12 canonical branch and 8-active/4-banned rules are unchanged.

Other inputs are unchanged `branches.json`, `economy.json` and `heroes.json` in the
web prototype. The 16 runtime heroes are explicitly `legacy_oracle`. The preferred
20 candidate concepts remain indexed in the archive pending v1.18, with no invented
stats or duplicate manually edited dataset. Alternate archive card fields are not
merged: vecchio/deck has 150 path differences; its two derivatives also differ in
24 level records. Full foundation validation rechecked these findings.

## 3. Pilot effects and honest coverage

`EffectRunner` executes **12 proposed base-text contracts** using integer units,
seeded local RNG with rejection sampling, explicit input order, chronological timers,
independent per-action stacking caps and transactional state/RNG/command logs.
Both actor IDs use the same operators; there is no card-ID dispatch.

Fifteen selected cards: **002, 005, 010, 020, 028, 040, 049, 077, 090, 092, 097,
111, 115, 132, 149**. Coverage includes flat stats, dual branches, chance, energy,
HP-loss thresholds, healing, critical hits, dodge, skill casts, stacking, timed
periodic damage and status application, cross-branch interaction and the explicit
`reflect_incoming_once` handler. No explicit currency/shop card was found in the
full original-text audit; reserved economy capabilities fail when requested.

The profile **`base_text_v1` must be explicitly requested**. It is not a fully
resolved leveled-card implementation. All numbered levels fail
`unsupported_progression`; raw generic level parameters are not interpreted.
The 135 unreviewed cards and three unresolved pilots fail clearly at binding.
Registry records link specification/tests and distinguish base-text execution from
rejection-only test coverage. None is falsely claimed exact/equivalent to an entire
legacy approximation.

Unresolved pilots: **097** damage/heal buffering and death order; **111** Shield
weakening/surviving HP; **132** Assault quantity and temporary-effect overlap.
Damage actions emit intents, without invented mitigation. Shield/Toxin/Wound stack
physics, duration/decay and damage remain unspecified; zero-HP facts fail pending a
death resolver. The prototype's player/bot asymmetry is documented, not silently
adopted or claimed as full parity. Full comparisons: `docs/migration/V1_16_PILOT_PARITY.md`.

## 4. Preserved legacy and structure

No legacy file was moved, renamed, deleted or edited in v1.16. All **393 web blobs**
and **1,152 archive files** retain their exact contents. The external OneDrive source
was not accessed. The v1.15 inventory, 86 exact duplicate groups/193 paths, 736
reference groups/832 origins and reference-only rights classifications remain valid
for their recorded scope. The historical inventory is not a new whole-repo census.

The web prototype remains bootable via:

```powershell
python -X utf8 legacy/web-prototype/tools/serve.py
```

Its 45 JS modules, 300 HTTP resources and eight-seed/three-round behavior oracle
remain validated. Production additions are schemas/generated JSON, typed models and
catalog under `game/scripts/core/data/`, the effect framework under `scripts/cards/`,
headless tests, migration/validation tools and documentation/CI gates.
Only the completed v1.16 plan moves from `active/` to `completed/` at closeout.

## 5. Toolchain

- Godot **4.7.2.stable.official.ed1daf0bf** remains at `.work/tools/godot-4.7.2/`.
- Existing Steam Blender **5.2.1 LTS** remains validated; no install/upgrade.
- Python **3.14.7** is available; the final clean run uses existing **3.12.0** in an
  isolated venv, with existing Python/Pillow used by foundation asset validation.
- Node **20.19.6**, Git **2.55.0.windows.3** and Java **17.0.15** remain available.
- jsonschema was detected absent before installing pinned validation dependencies
  only under ignored `.work/venvs/`. Python3.12's conditional typing-extensions is
  pinned too. No global dependency, engine, MCP or SDK installation.
- Android SDK/ADB/sdkmanager and export templates remain missing. Android/iOS
  package/signing/device gates and final mobile performance budgets remain deferred.

## 6. Executed validation and failures

Final implementation passed from a **fresh clone of the same branch with no prior
Godot cache**, remaining clean before/after:

- **11/11 canonical gates**: source lock/baseline/branch, full schema/raw metadata,
  generated-byte reproducibility, malformed data, fresh import and headless suites.
- Five Python tests, including the shared **30 malformed-data subcases**.
- **104 Godot loader assertions**, no failures.
- **8,150 effect assertions**, no failures; eight seeds ×400 input events repeated,
  known probability vectors, unbiased RNG rejection, actor-mirror symmetry, timer
  partition independence, thresholds/min/max/caps/order and rollback.
- **18/18 full local foundation gates**: unchanged archive/web, alternate-source
  parity, references, JS oracle, asset/Blender/GLB validation, headless boot and actual
  Vulkan Mobile rendering at **1366×768 and 844×390** on Radeon RX 7900 XT. Both sample
  screenshots were inspected; no new gameplay/phone UI claim is made.

Exact commands/output and limits: `docs/qa/evidence/v1.16/REVIEW.md`, `canonical.json`
and `foundation.json`. CI YAML was parsed locally and the dependency/canonical gate
steps checked. No remote GitHub Actions/Linux run is claimed.

First clean-checkout attempt failed because the initial data change had replaced
foundation Git attributes. The retained failure evidence and fixes restore **all**
v1.15 text/binary rules, with only additive JSON attributes. A fresh clone then
passed all gates. An early cost-uniformity assertion exposed ID071; the data was
preserved and validation corrected. No required final v1.16 failure remains.

The retained old JS readability script still fails its two v1.15 stale identifier
searches. The foundation gate verifies that accepted failure is unchanged. Not
run/applicable: remote CI/Linux, Android/iOS packaging/devices, final art/UI/VFX and
representative mobile performance. These are not reported as passes.

## 7. Debt and next macro phase

Full card semantics/progression, status physics, damage/death ordering and the three
ambiguous pilots need source-backed specifications. JS conflicts remain: UI3/helper4
shop slots, zero-preGold interest fallback, no-selling UI/latent API, player/bot HP-loss
formulas, passive/proc/healing asymmetry and biased random-comparator shuffle.
The pilot's snapshot/log copying needs profiling before production combat scale.
Roster/rig/reference rights, SDK/export/signing and physical-device QA remain later work.

**v1.17 — Deterministic combat simulation + automated balance lab**.
Plan: `docs/exec-plans/active/V1_17_COMBAT_BALANCE_LAB.md`. First settle the minimum
combat/status/death and progression specification; then integrate a headless intent
resolver and ordered derived-event queue for only the specified pilot. Run at least
12 representative scenarios ×1,000 fixed seeds, repeat exact replays and invariants,
record metrics/legacy differences before rebalance. Keep unsupported loadouts explicit.
Final roster/reference approval remains v1.18.

Full macro report and implementation commits: `docs/migration/V1_16_MIGRATION_REPORT.md`.
