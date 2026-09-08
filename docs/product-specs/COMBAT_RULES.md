# Combat rules — combat_v1.17.1

This ruleset is authoritative for validated inputs to the headless resolver. It
defines execution, not a final balanced roster or a solution to all 150 card texts.
CanonicalDataVersion remains `v1.16.1`. See ADR0004 and the status/damage/death specs.

## Input and identity

Two combatants have unique stable string IDs, unchanged oracle hero definitions,
explicit effect bindings and optional labeled mechanics-fixture statuses. Preparation
AI/player identity is absent. Side labels are presentation metadata. Sorting inputs
by identity precedes seeded initiative; swapping sides preserves event/result hashes.
All gameplay numbers are bounded finite integers after documented unit conversion.

A loadout can request a resolved single-level card or the explicit `base_text_v1`
literal contract from v1.16. The latter is a mechanics fixture, not an assertion
about level1 or higher. Unsupported level/effect/status-parameter bindings fail
before any fight. Hero statistics are not edited to improve lab outcomes.

## Time and readiness

- Time unit:1ms. HP/damage/energy:0.001 units; chances/multipliers:1bp. Converting
  legacy decimal metadata rounds to the nearest representable unit and checks the
  conversion error; IEEE spelling noise such as0.09000000000000001 is not balance.
- Maximum fight duration:45,000ms, from the existing combat horizon. Initial basic
  and skill cooldowns are ready; energy starts at0, maximum100 units, matching the
  hero factory. A skill has priority over a basic when both are ready.
- Energy regeneration uses the unchanged hero `stats.regen` (mana, not HP). Skill
  energy cost/CD/power come from the hero record. Basic interval is at least250ms,
  matching the current resolver's cap; rate accumulators preserve integer remainder.
- Ice slows basic cooldown progress and energy regeneration; the minimum speed
  multiplier is3500bp from the existing implemented Ice rule. Skill cooldown itself
  is not slowed. Stun pauses basic/skill cooldown progress and allows30% base energy
  regeneration, matching the actual implemented status behavior for either entity.
- Resources advance only to the next event boundary. Ready actors act once, then
  their next readiness is calculated; there is no dependence on frame frequency.
- At an exact timestamp: status ticks, expiry, card intervals, actions. Within each
  phase: seeded initiative, then stable status/binding/action order. Nested damage
  and resulting reactions complete before the next action. First card interval is
  delayed by its period. There is no retroactive tick on application.
- Events at45,000ms resolve before the timeout decision. If no final KO exists,
  result is explicitly `timeout`, with relative-HP leader reported as a metric,
  not a fabricated win. This differs intentionally from JS's timeout win/tie bias.

## Card event bridge

The v1.16 literal contract quantities are preserved; their triggers now consume
resolver facts. `basic_attack` precedes offensive damage calculation, so 010's
new stack applies to that attack. `basic_hit`/`skill_hit` mean a non-dodged hit,
including full shield absorption; critical-heal conditions use its resolved crit.
`damage_taken` receives actual HP lost, excluding absorption/overkill.
`heal` receives actual positive healing and an explicit regeneration category.
`status_applied` belongs to the applying source and identifies the target/status.

Trigger reactions are queued in stable rule order. Damage tagged `reflected` or
`secondary` cannot create new offensive on-hit chains; incoming damage/loss/death
reactions remain allowed. Effects never use a player-only fast path. Numeric/input,
event-count and reaction-depth limits fail the run visibly, not as a normal timeout.

## Explicit non-decisions

No market formula, branch synergy rebalance, XP/Guardian model or general multi-level
effect scaling is introduced. Current legacy branch bonuses remain reference unless
explicitly used as labeled fixtures. 097/111/132 remain unresolved; LIGHTBRINGER120
has an explicit single-level rebirth contract in the lethal specification.
