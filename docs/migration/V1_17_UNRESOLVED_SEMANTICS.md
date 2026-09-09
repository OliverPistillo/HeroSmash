# Unresolved semantics after v1.17

The pipeline is specified for validated inputs, without resolving all cards or
approving balance. The v1.16 canonical files remain byte-identical; all150 IDs and
582 records retain provenance in the compiled combat catalog.

| Question | Executable boundary | Required decision |
|---|---|---|
|Normal/Epic levels |450+108 exact source rows and separate JS oracle values; numbered effects rejected |Each parameter's operator/trigger meaning. Do not overwrite00560% with generic10%. |
|Legendary coverage |049/090/120 accepted;21 others unsupported |Single level does not establish mechanics. |
|097 OATHBREAKER |Rejected |Buffered quantities,release order,shield/HP and lethal behavior. |
|111 LAST STAND |Rejected |1200 Shield weakening,surviving HP,immunity; JS35%maxHP is not canonical. |
|132 temporary Assault |Rejected |Units of Assault+5,overlap,refresh,cap. |
|009 BERSERKER FRENZY |Rejected |1.4s lethal window,speed80 units,lifesteal45% timing/silence/expiry. |
|077 Shield |Literal4 stacks with explicit fixture |Capacity,conversion,duration; lab1HP/stack is labeled arbitrary input. |
|115/149 Toxin |Literal4 stacks with explicit fixture |Card-specific damage/duration/weakening; hero14DPS does not establish this. |
|Other statuses |Hero parameters or explicit mechanics inputs |No universal conversion from one fallback. Card122 weakening unresolved. |
|Unreviewed cards |120 reviewed from previous135;134 unreviewed plus3 unresolved pilots =137 rejected IDs |Narrow future pilots need source texts and tests. |
|Market adoption |Legacy buy/free/random +1,max rejection; combat receives level |Production acquisition/economy UX remains separate. |

Economic questions retained: UI3 vs helper4 shop slots; zero-preGold interest
fallback; latent selling; different player/bot run-HP loss formulas. None blocks
prepared CombatantState simulation; no economy file changed.

Technical debt: existing32-bit FoundationRng LCG needs statistical review before
competitive balance conclusions. Events do not yet drive presentation. Device
profiling/final-art budgets need representative content and toolchain. Remote CI
and cross-platform hash equality require actual runner evidence.
