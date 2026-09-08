# Card level progression — source audit v1.17

All582 preserved level records are used by exact lookup and comparison tests.
There are450 Normal,108 Epic and24 Legendary records. IDs/names/rarity/cost remain
unchanged, including Epic071 at300. No values are interpolated over explicit rows.

## Determined facts

`CardSystem.buy`, `randomBuy` and `addFree` advance owned level by exactly1 and
reject at `card.max`. A successful normal buy charges the preserved card cost;
random buy uses the existing explicit random-card price. Undo restores the prior
level; the latent sell API reduces level by1. No market/UI integration is ported.
The combat API receives a preselected level and never purchases/upgrades a card.

`BranchSystem.effects` multiplies each numeric approximation by that owned level.
It does not look up `legacyLevels` or `parameters`. Thus legacy oracle value atN
is reproducible as the actual old approximation×N, **not a canonical exact effect**.

The raw Normal sequence is stacks4/14/24/34/44 and chance10/20/30/40/50. Every one
of90 Normal cards has that same sequence. Every one of36 Epic cards has stacks
4/24/44 and chance10/30/50. All24 Legendary cards have one row without parameters.
No preserved GDScript implementation explains the missing parameter-to-effect
bindings. Several values conflict directly with original effect text (005 says60%,
077/149 say30%, while their level1 `chance` is10).

## Executable APIs and eligibility

- `source_level(cardId,N)` returns the exact preserved row, including parameters
  and image path. Missing/out-of-range/duplicate levels fail; no extrapolation.
- `source_parameter(cardId,N,key)` returns the explicit value or a missing-parameter
  error. This makes supplied values executable without asserting an unproved meaning.
- `legacy_oracle_values(cardId,N)` reproduces JS's actual multiplier for comparison
  only and is not accepted as a canonical combat loadout.
- `combat_values(cardId,N)` is allowed only for explicitly supported single-level
  texts (049,090,120 in this phase), whose quantities do not require interpolation.
  Other numbered effect bindings remain unresolved, including21 single-level cards
  whose mechanics are not implemented; known level count is not semantic coverage.
- Existing v1.16 base-text proposals can be selected explicitly as mechanics-lab
  fixtures. They have no implicit level. Their fixed quantities are not multiplied
  by owned copies or silently changed to generic `stacks/chance` values.

Acquisition is reconstructible in the JS oracle; adoption into production market
still waits for the separate economy/UX contract. Full canonical per-level effect
binding is unresolved for multi-level cards. This does not block the entity-agnostic
resolver, source-value API, or explicitly parameterized mechanics lab.
