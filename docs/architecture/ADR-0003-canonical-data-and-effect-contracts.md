# ADR 0003 — Versioned data and bounded effect contracts

Status: accepted for the v1.16 framework under the current task; unresolved product semantics below remain unapproved.

## Sources and ownership

`tools/migration/canonical_data.py` generates five production datasets from the
unchanged v1.15 web sources. JSON Schema Draft 2020-12 documents are authored in
`game/data/schemas/`. Generated JSON is committed for inspection and loading;
`--check` must reproduce it byte for byte. Logical version `v1.16.1` replaces a
wall-clock timestamp. Source hashes use UTF-8 bytes with CRLF normalized to LF so
Windows and Linux checkouts reproduce the same output. Raw JSON values are retained
losslessly, including text, image paths and level parameters.

The 16 runtime heroes are explicitly `legacy_oracle`, not the final roster. The
20 candidate concepts remain indexed in the archive pending the roster phase;
this phase does not create another copy or invent their combat statistics.

The only authored effect input is `game/data/effect_contracts.json`. It references
cards by preserved identity and guards original text with a SHA-256. The generator
creates a registry for all 150 cards: unreviewed records fail execution explicitly.
Keyword-derived JS numeric effects are comparison evidence only.

## Schema and typed boundaries

Python uses pinned `jsonschema` in a local virtual environment/CI. Godot validates
the same schemas using a deliberately restricted evaluator: types, properties,
required, additionalProperties, items, array size/uniqueness, enum, const, numeric
bounds, string length/pattern. Unknown schema keywords fail closed. It is not a
general-purpose JSON Schema implementation. Cross-record validation enforces IDs,
references, raw/normalized consistency, costs, rarities and level counts before
publishing a catalog. Failed reloads leave the previous catalog intact.

Typed definitions expose copies of mutable raw metadata. Data, the effect runner
and presentation remain independent. No scene scripts contain card definitions.

## Pilot scope and explicit limitations

Pilot IDs: 002, 005, 010, 020, 028, 040, 049, 077, 090, 092, 097, 111,
115, 132, 149. This supersedes the earlier plan's three illustrative candidates.
Nine and 111 were suggestions, not approval to invent their missing rules.

Execution profile `base_text_v1` demonstrates the literal quantities in the
original text. It **does not define card levels or balance**. The imported generic
`stacks/chance` level parameters do not consistently describe those texts; any
request to execute a numbered level fails `unsupported_progression`. Calling the
profile is an explicit opt-in to these bounded proposed semantics, not a complete
card implementation claim.

097 is unresolved: what damage/heal buffering means, threshold crossing and death
ordering are unspecified. 111 is unresolved: shield weakening amount and surviving
HP are unspecified. 132 is unresolved: Assault quantity and refresh/stack policy
are unspecified. They are selected, documented and rejected, not approximated.

## Deterministic event/action contract

- Single isolated combat session, two integer actor IDs (0/1); same semantics for
  both. Input events are caller-owned facts, processed in caller order at equal
  timestamps. Actors and binding order are explicit, never dictionary iteration.
- HP, energy and flat damage/stat amounts use milli-units; time uses integer
  milliseconds; probabilities and additive percentage bonuses use basis points.
  Integer division floors nonnegative results. Intermediate values are bounded.
- `combat_start` is issued once by the runner at time zero. Intervals first fire
  after their period; overdue ticks run chronologically, then actor/binding/rule
  order. At a supplied timestamp, scheduled ticks precede the external event.
- Assault maps to `basic_attack`, Essence cast to `skill_cast`, Evasion to `dodge`
  for this profile. `basic_hit` carries an explicit critical flag. `heal` carries
  `kind=regen` for the Shield interaction. The caller resolves authoritative hits,
  damage, HP transitions and regeneration; events do not independently repeat them.
- 010 accumulates an additive 400 bp basic-damage bonus per attack, capped at
  2000 bp; application to that attack is the future combat resolver's responsibility.
  020 consumes each 400,000 milli-HP actually lost, retains remainder across heals,
  and adds 6,000 milli-energy per crossing, with no invented energy cap.
- 028 uses current missing HP and a minimum 1,000 milli-heal, capped at max HP.
  077/115/149 add **status stacks**; their shield absorption, toxin damage/decay,
  Wound amplification and global status lifecycle remain unresolved in v1.17.
- Damage actions emit typed intents with amounts and damage kind. They do not
  bypass an imaginary armor/crit/death resolver. 090 emits 20,000 magic milli-damage
  every 500 ms without consuming Wound. This is a periodic-damage contract only.
- Special handler `reflect_incoming_once` implements 049's proposed 50% chance
  to reflect the full supplied incoming amount as magic, with `reflectable=false`.
  Inputs already marked nonreflectable produce no reflection. There is no recursion.
- A local FoundationRng stream is seeded at construction. Bounded draws use
  rejection sampling; only eligible 0<chance<10000 rules consume a draw. Actions
  run in declared order. New actions do not recursively dispatch their own events;
  resulting facts must be supplied by the future resolver in an explicit order.
- Typed command logs expose all applied mutations and pending damage intents.
  No full CombatSystem, implicit status physics, shop or death resolution is added.

Future trigger/action names are representable but capabilities are explicit;
unsupported combinations fail validation/binding. There is no card-ID dispatch.
Runtime input bounds limit actors to 1,000,000 HP/energy/stat units, input events to
one hour and per-call interval catch-up to 10,000 ticks. Invalid requests must fail
  without observable mutation or RNG consumption. Each public execution call is
  transactional: timer/action/numeric-limit errors restore state, queues and RNG.

HP input facts carry `amount_milli` (actual loss/heal) and `hp_after_milli`, which
must agree with the ledger after due timers. Heal facts additionally carry
`kind=regen|direct`; hit facts carry boolean `critical`; dodge facts carry positive
`incoming_milli` and boolean `reflectable`; status facts carry `status` and positive
`stacks`. Unknown fields/types fail. HP reaching zero is explicitly rejected until
the death lifecycle is specified; the pilot never implicitly resurrects an actor.
Commands can be drained by the caller; an undrained 100,000-command buffer fails
transactionally. Per-action stacking caps remain independent within composed rules.

## Legacy conflicts retained

Three visible shop slots versus four helper/probability slots, zero-preGold fallback,
latent selling, player/bot proc differences and conflicting player/bot HP-loss
formulas are not settled by copying economy constants. All remain explicit v1.17
specification decisions. The new isolated effect runner is actor-symmetric; it is
not claimed to reproduce the asymmetric JS combat loop.
