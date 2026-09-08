# v1.17 — Deterministic combat simulation and balance lab

Status: COMPLETE; final validated implementation `ec34ebb1a7bebc781c8f9806c045031d28597dcc`.

Completed on `revival/v1.17-combat-balance-lab`, baseline
`v1.16-canonical-data` / `87c1d0e4ba519e082feaf70848c84862acedc0ff`.

Current task explicitly requires entity-agnostic rules, 12 scenarios ×1,000 seeds,
integer combat time, replay hashes and no rebalance. Godot 4.7.2 and existing Python
3.12/jsonschema tooling were detected; no installation is required.

Source audit: all 582 raw level records remain available, but the JS never reads
their `parameters`; it multiplies approximate `card.effects` by the acquired level.
Normal/Epic parameters are two universal templates, not proved per-card semantics.
The new level API exposes exact source values and separate execution eligibility
from the known acquisition transition. Unproved bindings remain unresolved.

Status parameters must be explicit per application; no unspecified universal
Shield stack→HP or Toxin stack→damage conversion will be invented. Mechanics-lab
fixtures may supply labeled scalar status inputs without pretending to implement
an ambiguous leveled card. Literal v1.16 profiles remain distinct from resolved
single-level cards. LIGHTBRINGER (120) is added to the bounded pilot because its
single-level text explicitly specifies one rebirth at40% HP, clearing debuffs;
LAST STAND remains unresolved.

## Preconditions

- Start from the completed v1.16 state and its exact validated/evidence commits.
- Read root governance, ADR 0003, canonical policy, pilot parity matrix and QA.
- Keep v1.15 legacy sources locked/read-only; use `canonical_data.py --check`.
- Keep Godot 4.7.2, typed GDScript and the existing toolchain. No Android SDK,
  final art/UI production, multiplayer or full-150-effect rewrite in this phase.

## A — Settle the smallest combat specification before coding

- [x] Write a canonical combat specification and decision table for HP/energy units,
  stat units, armor/crit/dodge order, shield stack absorption, Toxin/Wound tick and
  decay, actual versus attempted damage, healing categories and death prevention.
- [x] Define attack/cast timings and same-timestamp order, derived-event emission,
  recursion prevention, RNG stream ownership and versioned replay input/output.
- [x] Decide actor symmetry explicitly. Document every intentional difference from
  the JS oracle: player-only passives/procs/healBoost and opening crit behavior.
- [x] Specify 097 buffering/death ordering, 111 shield decay/surviving HP and 132
  Assault quantity/overlap rules, or keep each excluded with a precise open question.
- [x] Resolve pilot level progression in a source-backed spec. Preserve raw levels;
  never reinterpret generic stacks/chance automatically. ID071 remains Epic/300
  unless an explicit balance decision changes the authoritative spec.
- [x] Record economy integration decisions separately: UI3 versus helper4 slots,
  zero-preGold interest fallback, latent selling, player/bot HP-loss formulas.
  These are not prerequisites for a combat-only lab and must not be silently fixed.

## B — Minimal headless combat resolver

- [x] Add typed CombatState/CombatEvent/DamageIntent/result APIs with fixed-step or
  chronological event scheduling, explicit input validation and deterministic logs.
- [x] Resolve intents from the v1.16 operators with specified damage/status/death
  rules; replace the pilot's zero-HP refusal only after lifecycle tests exist.
- [x] Feed derived events back through an ordered queue, suppress reflection loops,
  and constrain repeated/recursive procs with documented deterministic limits.
- [x] Use the 16 oracle hero records only as fixtures. Integrate only specified
  pilot cards; reject unsupported loadouts/levels clearly. No scene dependency.
- [x] Define a production execution profile distinct from `base_text_v1`; migrate
  definitions through versioned schemas and retain explicit comparison evidence.

## C — Automated balance lab before rebalance

- [x] Provide a CLI accepting fixture/loadout, seed list, round horizon and output
  path. Emit versioned replay JSON, per-fight result and aggregate CSV/JSON metrics.
- [x] Commit at least 12 representative matchup/loadout scenarios covering each
  implemented mechanism, with a fixed 1,000-seed corpus per scenario (12,000 fights).
- [x] Record outcomes, time-to-resolution, effective damage by kind, healing,
  absorbed damage, status uptime/procs, unresolved definitions and deterministic
  limits. Establish baseline distributions without tuning card values to taste.
- [x] Report JS comparisons only for implemented comparable behavior. Label deliberate
  specification changes and legacy approximations; do not demand false parity.

## D — Closure gates

- [x] Keep full canonical/foundation profiles green and legacy hashes unchanged.
- [x] Known mathematical vectors and boundary tests for mitigation, status/death
  order, timer/event ties, recursion and all newly specified pilot progression.
- [x] Repeat every lab seed/scenario and compare exact state/replay checksums;
  mirror actors under the approved symmetry contract and check invariants.
- [x] Reject malformed replay/loadout/version/unknown mechanics without partial
  results. Configure clean-checkout CI and reproduce datasets/lab locally; remote
  Actions execution is not claimed.
- [x] Publish metrics, intentional legacy differences, unresolved choices and runtime
  cost measurements. Do not treat desktop headless speed as phone performance.
- [x] Update PROJECT_STATE only after required gates; prepare v1.18 roster/reference
  approval using the indexed 20 candidates, with no final art production beforehand.

## Closure evidence

15/15 combat gates,11/11 canonical gates,18/18 full Foundation gates passed from
a clean same-branch clone.12,000 fights repeated,zero hash failures,1,000 mirrors,
12 file replay roundtrips. Full report:`docs/qa/V1_17_BALANCE_REPORT.md`; machine
evidence:`docs/qa/evidence/v1.17/`. PROJECT_STATE is updated only by the subsequent
documentation closeout commit after these executed gates. Next phase:
`docs/exec-plans/active/V1_18_HERO_ROSTER_REFERENCE_LOCK.md`.
