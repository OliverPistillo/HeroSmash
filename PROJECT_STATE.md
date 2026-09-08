# Hero Smash — Project State

**State date:** 2026-09-08
**Macro phase completed:** v1.18 Final Hero Roster + Reference Lock
**Phase status:** COMPLETE — specification/reference audit; no final asset production
**Branch:** `revival/v1.18-hero-reference-lock`
**Required baseline:** v1.17 / `337710e362b1df008b74cbb1e2ba6d1c58d2f2da`
**Validated implementation:** `50fdb5820a4b5241885378dcb5215d68bf31920b`
**Committed evidence / next-phase proposal:** `8ba23800db233878d16432a8509df328061e8f6f`
**Post-evidence clean-checkout integrity:** PASS at `8ba23800db233878d16432a8509df328061e8f6f`
**Main unchanged:** `66a5ba67f0691b7d50a11fa873f4ed24c80a14ef`

This documentation-only closeout follows all required executed gates. Its commit
is named `docs: close v1.18 roster phase and update project state`; the exact closing
SHA is in the task report. No push, main merge or v1.19 execution occurred.

## 1. Production reality and decisions

`D:\Dev\HeroSmash` remains the production workspace. Direction is unchanged: Godot
4.7.2 stable, typed GDScript, Mobile renderer, real-time 3D characters, 2.5D arenas,
Android/iOS landscape, Blender 5.2 LTS and validated glTF/GLB interchange. Runtime
remains the v1.17 headless combat laboratory plus the foundation sample. No final
character, rig, animation, arena, production UI, multiplayer, SDK or global
dependency was produced/installed in v1.18.

The current owner task authorized deciding 16 launch + 4 reserve, superseding the
earlier plan's separate roster-selection approval step. It did not establish art
rights or source-unsupported attributes. Identity selection and shared conventions
are specified; visual interpretations remain explicit proposals and rights/views
remain unresolved. This separation is part of the completed specification.

## 2. Roster and coverage

Launch: Solkael Lionheart, Fenrox Bloodhowl, Kitsara Moonveil, Aethryon Stormwing,
Brumgar Earthhide, Sylvex Venomkiss, Rajuro Strikefang, Morvayne Blackquill,
Karchar Reefbreaker, Elunor Lifethorn, Oromir Frostclock, Rhazgor Crystalhorn,
Vulkaryn Emberlord, Lupika Swiftkick, Tortugan Runewarden, Skarvex Stinglash.

Reserve: Gruttar Tuskgold, Nyxara Nightstep, Zelkara Jadeclaw, Kongaru Ironpalm.
All 20 original IDs/records remain retained. The single authored specification is
`docs/product-specs/roster/hero_roster.json`; 16 sheets and selection/scoring/coverage
matrices are generated. The exact source snapshot/provenance is under
`docs/references/visual/v1.18/`.

Coverage: Assault 3, Guardian 3, Essence 4, Rage 2, Ice 1, Toxin 2, Shield 3,
Healing 2, Power 3, Precision 4, Wound 3, Dodge 2. Ice is the documented exception:
only Oromir has sourced Frost/Ice. Guardian/Healing is the only duplicate unordered
launch pair, retained for Brumgar sustain brawling versus Elunor ritual healing.
Fifteen scoring criteria support systemic coverage, differentiation and production
cost decisions; scores do not measure balance or rights clearance.

Names/species/titles/personality/roles/weapons are sourced. Arcane→Essence,
Venom→Toxin and Frost→Ice are the only aliases. Gender/presentation is unresolved
for all 20. Body, scale, material, motion and rig details are proposals. Art badges,
anatomy transformations, rarity labels and unlock levels do not override text rules.
The 320-cell oracle matrix records conceptual matches, merge/split requirements
and six missing combined affinity pairs. No original oracle ID, stat, skill or
replay identity was merged/replaced; combined-kit numeric parity is not claimed.

## 3. References and production contracts

