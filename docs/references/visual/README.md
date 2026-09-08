# Visual Reference Library

This folder defines how visual references are organized.
Binary references remain at the indexed legacy paths; `/references/visual/`
contains category indexes. No production image admission is implied by location.

## Categories

### characters/
Use for:
- overall character style;
- body proportions;
- costume/material language;
- silhouette;
- weapons;
- model sheets.

Preferred final reference set per approved hero:
- front;
- 3/4 front;
- side;
- back;
- neutral pose;
- combat pose;
- silhouette;
- material/color sheet;
- weapon detail.

### expressions/
Expression library shared across hero production.

Recommended set:
- neutral;
- focused;
- aggressive;
- confident;
- pain light;
- pain heavy;
- stunned;
- casting;
- victory;
- defeat;
- KO;
- rare/comedic expression only where character-appropriate.

### arenas/
Use for:
- composition;
- foreground/midground/background separation;
- fighting plane;
- lighting;
- focal props;
- palette;
- depth treatment.

Each final arena should eventually have:
- hero-facing key art;
- camera blockout;
- depth/layer guide;
- lighting guide;
- prop list;
- mobile optimization notes.

### cards/
Use for:
- frame geometry;
- rarity hierarchy;
- branch icon placement;
- typography/readability;
- artwork crop;
- level/state representation.

References should be evaluated at real phone display size, not only full-screen desktop zoom.

### brand-ui/
Use for:
- logo;
- typography;
- color tokens;
- buttons;
- panels;
- bevel/slant language;
- glow;
- iconography;
- HUD density;
- interaction states.

### fx/
Use for:
- hit language;
- magic;
- shield;
- toxin;
- ice;
- healing;
- critical;
- KO;
- transition effects.

### ux/
Use for:
- flow;
- layout;
- information hierarchy;
- touch behavior;
- transitions;
- onboarding.

## File naming

Suggested:

`<CATEGORY>_<SUBJECT>_<PURPOSE>_<NN>.<ext>`

Examples:

- `CHAR_Solkael_front_01.png`
- `CHAR_Solkael_materials_01.png`
- `EXP_shared_pain_heavy_01.png`
- `ARENA_BeastCrucible_depth_01.png`
- `CARD_epic_frame_01.png`
- `UI_market_hierarchy_01.png`

## Manifest

The frozen v1.15 census remains `docs/references/visual/reference_manifest.json`.
The current audit is `v1.18/reference_inventory.json`, with source/owner, hashes,
associations, review decisions and explicit rights classes. See `v1.18/README.md`
and `v1.18/RIGHTS_REVIEW.md`. Rebuild with `tools/art/reference_lock.py`; do not
rewrite the historical census or copy its old `unknown` enum into production metadata.

A reference may be:
- `direction-selected` (internal planning only, not rights clearance);
- `reference-only`;
- `production-approved` (requires documented allowed rights and use);
- `rejected`.

Unknown-rights and proprietary reference-only material cannot be production-approved.
The ten-view character entry gate, including expression sheet, is in
`docs/art/CHARACTER_PRODUCTION_BIBLE.md`; the ten-expression shared library is in
`docs/art/expression_library.json`. Older suggested extra expressions are optional,
not additional required clips or gameplay states.
