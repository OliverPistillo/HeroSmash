# v1.17 — Deterministic combat and balance lab closeout

Status: required implementation gates passed. Validated clean checkout:
`ec34ebb1a7bebc781c8f9806c045031d28597dcc`, branch
`revival/v1.17-combat-balance-lab`, baseline tag `v1.16-canonical-data` /
`87c1d0e4ba519e082feaf70848c84862acedc0ff`. Subsequent closeout changes are documents
and evidence only. Main remains `66a5ba67f0691b7d50a11fa873f4ed24c80a14ef`.

## Implementation and decisions

Typed GDScript `combat_v1.17.1`, canonical data `v1.16.1`, Godot
`4.7.2.stable.official.ed1daf0bf`. The resolver has no player/bot switch and no scene
dependency. Two stable IDs share one pipeline; sides are presentation metadata.
Integer milliseconds and next-event scheduling avoid frame delta and retain
resource/rate remainders. Same-time order: earned DoT ticks,expiry,periodic cards,
seeded-initiative action rounds. Skill priority and energy-triggered readiness at
the same timestamp are explicit and bounded.

Damage: intent → offensive/crit → target Wound → flat physical armor/floor →
physical dodge → FIFO shields → clamped actual HP loss/overkill → damage-taken
triggers → lethal notification → finite prevention →120 rebirth → finalKO → eligible
post-hit/status/heal reactions. Physical/magic are types; basic,skill,dot,reflected,
secondary are tags.049 is50% full post-mitigation reflection,magic/noncrit/nondodge/
nonreflectable,with depth/event limits. Earned simultaneous lethal DoTs can draw.

StatusInstance supports replace,refresh_duration,add_stack,add_stack_and_refresh,
independent_instances,stronger_wins; explicit none/reset/extend_if_longer refresh.
Shield,Toxin,Burn,Wound,Ice,Stun carry identity,source,target,time,stacks,cap,magnitude,
policy,periodic state,metadata. DoTs first tick after their interval; final tick at
expiry is included. Refresh preserves periodic phase; source and integer remainder
persist. No universal unspecified card-stack conversion was invented.

Thirteen IDs execute in this bounded phase:002,005,010,020,028,040,049,077,090,092,
115,120,149. Twelve retain the explicit v1.16 literal profile; numbered execution
is limited to the three single-level texts049/090/120.120 restores40%HP once and
clears debuffs.111 LAST STAND,097,132 and134 unreviewed IDs remain rejected.

All582 level records are exact executable lookups:450 Normal,108 Epic,24 Legendary.
JS acquisition increments by1 and rejects max. Its approximate effect×level values
are separately queryable/tested. Repeated generic level parameters do not establish
per-card operator semantics; no interpolation or speculative progression. ID071
remains Epic/cost300. Full open questions: `../migration/V1_17_UNRESOLVED_SEMANTICS.md`.

## Twelve scenarios,1,000 seeds each

Fixed seeds0–999,horizon45,000ms. A/B below are stable alpha/beta identities,
including in the mirrored scenario. Durations include timeouts, in seconds.

