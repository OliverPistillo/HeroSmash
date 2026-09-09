# Solkael v002 — first textured polish iteration

Owner art review is REQUIRED. Technical gates do not grant final-art approval.
Only the eight unchanged production-approved Art Lock v1 images guide this asset.
No image pixels were used as textures. Historical v001 recipe/source/GLB stay intact.

## Source and reproduction

- `art/characters/solkael_lionheart/v002/source/chr_solkael_lionheart_v002.blend`
- `art/characters/solkael_lionheart/v002/solkael_asset.json`
- `art/characters/solkael_lionheart/v002/textures/{base_color,normal,orm,emissive}.png`
- `game/assets/characters/solkael_lionheart/chr_solkael_lionheart_v002.glb`
- `game/scenes/characters/solkael_lionheart/hero_solkael_lionheart_v002.tscn`

Author with Blender5.2 `--background --factory-startup --python-exit-code 1
--python tools/asset_pipeline/solkael_polish.py`. `-- --out-root <directory>`
reconstructs in isolation. Export the saved source through the existing validated
`solkael_export.py -- --source <blend> --output <glb>`. Packed source images make
the blend portable. Sources, texture PNGs, runtime GLB/PNG and evidence PNGs use
LFS; manifests, recipes and import settings use ordinary Git. No history rewrite.
Blender backup .blend1 files are ignored, never runtime inputs. APK/debug keystore,
SDK archives, staging projects and raw logs stay under ignored `.work/`.

## Geometry, face and animation

Continuous quad-ring torso and upper arms replace intersecting large body spheres.
Torso weights blend pelvis/spine segments while ceramic plates remain rigid.
The face has a longer bridge, reduced eye sockets, solid upper/lower eyelid surfaces,
intact eyeballs, deep dark mouth volume, lower/upper teeth, tongue and connected chin.
Lower teeth/tongue/chin follow independent jaw expression deltas. Nine independent
relative morphs plus neutral retain the shared ten-expression contract.

Mane strategy: opaque solid stylized clumps, smoothed tapered surfaces and extra
rear neck layers. Zero transparency, zero alpha-card overdraw, zero grooming cache,
one shared material. Short body-fur detail is authored in the atlas. This is a
mobile-oriented topology choice, not proof of final visual quality. The radial
mass and uniform clumps still deviate from the reference's flowing natural mane.

All ten clips retain timings/markers and no root motion. Added spine anticipation,
head response and decaying tail recovery on punches/hit reaction. KO floor correction
and idle loop continuity remain validated. The two-fighter stage adds the same
0.24m visual step-in for either entity and decays it over350ms; it is presentation
blocking only. Resolver timestamps, damage/status/death and hashes are unchanged.
The first CombatStarted and attack may share t=0: a one-second intro prelude holds
the playback clock before chronological replay starts. No simulated event is delayed.

## UV and material contract

One unique packed atlas, Smart Project72°, area weighting, .003 island spacing,
8px gutter dilation. Independent triangle clipping checks overlaps, zero-area UVs
and atlas bounds; negative controls include shared edges and invalid overlaps.
Face, armor and limbs share area-based texel density. Small mechanical/fur islands
are intentionally unique rather than mirrored. About one third of atlas area holds
triangles: packing efficiency and artist-oriented seam grouping remain polish debt.
This is editable and uniquely paintable, not a final hand-painted UV layout.

Four2048² PNG maps: sRGB Base Color, non-color tangent Normal, non-color
Occlusion/Roughness/Metalness, sRGB Emissive. Occlusion is neutral1.0; roughness and
metalness vary by original material region. No unmeasured baked-AO claim. Gold uses
.8 metallic, ceramic .05, cloth/fur0; amber emission is restrained1.15. Opaque glTF
metallic-roughness material, one surface/draw per color pass. Shader inputs export
to embedded PNGs; Godot extracts the same PNG resources beside the GLB. LOD generation
is disabled for evidence consistency. No reference imagery becomes a runtime texture.

Raw RGBA8 full-mip upper estimate is85.33MiB for four2048² maps, shared by both
instances. Actual desktop/Android compression and total viewport memory are recorded
separately. Android staging explicitly enables ETC2/ASTC import. Do not multiply
shared texture allocation by two or infer phone residency from desktop counters.

## Remaining art decisions

Matched: identity, dual integrated towers, canonical palette intent, sun emblems,
no sword/cape/separate shield, 10clips/10expressions. Acceptable technical deviation:
opaque clumps and compact one-material atlas. Unresolved: natural lion facial planes,
organic mane rhythm, full-body anatomical continuity at elbow/hip transitions,
armor wrap/detail, premium roughness painting, expressive asymmetry and planted
lower-body boxing weight. Owner must review the actual model renders before final
art approval; this technical iteration is not automatically production-final.
