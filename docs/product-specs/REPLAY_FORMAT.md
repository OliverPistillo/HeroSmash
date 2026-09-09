# Combat replay format1

Entry point: `CombatResolver.new(catalog).run(input, record_events=false)`.
Invalid input returns `ok=false`, errors and no partial result. Internal execution
limits fail visibly; CLI refuses to save failed runs as successful replays.
`CombatReplay.create` captures the stream; `verify` regenerates and compares the
complete canonical envelope, including the supplied events and final state.

## Input and profiles

Required keys: `scenarioId`, `rulesetVersion`, `canonicalDataVersion`, `seed`,
`horizon_ms`, `combatants`, `sides`. Seed is unsigned32-bit; horizon1–45,000ms.
Exactly two unique stable IDs are required. `sides` is a permutation of those IDs
and affects presentation only. Unknown fields fail; no player/bot property exists.

`CombatCatalog.hero_input(heroId,id)` produces a complete input: stats, skill,
initial HP/energy, bindings, initial statuses, templates and finite death prevention.
`origin=canonical_hero` requires unchanged source stats/skill. `unit_fixture` allows
bounded mathematical vectors; committed lab scenarios exclusively use canonical
heroes. `CombatInput` checks types, bounds, references and semantics before combat.

Bindings contain `{cardId,profile,level}`. `base_text_v1` requires level0, meaning
no numbered level is asserted. `numbered` requires level1 of049/090/120. Duplicate
bindings, unsupported semantics and missing status parameters fail. Fixtures077/
115/149 require explicit templates; they do not settle production stack conversions.
Status `magnitude` means capacity per stack for Shield, milli-damage/sec/stack for
DoT, basis points/stack for Wound/Ice. Input shape is enforced by `CombatInput`.

## Envelope and hashing

Fields: `formatVersion=1`, `rulesetVersion=combat_v1.17.1`,
`canonicalDataVersion=v1.16.1`, `dataHash`, `scenarioId`, `seed`, `initialState`,
`events`, `finalState`, `eventHash`, `resultHash`.

`dataHash` hashes the compiled catalog, which embeds rules and six source hashes.
Generation and runtime loading compare definitions to the preserved canonical data;
all582 level rows are also source-checked. `game/data/schemas/combat.schema.json`
defines the envelope. Semantic validation/regeneration is stricter than its generic
replay payload objects. Python validates Draft2020-12; Godot expands the local
schema references into the existing supported subset and checks relations explicitly.

Canonical encoding: Godot4.7.2 `JSON.stringify(normalized,"",true,true)`, sorted
keys, integral JSON numbers normalized to integers. `eventHash` incrementally hashes
each canonical event plus LF. `resultHash` hashes the full final result, including
actors, metrics, RNG state, outcome and event count. Wall time, profiling, scenario
label and sides are outside simulation hashes. Versions,seed,initiative are in
CombatStarted; the complete initial input/envelope is checked by regeneration.

## Events and metrics

Events carry `sequence`, integer `at_ms`, `type`, stable `source`/`target`,
`parent_sequence`, `payload`. Sequence starts at1; parent precedes child. Status
refresh/stack change emits StatusApplied with resulting full snapshot; ignored
weaker grants and expiry causes have distinct events. Critical facts and basic/
skill/dot/reflected/secondary tags are in DamageApplied, linked to action parents.

Presentation can consume BasicAttack/SkillCast, dodge,absorption,damage,healing,
status,rebirth and KO facts without deciding gameplay. Continuous resource displays
may interpolate published input rates for display only. No animation durations,
production presentation or UI integration are claimed.

Damage counts actual HP loss. DoT overlaps magic and must not be added as a third
damage category. Crit rate is landed crits / eligible attempts, including dodged
attempts in the denominator. Dodge rate uses eligible physical attempts. Uptime is
the union per target/type. Lethal source is the most recent lethal crossing; events
retain every prevention/rebirth/KO source. Quantiles use nearest rank; median uses
the standard midpoint. Duration distributions include timeouts.

Batch mode hashes the same events without retaining them. `profile` measures
serialization/hashing and verifies unchanged hashes; its timing is outside replay.
