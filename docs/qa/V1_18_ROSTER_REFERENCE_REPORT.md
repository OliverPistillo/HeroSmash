# v1.18 — Roster and reference lock report

The production specification selects **16 launch + 4 reserve** from the exact 20
legacy candidates. It preserves source facts, records unsupported details as
proposals, separates visual direction from rights approval and leaves all combat
data and runtime code unchanged. Full local gates passed at implementation commit
`50fdb5820a4b5241885378dcb5215d68bf31920b` on
`revival/v1.18-hero-reference-lock`, baseline `337710e`.

## Commits and structure

| Commit | Change |
| --- | --- |
| `4d1cf44` | Exact candidate-source snapshot, reference inventory, hashes/duplicates and visual provenance review |
| `22db872` | Launch/reserve identities, matrices, sheets, production/brand contracts, generators and validators |
| `50fdb58` | Card body-size consistency, MAX proof correction retained, complete rig summary and validation regression |
| `8ba2380` | Curated passing evidence, reference navigation and precise v1.19 first-fighter proposal |

The documentation-only closeout commit is identified in `PROJECT_STATE.md` and
the task completion report. Post-evidence clean-checkout validation at `8ba2380`
passed all 12 roster gates and all 13 artifact length/SHA/Git-byte checks. `main` remains
`66a5ba67f0691b7d50a11fa873f4ed24c80a14ef`; no push or merge occurred.

```text
docs/product-specs/roster/
  hero_roster.json                 # single authored identity/selection source
  oracle_mapping.json              # 16 × 20 reasons and preservation requirements
  LAUNCH_ROSTER.md / SCORING_MATRIX.md / BRANCH_COVERAGE.md
  ORACLE_MIGRATION_MATRIX.md
  heroes/                         # 16 generated structured identity sheets
docs/references/visual/v1.18/
  hero_candidates.source.json / source_provenance.json
  review_decisions.json / reference_inventory.json / reference_duplicates.json
  RIGHTS_REVIEW.md / README.md
docs/art/
  CHARACTER_PRODUCTION_BIBLE.md
  rig_families / character_conventions / animation_contract
  expression_library / brand_ui_language / card_visual_language
  [authored JSON and generated uppercase Markdown for each contract]
  UNRESOLVED_AND_REFERENCE_GAPS.md
docs/qa/evidence/v1.18/             # four profiles, lab summary, diagrams, screenshots
tools/art/                        # reference/roster generation and phone proof
tools/validation/roster.py / test_roster.py
```

No legacy/archive/art file was moved, renamed, deleted or edited. The only phase
relocation at closeout is the execution plan from active to completed. The original
v1.15 census remains historical; the v1.18 overlay is the current review catalog.
Runtime `game/` and `legacy/web-prototype/` compare unchanged to the v1.17 baseline.

## Selected launch heroes

| Hero | Sourced primary / secondary | Proposed rig |
| --- | --- | --- |
| Solkael Lionheart | Guardian / Shield | medium_biped |
| Fenrox Bloodhowl | Rage / Assault | agile_biped |
| Kitsara Moonveil | Dodge / Precision | agile_biped |
| Aethryon Stormwing | Essence / Precision | medium_biped |
| Brumgar Earthhide | Guardian / Healing | heavy_biped |
| Sylvex Venomkiss | Toxin / Wound | serpentine |
| Rajuro Strikefang | Assault / Precision | medium_biped |
| Morvayne Blackquill | Essence / Wound | medium_biped |
| Karchar Reefbreaker | Power / Wound | heavy_biped |
| Elunor Lifethorn | Healing / Guardian | medium_biped |
| Oromir Frostclock | Essence / Ice | medium_biped |
| Rhazgor Crystalhorn | Shield / Power | heavy_biped |
| Vulkaryn Emberlord | Rage / Power | heavy_biped |
| Lupika Swiftkick | Dodge / Assault | agile_biped |
| Tortugan Runewarden | Shield / Essence | medium_biped |
| Skarvex Stinglash | Toxin / Precision | agile_biped |

Reserve: **Gruttar Tuskgold**, **Nyxara Nightstep**, **Zelkara Jadeclaw**,
**Kongaru Ironpalm**. Their complete source records, proposed visual/rig metadata,
scores and references remain in the 20-candidate dataset. Reserves reduce repeated
hammer/fist heavies and evasive blade archetypes; they are not discarded concepts.

Coverage: Assault 3, Guardian 3, Essence 4, Rage 2, Ice 1, Toxin 2, Shield 3,
Healing 2, Power 3, Precision 4, Wound 3, Dodge 2. Ice is the explicit exception:
only Oromir has sourced Frost/Ice. Guardian/Healing is the only duplicated unordered
launch pair, justified by the two available Healing identities and distinct
sustain-brawler/ritual-healer presentation. No new affinities or combat values were
invented to improve the matrix. All 15 score criteria are ordinal editorial values,
not performance, rights or balance measurements.

All 320 oracle/candidate cells are documented. Six oracle combined pairs have no
direct candidate equivalent; their systemic roles are distributed and the combined
kit gaps remain explicit. Shared concepts never merge original oracle IDs, stats,
skills or replay history. Future runtime migration requires a separately versioned
spec and parity validation; v1.18 does not claim that it has already happened.

## Canonical sources and reference coverage

