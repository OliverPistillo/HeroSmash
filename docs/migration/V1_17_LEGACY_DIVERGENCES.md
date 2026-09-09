# Comparison with preserved JavaScript

`tools/validation/combat_legacy_oracle.mjs` executes unchanged modules read-only.
Effect isolation replaces a method only inside that test process.4,167 assertions
cover all582 actual level multipliers,buy/max behavior and the observations below.
These tests lock observations, not canonical approval. New mathematical/lifecycle
vectors and12-scenario mirror tests cover the specified replacement behavior.

| Mechanism | Observed JS | combat_v1.17.1 |
|---|---|---|
| Identity |Player-only HP regen,healBoost,on-hit,skillPower,opening crits; initial loadouts on both |One operator path; unsupported effects rejected. Every lab scenario is mirrored in tests. |
|049 reflection |Player always reflects half; bot lacks proc |50% full post-Wound/armor pre-Shield damage,magic/noncrit/nondodge/nonreflect.64-seed vectors and full mirror corpus. |
|Shield |5+3 shield vs10 damage loses5HP, leaves3shield |FIFO consumes both, loses2HP. Combined damage vector tests order. |
|Armor/Wound |`(20-6)*1.05=14.7` |Explicit defense-before-armor: `20*1.05-6=15`, then8shield leaves7HP. Intentional ordering decision. |
|DoT |Frame delta,null source,bypasses Wound;14DPS loses14HP with Wound |Scheduled source-attributed magic/DoT,Wound applies,delayed first tick,expiry-inclusive last,no implicit partial tick. |
|Skill status |Applies even after dodge |Requires landed hit; no application after finalKO or onto a new reborn generation from the same lethal skill. |
|Actual damage |1HP vs100 reports100 |Actual capped to currentHP,overkill separate;020 uses actual loss. |
|LAST STAND |1HP,35%maxHP shield for3s |111 unresolved. Explicit finite prevention fixture;120 one rebirth40%HP/cleanse. |
|Timing |Player then bot then DoT per frame; skill postpones basic |Seeded stable-ID initiative,integer boundaries/readiness rounds; simultaneous earned ticks can doubleKO. |
|Timeout |45s assigns relativeHP win,tie favors player |Explicit timeout,relativeHP leader metric only. |
|Crit recap |May count a dodged crit for player |Landed numerator,eligible-attempt denominator. |
|Levels |Approximate numeric effects×owned level;raw parameters unused |582 exact lookups,separate oracle values;049/090/120 numbered execution only. |

Thirteen IDs execute:12 literal contracts plus120. No unsupported player-only
approximation enters production. Branch synergy bonuses are excluded from the lab.
Hero stats,skill cost/CD/power,energy regeneration,Ice floor and stun energy rate
are source-normalized without tuning. The v1.16 EffectRunner/tests remain intact as
an operator harness; they do not claim full combat parity.
