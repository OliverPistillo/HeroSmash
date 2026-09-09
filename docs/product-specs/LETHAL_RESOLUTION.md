# Lethal/death resolution — combat_v1.17.1

All damage sources use one pipeline. Shield absorption precedes HP loss. Lethal
means actual HP becomes0 after damage; an actor can cross that boundary only once
per live generation. Actual HP-loss bookkeeping occurs before lethal processing.

1. DamageApplied with actual/absorbed/overkill quantities and source tags.
2. Damage-taken bookkeeping and on-lethal notification; ordinary queued healing
   cannot implicitly resurrect the actor.
3. An explicitly configured death-prevention policy may consume one finite charge
   and restore its **explicit input** surviving HP, emitting DeathPrevented. This
   general resolver capability is tested with labeled unit/lab fixtures, not silently
   attributed to LAST STAND. Repeating immunity requires a separate specification.
4. If still lethal, execute a supported on-death rebirth handler once. LIGHTBRINGER
   (120), single level, explicitly consumes its one rebirth, dispels all debuffs
   and restores40% maximum HP (floor milli-unit, minimum one milli-unit). Emit
   RebirthTriggered/CombatantRevived. It is a rebirth, counted separately from death
   prevention; it does not emit final CombatantKO and does not reset spent charges.
5. Otherwise emit CombatantKO once, mark final death, cancel future actions. No
   hidden1HP fallback, duplicate KO or spontaneous revival is permitted.
6. Drain already-earned damage reactions in the current chain before deciding the
   final result. Double final KO is a draw. A single surviving actor wins. Timeout
   is explicit if both survive the configured horizon.

Input death-prevention fixtures carry origin metadata and are never produced by a
card with unresolved semantics. A test may supply a finite charge and explicit HP
to prove ordering without creating a new game card or inventing its balance.

LAST STAND111 remains unresolved:1200 Shield stacks are explicit, but weakening
amount, surviving HP and exact immunity interpretation are not. The JS1HP plus35%
maxHP shield for3s is legacy divergence, not canonical LAST STAND. OATHBREAKER097's
buffer/death behavior and BERSERKER FRENZY009's speed units/lifesteal lifecycle also
remain unresolved. Their loadouts fail with a reason before combat.
