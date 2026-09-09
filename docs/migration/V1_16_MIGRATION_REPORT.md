# v1.16 — Canonical data and effect framework

Macro phase: COMPLETE after executed gates on 2026-09-08.
Branch: `revival/v1.16-canonical-data`.
Baseline: `v1.15-foundation` / `80c098b256f5855d4c5dfb9869135fd2bad6c709`.
Validated implementation: `e0185b4bb038a5314490e553c9374d6e3437927e`.

## Result and ownership

Godot loads 12 branches, all 150 cards, 16 legacy-oracle heroes, all 14 economy
fields and a 150-ID semantics registry through validated typed APIs. Six authored
Draft 2020-12 schemas cover five generated datasets and the authored pilot input.
Envelope `schemaVersion=1`, logical generation version `v1.16.1`.

The sole generator is `tools/migration/canonical_data.py`; source locks pin ten
v1.15 data/runtime files. Each record has a source path, JSON pointer and source
hash. Cards preserve every raw field, including original ID/name/text/rarity/cost,
branches, all 582 level records, and image paths. Derived stable IDs remain
`legacy_001`–`legacy_150`. Counts remain 90 Normal / 36 Epic / 24 Legendary and
84 single / 66 dual branch, with the 12 canonical branches and 8-active/4-banned
product rule unchanged. No new run-selection behavior is implemented.

Canonical inputs: imported `legacy_deck_source.json`, `branches.json`, `economy.json`
and the 16 `heroes.json` oracle records under `legacy/web-prototype/data/`.
The 20 candidate concepts stay in the indexed archive pending v1.18. No candidate
stats were invented, no alternate card fields merged and no manual dataset copies
were introduced. Generated JSON is a reproducible derivative, not a second editable
source. Authored effect proposals are guarded by original-text hashes.

## Resulting structure and touched systems

```text
game/data/schemas/                 six authored schemas
game/data/canonical/               branches/cards/heroes/economy/effects.json
game/data/effect_contracts.json     fifteen guarded pilot proposals
game/scripts/core/data/            schema evaluator, catalog, base/hero definitions
game/scripts/branches/             BranchDefinition
game/scripts/economy/              EconomyDefinition
game/scripts/cards/                Card/Effect definitions, capabilities, actor/event/runner
game/tests/                       loader/effect suites and shared malformed corpus
tools/migration/                   generator and v1.15 source lock
tools/validation/                  Python tests and portable gate runner
docs/migration/                    generated comparison/matrix and this report
docs/qa/evidence/v1.16/             exact JSON results, failed first attempt, two PNGs
```

Runtime/data and presentation remain separate; no production scene was wired to
the pilot. Architecture, canonical policy, QA instructions, documentation index
and CI workflow were updated. FoundationRng gained state-copy/read APIs for
transactional effects; its original sequence is unchanged. Existing Git attributes
are retained, with additive LF rules for new generated JSON/reports.

Files moved: only the completed execution plan, from
`docs/exec-plans/active/V1_16_CANONICAL_DATA.md` to `completed/` at closeout.
No legacy file moved, renamed, deleted or edited. All 393 prototype blobs and
1,152 archive files are unchanged; the external OneDrive source was not accessed.
The 86 exact duplicate groups/193 paths recorded in v1.15 remain retained; v1.16
does not repeat or reinterpret that historical inventory as a new whole-repo census.

## Pilot selection, behavior and limits

The complete original-text → actual-JS → proposed-semantics matrix is generated in
`V1_16_PILOT_PARITY.md`. Selection maximizes available categories:

| IDs | Coverage | v1.16 execution |
|---|---|---|
| 002 | Flat stat modifier | +5 base damage at start |
| 005 | Dual branch, chance, energy | 60% attack proc, +1.5 MP |
| 010 | Stacking percentage/cap | +4% per attack, up to 20% |
| 020 | HP-loss threshold, cross-branch | Each 400 actual HP lost → 6 MP; remainder retained |
| 028 | Timed missing-HP healing/minimum | 1% missing HP each second, minimum 1 HP, capped |
| 040 | Critical condition/healing | Crit basic/skill hit →10 HP |
| 049 | Dodge, specialized handler | 50% full incoming magic intent; nonreflectable |
| 077 | Regeneration, chance, Shield | Regen event →30% chance of 4 Shield stacks |
| 090 | Periodic damage, Wound interaction | 20 magic damage intent/500ms; no Wound consumption |
| 092 | Skill cast and healing | Cast →50 HP |
| 097 | HP threshold/delayed buffering | Unresolved, rejected |
| 111 | Death prevention/timed Shield decay | Unresolved, rejected |
| 115 | Timed Toxin/DoT application | 4 Toxin stacks/second; tick physics unresolved |
| 132 | Dodge/temporary-stat overlap | Unresolved, rejected |
| 149 | Wound→Toxin chance/cross-branch | Wound application →30% chance of 4 Toxin stacks |

No original card explicitly mentions shop/currency mechanics in the full-deck
lexical audit; shop/economy actions and additional triggers remain reserved and
fail capability checks when requested. All requested future trigger/action names
are represented without introducing card-ID switches.