| Scenario / heroes | A wins | B wins | Draw | Timeout | Mean | Median | p90 | p99 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
|01 baseline: fireheart/steelbane |1 |999 |0 |0 |30.034 |29.808 |32.693 |34.616 |
|02 stats002/010: fireheart/steelbane |181 |819 |0 |0 |24.946 |25.000 |26.924 |28.847 |
|03 crit/dodge/040: shadowflame/windrider |984 |0 |0 |16 |36.363 |36.171 |40.426 |45.000 |
|04 Shield/healing028/077: ironfist/emberforge |0 |0 |0 |1000 |45.000 |45.000 |45.000 |45.000 |
|05 Toxin/115: nightshade/blackthorn |7 |898 |95 |0 |6.136 |6.000 |6.250 |7.000 |
|06 Wound/149: bloodthorn/blackthorn |240 |757 |3 |0 |27.945 |28.091 |30.091 |31.250 |
|07 Ice/Stun: frostfang/stormblade |0 |1000 |0 |0 |29.342 |29.223 |31.571 |35.144 |
|08 skill/Essence005/092: darion/duskwhisper |0 |10 |0 |990 |44.988 |45.000 |45.000 |45.000 |
|09 Rage/speed010: stormblade/darion |1000 |0 |0 |0 |20.408 |20.176 |21.930 |23.685 |
|10 reflection/lethal049/120/090: windrider/nightshade |0 |1000 |0 |0 |17.949 |18.000 |19.000 |20.000 |
|11 cross/timed005/020/028/149 vs090/115: bloodthorn/nightshade |0 |1000 |0 |0 |5.999 |6.000 |6.000 |6.000 |
|12 same states as11,reversed input/sides |0 |1000 |0 |0 |5.999 |6.000 |6.000 |6.000 |

The detailed scenario definitions are `game/data/combat/scenarios.json`. Hero stats
are unchanged,branch bonuses absent. Rage coverage uses the existing Stormblade
speed; it does not invent a Rage-stack conversion. Status templates are labeled
mechanics fixtures: Shield1HP/stack and Toxin14DPS/stack are explicit inputs,not
approved card semantics. Every scenario's first replay is saved and verified.

## Aggregate measurements and anomalies

12,000 unique fights:9,896 wins (82.467%),2,006 timeouts (16.717%),98 draws (0.817%).
Mean duration24.592s,median26s,p90/p99 both45s. Alpha wins2,413;beta7,483. These pooled
counts reflect intentionally different mechanics fixtures and the mirrored duplicate;
they are not a population win-rate or proposed meta.

Totals across both entities, in HP units unless stated otherwise:

| Metric | Total |
|---|---:|
|Physical actual damage |13,214,561.327 |
|Magic actual damage |6,981,396.617 |
|DoT subset of magic |4,198,700.692 |
|Actual damage taken |20,195,957.944 |
|Healing |1,122,602.658 |
|Shield generated / absorbed |111,904 /109,042 |
|Crits / eligible attempts |79,902 /701,500 (11.390%) |
|Dodges / eligible physical attempts |77,150 /667,847 (11.552%) |
|Basic attacks / skill casts |607,327 /94,173 |
|Status applications |93,233 |
|Death preventions / rebirths |1,000 /1,000 |
|Final KOs |10,092 |
|Events |2,424,013 |

Per-scenario/per-entity totals,means,remainingHP distributions,lethal sources and
status uptime are in `evidence/v1.17/lab-summary.json`. All12,000 per-fight records
are in `lab-metrics.jsonl.gz` (manifest line followed by records); no spreadsheet or
online analytics platform is needed. DoT overlaps magic: do not double-count it.

Observed extremes are retained: baseline B wins99.9%;Shield/healing always times
out;skill/Essence times out99%;Toxin averages6.136s with9.5% simultaneous deaths;
cross-timed resolves around6s. The unapproved hero-DPS Toxin fixture strongly affects
these experiments. None justified changing a hero,card,cost,rarity,economy or threshold.
Scenario10 records one prevention and one120 rebirth per fight,then finalKO.

## Determinism and performance

Two full corpus passes from the clean checkout: **27.675s** and **27.167s** on this
Windows host,4 Godot processes. Total lab wall time **62.800s**, including12 file
roundtrips and aggregation. The earlier production-workspace experiment took22.039s
and25.670s; all12,000 deterministic records match across checkouts. Runtime varies
with host load and is deliberately excluded from hashes.

Clean corpus per-fight wall time inside each concurrent process:mean8.114ms,
median6.336ms,p90 15.379ms,p99 26.688ms,max31.067ms. These are wall-time observations,
not CPU-exclusive timings or mobile budgets. Mean202 events/fight,p99 548,max584,
well below20,000. No limit failures,NaN/infinite gameplay values,stack breaches,
past events,duplicate final death or unexplained resurrection occurred.