The current v1.18 catalog covers 534 canonical content groups and 832 origins:
270 tracked design image paths and 562 archive image paths. There are 286 duplicate
content groups and 298 extra origins. 202 historical SVG checkout groups consolidate
under Git/archive bytes; old IDs and working hashes remain visible so LF/CRLF
equivalence is explicit. The v1.15 manifest remains the frozen historical census.
QA screenshots are explicitly excluded from design-reference selection.

38 significant boards were visually reviewed. Six images are selected only for
internal direction, including the named complete roster and Solkael gauntlet sheet.
All 534 groups are unknown-rights; zero are production-approved. Tool-name filenames
do not prove ownership/license. Dota/Valve and similar proprietary references cannot
become usable production art from stylistic usefulness. Images remain indexed at
existing legacy paths; none were deleted or copied into production assets.

The 16 launch packets have 49 partial view slots and 111 missing slots; zero of
160 slots is certified production-ready. Front/side/back, isolated silhouette,
consistent combat stance, expression sheets and nearly all weapon-detail views
are missing. Each identity sheet records reference IDs and gaps. **All final
character production entry gates remain closed** until rights/original design
and a consistent ten-view packet are approved. Classification/specification gates
are complete; no missing production art was generated.

Four proposed rig families cover 7 medium bipeds, 4 heavy bipeds, 4 agile bipeds and
Sylvex's serpentine form. Hierarchy, fingers, rest/retarget requirements, sockets,
tail/stinger/wing/hood/ear/feather extensions are documented; no rigs were built.
Shared conventions lock meters, contact origin, skull-height measurement,
Blender -Y/front/+Z/up to Godot +Z/front/+Y/up, T-pose bipeds, HeroSkeleton, versioned
GLB/wrapper/material/texture names, 30 fps and no root motion. Ten animations,
seven cosmetic markers and ten expressions have validated contracts. Resolver
event IDs/time alone govern damage; callbacks cannot calculate/apply it.

Brand/Card Language v1 defines dark opaque surfaces, restrained gold, broad clipped
planes, bounded glow/motion, readable typography, labels plus rarity/branch shapes
and touch targets. Normal/Epic/Legendary, single/dual affinity, levels and all card
states have fixed hierarchy. Four synthetic phone diagrams demonstrate bounded
text/no overlap at 667×375 and 844×390, 14-px body text and 44-px action targets.
They are conceptual layout evidence, not final UI or physical-device approval.

## 4. Preserved simulation and canonical data

All of `game/` and `legacy/web-prototype/` compare unchanged to v1.17. Resolver
ruleset stays `combat_v1.17.1`, canonical version `v1.16.1`, dataHash
`932aaad64f3c805dbb60439d36213e253d2a7eb3d25e0e66d42bfc7c2c5359bf`.
Damage/status/lethal/replay rules remain authoritative in the v1.17 specs/ADR 0004.
No stats, effects, costs, rarity, economy or thresholds were tuned.

Data remains 12 branches, 150 cards, 582 exact levels, 16 oracle heroes, 14 economy
fields and the 150-ID effect registry. The 8-active/4-banned rule, 90 Normal/36 Epic/
24 Legendary and 84 single/66 dual distributions are unchanged. Deck authority is
`legacy/web-prototype/data/legacy_deck_source.json`, with the previously selected
branches/heroes/economy sources. Candidate metadata is not a runtime replacement.

Thirteen effect IDs execute in limited profiles: 002, 005, 010, 020, 028, 040, 049,
077, 090, 092, 115, 120, 149. Numbered execution remains restricted to 049/090/120
level 1; other literal fixtures use level 0. 134 unreviewed + 3 unresolved IDs
reject unsupported bindings. No full card-semantic rewrite is claimed. Shield
1HP/stack and Toxin 14DPS/stack remain experiment inputs, not approved card values.

The repeated lab retains 9,896 wins, 2,006 timeouts, 98 draws; mean duration
24.592 s, median 26 s, p90/p99 45 s and 2,424,013 events. Shield/healing 100% timeout,
skill/Essence about 99%, Toxin roughly 6.1 s and all other v1.17 anomalies remain
observed fixture signals, not roster scoring or balance decisions.

