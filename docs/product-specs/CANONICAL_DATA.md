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

The newer roster is the preferred candidate direction, but is not final until the Hero Roster phase closes.

## One-source rule

Never manually maintain two canonical copies of:
- cards;
- branches;
- hero definitions;
- economy constants.

Generated derivatives must say where they came from.
