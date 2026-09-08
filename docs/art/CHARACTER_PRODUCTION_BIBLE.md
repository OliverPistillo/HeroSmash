# Character Production Bible v1

This is a specification lock, not a collection of finished models. The current
owner task authorizes the 16 launch/4 reserve selection. Source-unsupported shape,
motion, dimension and rig details remain explicit proposals in the identity sheets;
artists must resolve those proposals in an approved reference packet before final
modeling. The phase does not assert rights clearance for any legacy image.

## Authoritative inputs

- [Launch roster](../product-specs/roster/LAUNCH_ROSTER.md), [scores](../product-specs/roster/SCORING_MATRIX.md), [coverage](../product-specs/roster/BRANCH_COVERAGE.md).
- [Oracle matrix](../product-specs/roster/ORACLE_MIGRATION_MATRIX.md): all 16 combat identities and their fixtures remain intact.
- [Reference catalog](../references/visual/v1.18/README.md), [rights review](../references/visual/v1.18/RIGHTS_REVIEW.md), [per-hero gaps](UNRESOLVED_AND_REFERENCE_GAPS.md).
- `rig_families.json`, `character_conventions.json`, `animation_contract.json`,
  `expression_library.json`, `brand_ui_language.json`, `card_visual_language.json`
  are the machine-readable contracts; corresponding uppercase Markdown files are
  generated readable views. Edit JSON and rebuild, not two copies.

## Reference entry gate

Every hero needs front, 3/4 front, side, back, isolated silhouette, neutral pose,
combat stance, materials/palette, weapon detail and expression sheet. The views
must depict one consistent body, equipment, scale and rest anatomy. Record reference
IDs, owner/provenance, intended use and approval for each. A roster thumbnail, action
sprite sequence or three evolution stages does not establish missing orthographic
views. No automatic production-art generation is part of v1.18.

All 16 launch packets currently fail this asset-entry gate. This is documented
reference debt, not a skipped specification gate. Rights can be resolved by valid
evidence for an allowed use or an independently authored original design process;
uncleared pixels cannot become textures or traced production shapes by changing a
manifest flag. Final model work starts only after a concrete packet is approved.

## Body and rig policy

Medium biped covers Solkael, Rajuro, Aethryon, Morvayne, Elunor, Oromir and Tortugan.
Heavy biped covers Brumgar, Karchar, Rhazgor and Vulkaryn. Agile biped covers Fenrox,
Kitsara, Lupika and Skarvex. Sylvex uses a serpentine lower chain. These are four shared
topology/profile families, not four already built skeletons. The three biped
families share semantic hierarchy but have distinct rest matrices/proportions and
contact offsets. Reserve Gruttar/Kongaru extend heavy and Nyxara/Zelkara agile;
the mantis blade-arm exception needs its own reviewed profile before production.

The hierarchy explicitly includes root, pelvis, three spine bones, neck/head/jaw,
clavicles, arms/hands and biped legs/feet/toes. Five named digits support reusable
hand clips; unused controls may remain at rest under gloves/hooks. The source does
not establish final visible finger counts. Tail, stinger, wing mantle, feather cape,
hood and ears are bounded extensions. Horns/antlers/shells/fins default to rigid
attachments. No evolution form can silently replace limbs, add flight, change
species or break an animation interface. Keep hero-specific extension tracks
separate from shared tracks and validate actual contacts after retargeting.

## Blender → GLB → Godot contract

Use one meter per unit, metric authoring and identity object transforms. The origin
is centered at supporting floor contact; measure skull height separately from ears,
horns, hair and raised wings. Hero heights are explicit proposals, not uniform
rescaling. Blender front is -Y/up +Z; imported model front is +Z/up +Y. Convert once
in glTF export. This follows Godot's documented [model direction conventions](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/model_export_considerations.html).

Use a T-pose for bipeds, a documented grounded tail rest for Sylvex, and one unique
`HeroSkeleton`. Names alone do not guarantee shared animation: record BoneMap,
rest rotations, roll and scaled contacts; use a custom serpent profile rather than
inventing legs. See Godot's [retargeting documentation](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/retargeting_3d_skeletons.html).

Export versioned `.glb` with embedded validated textures, intentional triangulation
and metallic/roughness PBR. Runtime consumes exports through a separate typed
GDScript scene wrapper; it never imports arbitrary working `.blend` files. Naming,
folder patterns, channel conventions, sockets, tolerances and axis conversion
matrix are fixed in `character_conventions.json`. No final triangle/material/texture
budgets are invented before a representative measured build.

## Animation and face contract

Required clip names: `idle`, `intro`, `attack_light`, `attack_heavy`, `skill_cast`,
`hit_react`, `dodge`, `ko`, `victory`, `idle_breathing`. `KO` is the semantic state;
`ko` is its lowercase asset name. Author/bake at 30 fps. Only the two idle clips
loop. Root motion is disabled; wrapper/pelvis offsets are presentation, not combat
movement. The shared ten-expression library supports mammal, avian, reptile,
chitin, shark and antlered morphology with per-hero deviations.

Markers `windup_start`, `hit`, `projectile_spawn`, `cast`, `vfx_spawn`,
`recover_start`, `recover_end` schedule visual/audio cues only. Resolver event ID
and time govern damage, dodge, reflection and KO. No animation callback applies
damage. Late playback, cancelled attacks, replay seeking and missing clips follow
the explicit fallback/deduplication rules in the animation contract.

## Next asset validation

The first fighter must prove actual mesh/rig/texture naming, scale/origin/rest,
material counts, missing-texture checks, required clips/loops/root motion, Blender
export, Godot import and wrapper boot. Add landscape screenshots, an event-synced
clip and measured costs. Specification validation in v1.18 does not claim those
future character checks have already passed. Existing foundation sample-GLB gates
remain independent and must stay green.

## v1.19 proposal only

Use Solkael as the first production-fighter candidate: named gauntlet concept,
readable silhouette, medium rig, no flight or special locomotion, and brand-facing
defender role. First resolve rights/original design and complete the ten-view packet.
Then build a reproducible Blender export/validation script, a disposable convention
fixture, one approved base-form fighter, minimum animation/facial controls and a
Godot wrapper consuming the unchanged resolver. Exit with clean-checkout rebuild,
GLB/import/animation checks, phone-scale footage and measured performance. Do not
start other final fighters, evolution forms, arenas or balance changes. v1.19 has
not been started by this phase.
