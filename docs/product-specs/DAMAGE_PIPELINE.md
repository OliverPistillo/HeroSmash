# Damage pipeline — combat_v1.17.1

Only two damage types exist: `physical` and `magic`. `basic`, `skill`, `dot`,
`reflected` and `secondary` are source tags. No third DoT damage type is invented.
Raw hero skill `phys` is normalized to `physical`, preserving its value/provenance.

## Stable pipeline

1. Create a typed DamageEvent with source/target, base milli-amount, damage type,
   tags, critical/dodge eligibility, reflectability and parent event/chain depth.
2. Resolve offensive modifiers: basic-damage bonus or skill power, then critical
   multiplier for eligible basic/skill attacks. Crit chance clamps at9000bp as in
   JS; certain test inputs require explicit eligibility flags rather than new stats.
3. Resolve target Wound amplification from explicit active status magnitudes.
4. Physical damage subtracts flat armor. Magic has no invented resistance stat.
   Damage floor is1HP for ordinary attack intents, matching the implemented JS
   floor; periodic explicit damage has no per-tick minimum that changes its DPS.
5. Eligible physical hits roll target dodge. Magic/periodic/reflected damage do not
   dodge absent a separately specified effect. A dodge emits no HP/shield damage.
6. Absorb through active Shield instances in application order, with stable-ID ties.
   Consume all eligible shields as needed; the legacy first-shield-only behavior
   is a documented divergence. Emit each absorbed amount and residual capacity.
7. Apply remaining HP damage, clamped to current HP. Record attempted, mitigated,
   absorbed, actual HP loss and overkill separately. Attribution always retains
   original source even for periodic damage or a dead source.
8. Emit actual damage facts and execute damage-taken bookkeeping/triggers. Generic
   healing does not secretly cancel lethal damage. The lethal pipeline decides.
9. Resolve lethal interception, rebirth or final KO exactly once as specified.
10. Process post-event hit/status/heal reactions if eligible and still meaningful;
    a combatant with final KO cannot act/heal. Resolve all already-earned queued
    damage in the current chain before declaring the combat outcome.

## Reflection049

An eligible Evasion from DIVINE REFLECTION rolls exactly50%. On success it reflects
the dodged incoming amount **after offensive/Wound/armor computation, before any
Shield/HP application**. This makes the base explicit instead of conflating chance
with half damage. The reflected intent is magic, tagged `reflected`, noncritical,
nondodgeable and nonreflectable. Its fixed amount is not amplified a second time by
the reflector's offensive bonuses; the recipient's defensive Wound/Shield pipeline
still applies. There is no recursive reflection or new offensive on-hit proc chain.
Incoming actual HP-loss and lethal hooks remain eligible. Both entities use this rule.

JS divergence: the player always reflects half damage and the bot lacks that proc;
the text explicitly says50% chance and prohibits reflecting it again. Independent
source/target/parent metadata and a bounded reaction queue provide explicit protection.

## Source basis and unresolved cases

Flat armor, crit cap/multiplier, minimum attack damage and physical-only dodge are
implemented mechanics in the preserved CombatSystem, not keyword approximations.
The ordering above is the new explicit contract; differences from JS are recorded.
Unspecified health-loss damage cards are not coerced into a third damage type.
They remain unresolved until their bypass/mitigation behavior is specified.
