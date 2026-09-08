# Status semantics — combat_v1.17.1

Every StatusInstance records instance ID/type, source/target identity, appliedAt,
duration/expiry/remaining, stacks/maxStacks, magnitude/parameters, stackingPolicy,
refreshPolicy, periodic interval/next tick and metadata (including debuff/source
provenance). Parameters are per application. There is no hidden global conversion
from a card's unspecified stack count to HP or damage.

## Policies

| Policy | Existing same-type/source/target instance |
|---|---|
| replace | Replace with a fresh instance and supplied parameters |
| refresh_duration | Keep stacks/magnitude, refresh according to refreshPolicy |
| add_stack | Add supplied stacks up to cap; retain expiry and magnitude |
| add_stack_and_refresh | Add supplied stacks up to cap, take stronger magnitude and refresh |
| independent_instances | Keep each application as a separately attributed instance |
| stronger_wins | Accept a strictly stronger magnitude; weaker/equal application is ignored |

Refresh policy is explicit: `none`, `reset` (now+duration), or `extend_if_longer`
(max(existing expiry,now+duration)). Refresh preserves the existing periodic phase;
replacement starts a new delayed phase. Identity keys include source so damage
attribution is not overwritten when different sources apply the same status.

## Implemented status types

- **shield**: positive independent scalar-capacity instances. Capacity is supplied
  in milli-HP; FIFO absorption updates it and expires an exhausted instance. When
  a stack grant is supplied, `capacity_per_stack_milli` must be explicit; zero or
  missing conversion is an error, not a guessed1HP/stack rule.
- **toxin / burn**: debuffs with explicit milli-damage/second/stack and duration.
  The unchanged hero skill source supplies14 damage/sec and3s where used. Damage
  is magic with `dot` tag, no crit/dodge/offensive proc chain. Source-normalized
  fixtures use max20 stacks and add_stack_and_refresh from the implemented legacy
  mechanism. This does not resolve the different weakening implied by card122.
- **wound**: debuff with explicit amplification basis points per stack, cap and
  duration. The actual legacy fallback is500bp when a hero applies Wound without
  an amp parameter; its use is source-linked. Applies to incoming damage, excluding
  any invented health-loss type. No automatic stack consumption is implied.
- **ice**: debuff with explicit slow basis points per stack, cap and duration;
  the implemented hero-skill fallback is1000bp. Combined slow cannot reduce basic
  cooldown/energy rates below35%. `slow` is presentation terminology for this type.
- **stun**: debuff preventing actions and pausing action cooldown progress. The
  explicit duration determines expiry; repeated applications refresh rather than
  creating extra action loops. Energy regeneration behavior is in COMBAT_RULES.

Toxin/burn/wound/ice fixture defaults above are evidenced implemented JS behavior,
with entity symmetry and deterministic scheduling deliberately specified here.
They are not an automatic interpretation of every card mentioning those branches.
Card077/115/149 stack applications need explicit status-parameter bindings in a lab
input; when absent they are rejected. Any such lab binding is labeled a mechanics
fixture, not a resolved production progression/balance value.

## Periodic timing

The status clock is the combat clock. For source-normalized DoT fixtures the
period is1000ms and first tick occurs at appliedAt+1000ms. A tick exactly at expiry
occurs before expiration. An application with shorter duration produces no full
tick; no implicit prorated final tick is invented. Durations used by canonical
hero fixtures are exact multiples of the chosen period, preserving total nominal
DPS×duration. Other explicit periods compute integer damage with remainder carry.

Refresh does not reset next-tick time, so frequent applications cannot indefinitely
postpone damage. Added stacks affect the next tick. Replacement resets phase.
Tick events retain source identity after its death; final combat resolution stops
future events. Uptime is measured as the union of active time per target/type,
not a sum that double-counts independent instances.

Remaining is derived from expiry-currentTime and never negative. All stack/cap,
duration/magnitude/interval/policy fields validate before combat. Status expiry
emits an event with its cause (time, absorption, dispel, replacement or death).