Identity facts: exact `hero.json.txt` snapshot and its 20 source pointers. Branch
normalization is limited to Arcane→Essence, Venom→Toxin, Frost→Ice. Names/species/
titles/personality/roles/weapons are retained. Gender/presentation is unresolved
for every candidate. Shape, scale, material, motion and rig details remain proposal.
The named complete-roster board is the shared silhouette direction; named
`Solkael.png` is Solkael's primary gauntlet direction. Inconsistent branch icons,
rarity/evolution labels and anatomy in images do not override textual rules.

The audit contains **534 content groups, 832 origins**, **286 duplicate-content
groups and 298 extra origins**. 202 historical SVG groups were consolidated using
Git/archive bytes while retaining the old checkout hash and ID aliases; LF/CRLF
equivalence is not mislabeled as historical byte identity. All 270 tracked design
image paths and all 562 archive image paths are covered; QA screenshots are listed
separately. 38 significant boards were visually reviewed, not all 534 images.

Rights: **534 unknown-rights; zero production-approved**. Six references are
selected only for internal direction. Filename generator labels do not establish
ownership/licensing. Dota/Valve or similar proprietary material cannot pass into
production from stylistic usefulness. Unknown images remain indexed in existing
legacy paths, outside production admission; none were deleted or copied into assets.

For the 16 launch heroes, **49 partial view slots, 111 missing slots, zero certified
production-ready slots**. All need front/side/back, isolated silhouette, a consistent
combat stance and an expression sheet; weapon detail is missing except partial
Solkael gauntlets. Neutral/3/4-front/palette are partial concepts only. Each sheet
records the exact reference IDs and gaps. No missing production art was generated.

## Contracts and visual decisions

Four proposed rig families cover 7 medium, 4 heavy, 4 agile and 1 serpentine launch
hero. Shared semantic hierarchy, digit policy, retarget requirements and sockets
are specified, with tail/stinger/wing/hood/ear/feather extensions. No final rigs exist.

Locked shared conventions: 1 m/unit; floor-contact origin; skull-height measurement;
Blender -Y/front and +Z/up to Godot +Z/front and +Y/up; T-pose biped; `HeroSkeleton`;
30 fps; lowercase clip names; idle-only looping; no root motion; versioned GLB and
separate scene wrappers; material/texture/folder regexes. Ten required animations,
seven cosmetic marker names and ten shared expressions are machine-checked.
Damage remains exclusively resolver-driven. Final retarget/contact/GLB evidence
must come from the first admitted original fighter.

Brand: premium arcade/fantasy-tech, readable fighter silhouettes, opaque dark
surfaces, restrained gold accents, broad clipped planes and bounded motion/glow.
Rarity uses label plus frame shape, branch uses label plus glyph. Card hierarchy
fixes rarity/cost, title, branch row, art, effect summary and level/state rail.
Normal/Epic/Legendary and all acquisition/selection states are represented without
rewriting cards. Phone planning proofs at 667×375 and 844×390 have no text overlap;
body size is 14 px and main action target 44 px. Shipping fonts/glyphs and actual
physical-device usability remain unresolved.

## Executed gates, toolchain and limits

**56/56 profile checks passed**: v1.18 12, canonical 11, combat 15, foundation 18.
Seventeen new adversarial tests pass. Full combat repeats 12,000 fights, verifies
1,000 mirror pairs and 12 replay roundtrips, with zero deterministic differences
against v1.17. Full foundation preserves 393 web blobs and all 1,152 archive files,
boots Godot, validates the sample GLB/Blender and captures two Mobile screenshots.
Clean-checkout document generation and same-font phone-proof bytes reproduce.
CI configuration parses; remote execution is not claimed.

Godot 4.7.2.stable.official.ed1daf0bf and Steam Blender 5.2.1 LTS are operational.
Existing Python 3.14.7, Python 3.12.0 canonical venv/Pillow, Node 20.19.6, Git
2.55.0.windows.3 and Java 17.0.15 were reused. No tool/dependency was installed.
Android SDK/ADB/sdkmanager are not detected: ANDROID_HOME names an absent directory.
The Godot export-template directory exists but is empty. Apple signing/toolchain
and physical mobile QA are unavailable. Final-character asset/animation/VFX gates
are not applicable yet, and reference-production entry remains blocked by rights
and missing views. These limits are not represented as passing asset checks.

Final required tests failed: **none**. Development proof bearing/body-size/MAX and
rig-summary issues were corrected and rechecked. The two historical JS readability
failures remain the accepted, explicitly tested unchanged baseline. Details,
commands and artifacts are in `evidence/v1.18/REVIEW.md` and the gate reports.

## Preserved debt and precise next phase

Keep all v1.17 balance signals unchanged, including Shield/healing 100% timeout,
Toxin short fights, skill/Essence timeouts and other fixture anomalies. The 150
cards, 582 levels, 137 unsupported effect bindings, economy questions and replay
rules remain untouched. Visual debt: rights/provenance, minimum views, morphology
consistency, handedness/socket offsets, original font/glyph selection, combined-kit
mapping gaps and future representative mobile performance measurements.

**v1.19: Blender Character Pipeline / First Production Fighter**, proposed only.
Use Solkael base form after rights/original-design and reference packet approval;
then implement a disposable convention fixture, repeatable Blender exporter, one
original fighter with minimum rig/face/clips, a typed Godot event-consuming wrapper,
GLB/import checks, landscape footage and measured costs. Preserve the full previous
gates. Do not start other final heroes, evolution forms, arenas or balance changes.
The exact ordered proposal is `docs/exec-plans/active/V1_19_BLENDER_CHARACTER_PIPELINE.md`.
