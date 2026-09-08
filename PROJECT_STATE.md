# Hero Smash — Project State

**State date:** 2026-09-08
**Macro phase completed:** v1.17 Deterministic Combat Resolver + Balance Lab
**Phase status:** COMPLETE
**Branch:** `revival/v1.17-combat-balance-lab`
**Required baseline:** `v1.16-canonical-data` / `87c1d0e4ba519e082feaf70848c84862acedc0ff`
**Validated implementation:** `ec34ebb1a7bebc781c8f9806c045031d28597dcc`
**Committed evidence / next-phase plan:** `2259b10a3811e671981387059739504a723b5af1`
**Verified evidence integrity:** `f34752c2b34133bd7cccb866b735da62793da835`
**Main unchanged:** `66a5ba67f0691b7d50a11fa873f4ed24c80a14ef`

This documentation-only macro closeout follows all required executed gates. Its
commit is named `docs: close v1.17 combat phase and update project state`; the exact
closing SHA appears in the task completion report. No push or main merge occurred.

## 1. Production reality and decisions

`D:\Dev\HeroSmash` remains the production workspace. Locked direction remains Godot
4.7.2 stable,typed GDScript,Mobile renderer,real-time3D characters,2.5D arenas and
Android/iOS landscape. Blender5.2.1LTS and the existing animated sample GLB remain
validated. No final characters,arenas,production UI/animation,multiplayer,SDK,
monetization or online analytics were implemented.

The new headless resolver is authoritative for validated inputs under
**rulesetVersion `combat_v1.17.1`** and **canonicalDataVersion `v1.16.1`**. There is
one rule path for both stable combatant identities; preparation AI and sides are
outside gameplay. ADR0004 accepts execution/measurement boundaries,not final balance.
No hero stat,card value,cost,rarity,economy or branch threshold was tuned.

Integer millisecond scheduling advances directly to event boundaries and retains
resource/rate remainders. At a timestamp:earned periodic ticks,expiry,card intervals,
then seeded-initiative readiness rounds. A skill has priority; same-time energy
triggers can make another action ready without a graphical frame delay.

Damage order:offense/crit,Wound,flat physical armor/floor,physical dodge,FIFO shields,
actual HP loss/overkill,damage-taken bookkeeping,lethal notification,finite prevention,
rebirth,finalKO,eligible post-hit reactions. Types are physical/magic; basic,skill,
dot,reflected,secondary are tags.049 uses50% chance to reflect full post-mitigation
pre-Shield damage as magic,without crit,dodge or recursive reflection.

StatusInstance covers Shield,Toxin,Burn,Wound,Ice,Stun,source attribution and explicit
replace/refresh/add-stack/independent/stronger policies. Periodic ticks are delayed
and expiry-inclusive;refresh preserves phase. Lethal resolution is shared by every
source.120 has one original-text rebirth at40%HP,cleansing debuffs. General finite
prevention requires explicit fixture parameters; it does not invent LAST STAND111.

## 2. Canonical data and honest coverage

All v1.16 canonical datasets remain byte-identical:12 branches,150 cards,16 oracle
heroes,14 economy fields and150-ID effect registry. The8-active/4-banned branch rule
and distributions90 Normal/36 Epic/24 Legendary,84 single/66 dual remain unchanged.
ID071 HEAVY BASH remains Epic/cost300. Authoritative deck is still
`legacy/web-prototype/data/legacy_deck_source.json`; runtime branches/heroes/economy
remain the previously chosen sources. The20 newer roster candidates await v1.18.

New generated data under `game/data/generated/v1_17/` preserves all582 level rows
with provenance:450 Normal,108 Epic,24 Legendary. APIs return exact source rows,
parameters and separately labeled actual JS approximation values. Acquisition in
JS advances by1 and rejects max; no market implementation or interpolation was added.
Generic shared level templates do not prove canonical per-card operator bindings.

Thirteen IDs execute:002,005,010,020,028,040,049,077,090,092,115,120,149. Twelve retain
explicit `base_text_v1` literal fixtures with level0; numbered execution is restricted
to049/090/120 at level1.077/115/149 require labeled status templates. Lab Shield1HP/
stack and Toxin14DPS/stack are explicit experiment inputs,not approved card conversions.
The old EffectRunner and its v1.16 tests remain intact as an operator harness.

Unresolved:097 buffering/lethal ordering,111 Shield weakening/surviving HP,132 temporary
Assault units/overlap,009 lethal-window units/lifesteal,most numbered effects and
card-specific status parameters.134 IDs remain unreviewed;with3 unresolved pilots,
137 IDs reject unsupported bindings. No full150-card semantic rewrite is claimed.
See `docs/migration/V1_17_UNRESOLVED_SEMANTICS.md` and `CARD_LEVEL_PROGRESSION.md`.

## 3. Replay and laboratory

`CombatReplay` saves versioned inputs,seed,events,final state,data/event/result hashes;
verification regenerates and compares the complete envelope. Events carry stable
IDs,timestamp,sequence,parent,payload and resolved combat facts. Presentation can
consume those facts later; no UI integration or animation timing is claimed.

CLI supports list,run/save,input-file,verify,batch seed ranges,explicit seed lists,
custom horizons and opt-in profiling. Python only migrates,validates,orchestrates
Godot and aggregates measurements. `docs/qa/COMBAT_VALIDATION.md` gives commands.