## 5. Executed gates and retention

Final full profiles at `50fdb58` from the clean same-branch clone passed:

- 12/12 v1.18 checks, including 17 adversarial tests, 20 sources, 16+4 selection,
  12 branches, 320 cells, reference scope/hashes/rights, rigs/names/expressions,
  contrast, generated documents and phone proof.
- 11/11 canonical checks, including 104 loader and 8,150 effect assertions,
  source/schema generation, Python/shared malformed cases and clean checks.
- 15/15 combat checks, including 2,173 combat and 289 replay/catalog assertions,
  4,167 live-JS assertions, all 582 levels, two 12,000-fight passes, 1,000 mirrors
  and 12 replay roundtrips. Zero deterministic metric/event/result regressions.
- 18/18 full local foundation checks: 393 web blobs and all 1,152 archive files
  preserved; JS launch/assets/oracle, Blender/sample GLB, Godot import/boot/RNG
  and two actual Vulkan Mobile sample screenshots. Both resolutions inspected.
- Same-font clean-checkout phone re-render reproduced all five artifacts exactly.
  CI YAML parsed. At evidence commit `8ba2380`, all 12 roster checks and all 13
  curated artifact lengths/SHA/Git-blob comparisons passed again with a clean tree.

No final required test failed. Development font-bearing/body-size/MAX and readable
rig-summary issues were corrected. The two historical JS readability failures
remain the explicitly verified accepted negative baseline.

No legacy/archive/art file moved, renamed, deleted or edited. The external OneDrive
source was not accessed. Only the v1.18 plan moves active→completed at closeout.
Commands, artifacts and limits: `docs/qa/evidence/v1.18/REVIEW.md` and four gate JSONs.

## 6. Toolchain and unavailable checks

Godot 4.7.2.stable.official.ed1daf0bf and Steam Blender 5.2.1 LTS passed actual
version/execution checks. Python 3.14.7, the existing Python 3.12.0 canonical venv,
Python312/Pillow, Node 20.19.6, Git 2.55.0.windows.3 and Java 17.0.15 were reused.
No engine, SDK, MCP, package or global dependency was installed.

ANDROID_HOME points to absent `C:/Users/olive/AppData/Local/Android/Sdk`; adb and
sdkmanager are not on PATH. The export-template root exists but is empty.
Android/iOS package/device tests, Apple signing/toolchain, physical mobile
performance, remote GitHub Actions/Linux and final character GLB/rig/animation/VFX
validation were not run or claimed. These are unavailable/future asset gates,
not inferred passes. Final budgets await representative fighters and an arena.

## 7. Debt and next macro phase

Visual debt: rights/provenance and ten-view packets; gender/presentation/voice;
consistent morphology/evolution policy; dimensions, handedness/socket offsets,
face mapping; licensed shipping font/original glyphs; six combined oracle kit gaps;
actual retarget/contact/performance measurements.

Existing gameplay debt remains: 097 timing/lethal buffering, 111 Shield weakening/
surviving HP, 132 Assault overlap, 009 lethal-window units/lifesteal, most numbered
bindings/status conversions; market UI3/helper4 slots, interest, latent sell API,
player/bot run-HP formulas, documented JS divergences and LCG statistical review.

**Next proposed phase: v1.19 — Blender Character Pipeline / First Production Fighter.**
`docs/exec-plans/active/V1_19_BLENDER_CHARACTER_PIPELINE.md` is proposed, not started.
Solkael base form is the first candidate after rights/reference preflight; then
a repeatable Blender fixture/exporter, one original fighter, minimum rig/face/clips,
typed Godot event wrapper, import/animation checks and measured landscape evidence.
No other final heroes, evolution forms, arenas, balance changes or automatic SDK work.

Full macro report: `docs/qa/V1_18_ROSTER_REFERENCE_REPORT.md`.