**Twelve executable contracts are not twelve fully completed leveled cards.**
`base_text_v1` is an explicit proposed base-text profile. All numbered levels are
rejected, because generic legacy parameters are not an approved progression rule.
There are 135 unreviewed records and three unresolved pilots, all rejected clearly.
Every registry record links specification/tests and distinguishes base-text execution
from rejection-only coverage. No complete card is falsely labeled exact/equivalent
to the old approximation.

Damage commands are pending typed intents; global mitigation/crit/dodge/death order
is deferred. Shield/Toxin/Wound stack physics, decay and damage are not invented.
Zero-HP facts fail explicitly until a death resolver is specified. Timer catch-up,
input bounds, per-action caps and state/RNG/log changes are transactional. Same
seed and input order reproduce the entire output; both actor IDs use the same rules.

## Legacy differences and discovered debt

- ID071 HEAVY BASH is Epic/cost300, unlike the other 35 Epic/cost200 cards. Preserved.
- 049 JS always reflects half damage for the player; the proposed contract uses
  a 50% chance of full incoming damage and an explicit nonreflection flag.
- 111 JS grants 1 HP and Shield equal to 35% maxHP for 3 seconds on death, while the
  text says 1200 stacks and an unspecified weakening. Not adopted as canonical.
- Player/bot ongoing passives, procs, healing modifiers and opening critical charges
  differ in JS. New isolated operators are symmetric, with no claim of full JS parity.
- UI 3 shop slots versus helper/probability 4, zero-preGold fallback, latent selling
  and incompatible player/bot HP-loss formulas remain explicit pending decisions.
- Full-deck exact semantics, level interpretation, status lifecycle, 097 buffering,
  111 weakening/survival and 132 stat/duration overlap require authoritative specs.
- The pilot command checkpoint copies/logs favor test clarity; profile and redesign
  as needed before using this mechanism for a high-volume production combat loop.

## Toolchain and validation

Existing Godot **4.7.2.stable.official.ed1daf0bf**, Blender **5.2.1 LTS** and
Mobile/Vulkan rendering remain validated. Python 3.14.7 was available for development;
the final clean run used existing Python **3.12.0**, matching CI's major/minor.
Node **20.19.6** supports the unchanged web oracle. Missing jsonschema was reported
before installation into ignored local virtual environments; direct and conditional
dependencies are pinned. No global install, SDK, Blender/Godot upgrade or MCP change.
Android SDK/ADB/sdkmanager and Godot export templates remain unavailable. Java 17
is present; Android/iOS packaging/device claims remain deferred.

Final fresh clone: **11/11 canonical gates and 18/18 full foundation gates pass**
on the validated commit, no prior Godot cache, clean before/after. Python: five tests
including 30 malformed subcases; Godot loader: 104 assertions; effects: 8,150 assertions,
eight seeds × 400 events repeated and actor symmetry. Source locks, all raw fields,
IDs/branches/distributions, generated bytes and alternate-source reports agree.
Exact commands/output: `docs/qa/evidence/v1.16/canonical.json`, `foundation.json`
and `REVIEW.md`. The two existing sample-scene screenshots were inspected.

Failed during development: the first clean-checkout gate exposed an introduced
Git-attribute regression, fixed by restoring every v1.15 rule and retesting a fresh
clone. The first cost-uniformity assertion exposed ID071 and was replaced with
source-preserving validation. Final required gates have no unresolved failure.
The retained old readability script still has its explicitly accepted v1.15 two
stale-identifier failures; the foundation gate verifies unchanged failure behavior.

Not run/not applicable: remote CI/Linux execution, Android/iOS export/signing/device
tests, final-character/arena/UI/VFX QA and representative mobile profiling. CI YAML
was locally parsed and canonical steps checked. No gameplay/UI/art production,
full CombatSystem port, full 150-card implementation or multiplayer was attempted.

## Commits and next phase

- `1efc5b8` — data ownership and bounded effect contract.
- `4aeb4ac` — schemas, generated datasets, source lock, full comparison/pilot matrix.
- `1da2f07` — typed transactional Godot catalog and schema loader.
- `30552dd` — seeded effect framework, pilot implementations and regression tests.
- `1e5c8a4` — local/CI gate runner and architecture/QA documentation.
- `845f767` — pin the Python 3.12-only transitive dependency.
- `e507533` — repair import LF handling and gate-result reporting.
- `e0185b4` — retain all existing foundation text/binary attributes.

Evidence/next-plan and documentation-only state closeout follow these implementation
commits; their SHAs are recorded in PROJECT_STATE and the task completion report.
No push or main merge was performed. Main remains
`66a5ba67f0691b7d50a11fa873f4ed24c80a14ef`.

Next: `docs/exec-plans/active/V1_17_COMBAT_BALANCE_LAB.md`. Specify combat/status/death
and progression first, build a minimal actor-symmetric headless intent resolver,
then execute a 12-scenario × 1,000-seed lab with exact replay/invariant comparison
before any rebalance. Keep unresolved loadouts excluded; roster/reference approval
remains v1.18.
