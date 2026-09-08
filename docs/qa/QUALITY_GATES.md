# Hero Smash — Quality Gates

These gates evolve as the production runtime is built.

## Foundation gate

Required before closing v1.15:
- repo inventory generated;
- archive inventory generated;
- duplicate classification generated;
- authoritative data map generated;
- minimal Godot project starts successfully;
- Godot headless command exits successfully;
- sample GLB imports;
- no unreviewed deletion of legacy files;
- `PROJECT_STATE.md` updated.

## Logic gate

For gameplay/data work:
- schema validation;
- deterministic seeded test;
- unit tests;
- simulation regression where applicable.

## Asset gate

For a character/arena:
- naming validation;
- scale/origin validation;
- missing texture check;
- material count check;
- animation list check;
- GLB export success;
- Godot import success;
- runtime scene load success.

## Visual gate

For UI/combat presentation:
- reference resolution screenshot;
- safe-area check;
- readable at target phone scale;
- no critical overlap;
- animation/VFX sync checked.

## Mobile performance gate

Budgets will be locked after the first representative arena + two representative final-quality fighters.

Do not invent final budgets before measuring a representative build.

Until then:
- avoid obvious overdraw;
- avoid uncontrolled dynamic lights/shadows;
- keep materials and transparent effects intentional;
- profile on physical Android hardware regularly.

## Release gate

Later:
- Android package builds headlessly;
- clean install/launch;
- save migration tested;
- no missing resources;
- crash-free smoke run;
- performance target met on defined minimum device tier.
