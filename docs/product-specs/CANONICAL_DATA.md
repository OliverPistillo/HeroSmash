# Canonical Data Policy

## Branches

Canonical IDs/names are derived from:

- Assault
- Guardian
- Essence
- Rage
- Ice
- Toxin
- Shield
- Healing
- Power
- Precision
- Wound
- Dodge

Normalize experimental synonyms:
- Arcane → Essence
- Venom → Toxin
- Frost → Ice

## Cards

The 150-card imported legacy deck is authoritative until explicitly revised.

Migration requirements:
- preserve legacy ID;
- preserve original name;
- preserve original effect text;
- preserve rarity;
- preserve branch membership;
- preserve cost;
- preserve original level metadata.

Runtime implementations may add normalized fields, but should retain traceability to the original source.

## Heroes

There are currently multiple generations of hero data:
1. older placeholder/runtime heroes in the JS prototype;
2. newer 20-character anthropomorphic roster in the legacy archive.

The current v1.18 task authorizes selection of 16 launch and 4 reserve from the
20 sourced candidates. `roster/hero_roster.json` owns production identity and
normalized display affinities; the source snapshot retains all original fields.
Visual/pipeline proposals and reference rights are explicitly separate. Runtime
hero replacement is not performed: the 16 oracle IDs/stats/skills remain canonical
for simulation and replay until a separately validated gameplay migration.

## One-source rule

Never manually maintain two canonical copies of:
- cards;
- branches;
- hero definitions;
- economy constants.

Generated derivatives must say where they came from.

## v1.16 portable contract

Authored schemas: `game/data/schemas/*.schema.json`, Draft 2020-12 (the supported
Godot subset is defined in ADR 0003). Envelope fields are `schemaVersion=1`,
`logicalVersion=v1.16.1`, `dataset`, `generator`, `sources`, `records`.
Each source has `path`, `sha256`, `normalization=utf8_lf`. Each record has
`provenance.source`, `pointer` and `sourceSha256`.

The generator `tools/migration/canonical_data.py` is the sole writer of canonical
branches/cards/heroes/economy/effects JSON and the two comparison documents.
Use `--check` for a non-mutating reproducibility check. The v1.15 source lock must
match before any output is written. Raw card and hero objects are retained in
`legacy`; economy constants in `values` are the unchanged source object.

Card API fields: `id=legacy_NNN`, numeric `legacyId`, `name`, `originalText`,
`branches` (canonical lowercase IDs), original English `rarity`, `cost`,
`maxLevel`, `legacy`, `provenance`. Original level metadata is opaque; it is not
an effect scaling formula. ID 071 HEAVY BASH remains Epic/cost 300.

Only card casing, commas/semicolons, empty delimiter tokens and the Guadian typo
on ID 070 are normalized. Unknown names and duplicate normalized branches fail.
Candidate aliases are reserved for the future candidate importer, not permitted
as fallback spellings in the 150-card deck. The imported 16 heroes are explicitly
`legacy_oracle`. v1.18 applies Arcane/Essence, Venom/Toxin and Frost/Ice aliases only
to production candidate metadata; it does not broaden the runtime card importer.

`game/data/effect_contracts.json` owns 15 reviewed pilot proposals guarded by
original-text hashes. The generated 150-ID registry distinguishes `unreviewed`,
`unresolved`, `implemented` and a separate parity classification. Tests/evidence
establish execution coverage; a numeric ID or `implemented` base-text profile
does not claim a fully resolved, leveled card. See ADR 0003 and the generated
`docs/migration/V1_16_PILOT_PARITY.md` for units, ordering and explicit limitations.
