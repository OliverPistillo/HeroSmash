# Visual Reference Library

This folder defines how visual references are organized.
Actual binary references live under `/references/visual/`.

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

Every important reference should be registered in:
`docs/references/visual/reference_manifest.json`

A reference may be:
- `approved-direction`;
- `reference-only`;
- `legacy-candidate`;
- `rejected`.

Copyrighted third-party material should almost always be `reference-only`.