The committed12-scenario corpus uses seeds0–999 and45,000ms maximum:baseline,stats,
crit/dodge,Shield/healing,Toxin,Wound,Ice/Stun,skill/Essence,Rage/speed,reflection/lethal,
cross-timed and identical states with reversed sides. All12,000 fights were repeated,
with zero event/result/hash differences;1,000 mirror pairs and12 file replay
roundtrips passed. A previous checkout's full deterministic metrics also match.

Final clean measurement:9,896 wins,2,006 timeouts,98 draws;mean duration24.592s,
median26s,p90/p99 45s;2,424,013 events,max584 per fight. Two full passes took27.675s
and27.167s with4 Godot processes;total lab including roundtrips/aggregation62.800s.
Per-fight wall time mean8.114ms,p99 26.688ms under concurrency. These are desktop
measurements,not phone budgets. Instrumented12 samples attributed39.4% of measured
time to event serialization/hash;no premature optimization or100k benchmark claim.

Extremes retained without tuning:Shield/healing100% timeouts;skill/Essence99%
timeouts;Toxin roughly6.1s with9.5% draws;several fixtures have100% one-sided wins.
These mechanics fixtures,including a mirrored duplicate,do not establish a meta.
All requested damage/heal/shield/status/uptime/crit/dodge/lethal/HP/runtime metrics
are in `docs/qa/evidence/v1.17/lab-summary.json` and12,000 compressed JSONL records.

## 4. Retention and resulting structure

No legacy/archive/art file moved,renamed,deleted or edited in v1.17. All393 web blobs
and1,152 archive files passed hash retention again. The external OneDrive source was
not accessed. Existing inventories,duplicate classifications and canonical/reference
choices retain their recorded scope;no new whole-repo census is claimed.

Added `game/scripts/combat/`, `game/data/combat/`, `game/data/generated/v1_17/`,
combat schema/tests/CLI,`tools/balance_lab/`,combat migration/validation/JS oracle,
ADR/specs/reports/evidence and a CI gate. The sample scene and production art remain
unchanged. Only `V1_17_COMBAT_BALANCE_LAB.md` moved active→completed using git mv;
v1.18's proposed roster/reference plan is now active. All foundation Git attributes
are retained;new data/evidence attributes are additive.

## 5. Executed gates and limitations

Final implementation passed from a clean same-branch local clone:

- 15/15 v1.17 gates:2,173 combat assertions,289 replay/catalog assertions,five Python
 tests,4,167 live-JS oracle assertions including582 level comparisons,seed-list
 boundary cases,12,000 fights repeated,mirrors,replay roundtrips and schemas.
- 11/11 canonical gates:104 Godot loader assertions,8,150 effect assertions,five
 Python tests/shared30 malformed cases,source generation/schema and clean checks.
- 18/18 full Foundation gates:inventory/archive/web/reference retention,JS oracle,
 assets/GLB/Blender,Godot headless import/boot/RNG and Vulkan Mobile sample images
 at1366×768 and844×390. Both sample resolutions were inspected.
- CI YAML parsed;full clean combat step checked locally. Artifact SHA-256,committed
 Git bytes,12,000 unique metric rows and12 aggregate hashes verified after checkout.

Resolved development failures:cross-trigger same-time readiness,schema adapter
limitations/numeric normalization,and report CRLF/LF checksum mismatch during
Git export. Final required gates have no failure. The old JS readability script's
2 stale identifiers remain the explicitly checked unchanged baseline exception.

Not run/claimed:remote GitHub Actions/Linux,cross-platform replay equivalence,
Android/iOS device performance/export/signing,final art/UI/VFX. These are unavailable
or non-applicable gates,not inferred passes. Complete commands/output,failures and
limits: `docs/qa/evidence/v1.17/REVIEW.md` and the three gate JSON reports.

## 6. Detected toolchain

Godot4.7.2.stable.official.ed1daf0bf and Steam Blender5.2.1LTS passed actual version
and execution checks. Python3.14.7 is available;final gates used existing3.12.0 venv
with pinned jsonschema dependencies. Node20.19.6,Git2.55.0.windows.3,Java17.0.15 remain
available. No engine,SDK,MCP,dependency or global tool was installed in this phase.
Android SDK/ADB/sdkmanager/export templates remain absent;Apple tooling/signing
remain necessary for iOS. Physical mobile profiling stays explicit future work.

## 7. Debt and next macro phase

Unproved card progression/status conversions and137 rejected effect IDs remain
visible. Economy questions stay separate:UI3/helper4 slots,zero-preGold interest,
latent sell API,player/bot run-HP loss formulas. JS passive/proc/heal/reflection
asymmetries were executed and documented as legacy divergences,not canonicalized.
The32-bit LCG needs statistical review before competitive balance conclusions.
Presentation event consumption,large-corpus profiling,rights/rig conventions and
mobile toolchain/device gates remain future work.

**v1.18 — Final hero roster + visual reference lock**:
`docs/exec-plans/active/V1_18_HERO_ROSTER_REFERENCE_LOCK.md`. Inventory the20 indexed
candidates,produce an explicit16→20 identity/migration matrix,prepare the complete
roster/reference/rights proposal for human product approval,and document shared rig/
GLB conventions. No guessed stat transfer,final art or balance tuning. Preserve this
combat baseline and its gates;only approved specs can authorize later replacements.

Full macro report: `docs/qa/V1_17_BALANCE_REPORT.md`.
