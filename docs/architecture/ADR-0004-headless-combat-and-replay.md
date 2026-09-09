# ADR 0004 — Entity-agnostic combat and reproducible measurement

Status: accepted architecture for the current v1.17 task. This does not approve
unproved card progression, missing status parameters or balance tuning.

## Boundaries

The authoritative resolver accepts two validated CombatantState inputs. It has no
player/bot flag and no market AI. Stable combatant IDs move with their state when
presentation sides are swapped; side labels are metadata outside simulation hashes.
An initiative permutation is seeded once from sorted IDs, and all tie handling uses
that order. Neither side nor dictionary insertion order changes gameplay.

The production simulation is typed GDScript and runs through Godot 4.7.2 headless.
Python only migrates/validates sources, orchestrates commands and aggregates results.
No second Python combat implementation is introduced.

## Clock, values and hashes

Use integer milliseconds with chronological scheduling. HP/energy/damage are
milli-units, percentages basis points and attack speed milli-attacks/second. Integer
rate accumulators retain remainders. Action readiness is rounded up to the next
millisecond rather than derived from rendering. No graphical frame delta is used.

At a timestamp: advance resources/cooldowns and uptime to that time; run due status
ticks (including a final tick exactly at expiry); expire statuses; run periodic
card rules; process ready actions in seeded initiative order. Every action and its
derived reactions resolve before the next action. Each phase uses stable instance
or binding order. The rules document specifies boundaries and timeout handling.

Canonical JSON hashing uses sorted object keys and integer values. Event hashes
are incremental SHA-256 of canonical event JSON lines; results hash the deterministic
final state/metrics/result. Wall-clock profiling and presentation sides are excluded.
Replay records include ruleset/data versions, initial state, seed, scenario ID,
ordered events, final state and both hashes. Replays regenerate and compare the
complete stream, not just trusting hashes copied from a file.

Lab runs stream events through the same hashing/metrics path without retaining
every event in RAM. One-fight debug replay retains the stream. No per-event full
history checkpoint from the v1.16 harness is used for batch combat; inputs validate
before combat begins and internal failures abort the result instead of producing a
successful partial replay. v1.16 APIs/tests remain intact.

## No speculative balance values

The v1.16 canonical datasets remain byte-identical. New generated combat inputs
reference their provenance and normalize representational units only. Raw hero
stats, card values, costs, rarities, economy and branch thresholds are unchanged.
Explicit original-card literal contracts and resolved single-level effects are
separate from numbered multi-level semantics. Exact source level values are
queryable even when their binding to an effect is unresolved.

StatusInstance owns an explicit magnitude, duration, cap and policies per source.
Legacy hero skill parameters and labeled mechanics fixtures are usable inputs;
they are not evidence for a universal Shield/Toxin stack conversion. Unknown
parameters, LAST STAND weakening and other ambiguous cards fail explicitly.

No online analytics, rendering/UI integration, new global tools or balance tuning.
