# v1.17 — Deterministic combat simulation and balance lab

Status: proposed next macro phase; **not executed in v1.16**.

## Preconditions

- Start from the completed v1.16 state and its exact validated/evidence commits.
- Read root governance, ADR 0003, canonical policy, pilot parity matrix and QA.
- Keep v1.15 legacy sources locked/read-only; use `canonical_data.py --check`.
- Keep Godot 4.7.2, typed GDScript and the existing toolchain. No Android SDK,
  final art/UI production, multiplayer or full-150-effect rewrite in this phase.

## A — Settle the smallest combat specification before coding

- [ ] Write a canonical combat specification and decision table for HP/energy units,
  stat units, armor/crit/dodge order, shield stack absorption, Toxin/Wound tick and
  decay, actual versus attempted damage, healing categories and death prevention.
- [ ] Define attack/cast timings and same-timestamp order, derived-event emission,
  recursion prevention, RNG stream ownership and versioned replay input/output.
- [ ] Decide actor symmetry explicitly. Document every intentional difference from
  the JS oracle: player-only passives/procs/healBoost and opening crit behavior.
- [ ] Specify 097 buffering/death ordering, 111 shield decay/surviving HP and 132
  Assault quantity/overlap rules, or keep each excluded with a precise open question.
- [ ] Resolve pilot level progression in a source-backed spec. Preserve raw levels;
  never reinterpret generic stacks/chance automatically. ID071 remains Epic/300
  unless an explicit balance decision changes the authoritative spec.
- [ ] Record economy integration decisions separately: UI3 versus helper4 slots,
  zero-preGold interest fallback, latent selling, player/bot HP-loss formulas.
  These are not prerequisites for a combat-only lab and must not be silently fixed.

## B — Minimal headless combat resolver

- [ ] Add typed CombatState/CombatEvent/DamageIntent/result APIs with fixed-step or
  chronological event scheduling, explicit input validation and deterministic logs.
- [ ] Resolve intents from the v1.16 operators with specified damage/status/death
  rules; replace the pilot's zero-HP refusal only after lifecycle tests exist.
- [ ] Feed derived events back through an ordered queue, suppress reflection loops,
  and constrain repeated/recursive procs with documented deterministic limits.
- [ ] Use the 16 oracle hero records only as fixtures. Integrate only specified
  pilot cards; reject unsupported loadouts/levels clearly. No scene dependency.
- [ ] Define a production execution profile distinct from `base_text_v1`; migrate
  definitions through versioned schemas and retain explicit comparison evidence.

## C — Automated balance lab before rebalance

- [ ] Provide a CLI accepting fixture/loadout, seed list, round horizon and output
  path. Emit versioned replay JSON, per-fight result and aggregate CSV/JSON metrics.
- [ ] Commit at least 12 representative matchup/loadout scenarios covering each
  implemented mechanism, with a fixed 1,000-seed corpus per scenario (12,000 fights).
- [ ] Record outcomes, time-to-resolution, effective damage by kind, healing,
  absorbed damage, status uptime/procs, unresolved definitions and deterministic
  limits. Establish baseline distributions without tuning card values to taste.
- [ ] Report JS comparisons only for implemented comparable behavior. Label deliberate
  specification changes and legacy approximations; do not demand false parity.

## D — Closure gates

- [ ] Keep full canonical/foundation profiles green and legacy hashes unchanged.
- [ ] Known mathematical vectors and boundary tests for mitigation, status/death
  order, timer/event ties, recursion and all newly specified pilot progression.
- [ ] Repeat every lab seed/scenario and compare exact state/replay checksums;
  mirror actors under the approved symmetry contract and check invariants.
- [ ] Reject malformed replay/loadout/version/unknown mechanics without partial
  results. Reproduce datasets and lab results from a fresh clean checkout in CI.
- [ ] Publish metrics, intentional legacy differences, unresolved choices and runtime
  cost measurements. Do not treat desktop headless speed as phone performance.
- [ ] Update PROJECT_STATE only after required gates; prepare v1.18 roster/reference
  approval using the indexed 20 candidates, with no final art production beforehand.