Opt-in instrumented seed0 across12 scenarios:78,457µs total;30,940µs (39.4%) in
event serialization/hash,2,440 events,551,309 serialized bytes. Instrumentation
checks unchanged hashes. JSON/dictionary allocation and hashing are measured costs
to revisit if scale demands it. Batch does not retain event histories or copy the
v1.16 full-history snapshots per event. No premature optimization or100k benchmark
claim: full per-fight files and process parallelism will need measurement at that scale.

Zero replay/hash failures across12,000 repeated pairs,1,000 mirror pairs and12 full
file replay roundtrips. Both eventHash and resultHash match. Data hash:
`932aaad64f3c805dbb60439d36213e253d2a7eb3d25e0e66d42bfc7c2c5359bf`.

## Gates, failures and applicability

Clean checkout remained clean before and after all profiles:

- 15/15 v1.17 gates:2,173 combat assertions,289 replay/catalog assertions,five Python
  tests,4,167 live-JS oracle assertions,12,000 fights repeated and replay schemas.
- 11/11 canonical gates:all v1.16 tests retained,104 loader assertions,8,150 effect
  assertions,five Python tests/shared30 malformed cases,source/generation checks.
- 18/18 full Foundation gates:393 legacy web blobs,1,152 archive files,inventory,
  references,JS8seeds×3rounds repeated,HTTP/assets,GLB,Blender,Godot boot/RNG and
  Mobile renderer screenshots1366×768/844×390. Both sample images inspected.

Resolved development failures:cross-trigger seed5 exposed same-millisecond readiness
after energy gain; bounded initiative rounds now cover it. Extending schema checking
exposed the old validator's boolean-only additionalProperties and float/int nested
comparison limits; the new adapter and explicit relations handle them,without editing
the old validator. Evidence export also exposed CRLF/LF hash differences after Git
normalization; JSON now normalizes before hashing and Git-blob/checkout validation.
Final required checks have no failures. The two old JS readability
identifier failures remain the accepted unchanged baseline,not new regressions.

Not run/claimed:remote Actions/Linux execution,cross-platform replay equivalence,
physical Android/iOS performance,packaging/signing,final characters/arenas/UI/VFX.
Godot4.7.2 and Steam Blender5.2.1LTS passed actual checks. Python3.12.0 in the existing
venv,Node20.19.6,Java17.0.15 remain available. Android SDK/ADB/sdkmanager and export
templates remain absent; iOS requires Apple tooling. No tool/dependency/SDK/MCP installed.

## Files, retention and commits

Added `game/scripts/combat/` resolver/input/state/status/event/replay/catalog/scenario
classes; `game/data/combat/` authored rules/contracts/scenarios; `generated/v1_17/`
catalog/levels; versioned schema;combat/replay/CLI tests;Python migration/lab/gates;
read-only JS oracle;CI step;specs/ADR/reports/evidence. Existing bootstrap/presentation,
v1.16 EffectRunner,canonical datasets,art,legacy and external sources remain intact.
Only the completed v1.17 plan relocates active→completed at closure; no legacy moves.
All previous inventory/canonical choices remain unchanged.

Implementation commits:

- `75ea953` source-backed combat/level specification.
- `e672559` guarded catalog,models and582-level API.
- `b21cd28` deterministic entity-agnostic resolver and vectors.
- `73725b7` replay CLI,12-scenario lab,JS oracle and gates.
- `251e8be` opt-in event cost measurement.
- `5af0f0a` replay/metrics/divergence/unresolved documentation;first clean snapshot.
- `ec34ebb` explicit seed-list CLI and boundary gates;final validated implementation.

Evidence and macro-state closeout commits are listed in the task completion report.
No push or merge to main. Precise next phase:
`../exec-plans/active/V1_18_HERO_ROSTER_REFERENCE_LOCK.md`.
