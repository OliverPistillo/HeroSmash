# v1.20 — Solkael Polish & Device Slice

## Separate acceptance states

1. **PIPELINE VALIDATED:** local and fresh GitHub checkout asset/runtime gates pass;
   all previous full profiles pass, including repeated12000-fight comparison.
2. **ART REVIEW STATUS:** REQUIRES OWNER REVIEW. Not final-art approved. The actual
   model remains visibly simpler than the Art Lock; unresolved sculpt/paint/animation
   quality is listed below and in the structured render review.
3. **ANDROID EXPORT VALIDATED:** official toolchain/templates, ARM64 debug APK,
   signature/manifest/dependency checks and exported-pack headless boot pass; a
   second clean-checkout export also passes.
4. **PHYSICAL DEVICE BLOCKED:** repeated adb discovery found zero authorized phones.
   No physical model/OS/SoC/GPU/RAM/thermal/FPS/load/crash measurements are fabricated.
5. **TWO-FIGHTER BUDGET STATUS:** actual asset counts and60s desktop samples recorded;
   mobile budgets are PROPOSED, arena headroom remains UNDETERMINED without hardware.

## Git and scope

Branch: `revival/v1.20-solkael-polish-device-slice`; Draft PR:
https://github.com/OliverPistillo/HeroSmash/pull/2 toward main, no merge/auto-merge.
Baseline `f03a1b3833055b2538f1780bcc4a649830981195` was clean and matched origin.
Annotated tag `v1.19-golden-fighter-pipeline` points to that exact baseline.
Main remains `66a5ba67f0691b7d50a11fa873f4ed24c80a14ef`; PR#1 is untouched.

Implementation/evidence commits:

| Commit | Change |
|---|---|
|8a66756|Authorized plan and detected environment|
|9f0a543|Separate official Node24 Actions maintenance|
|5604093|Versioned textured v002 source, rig/face/animation pass|
|a7247ee|Two-fighter replay scene, UV/runtime validation|
|82e6230|Official Android tooling and isolated debug export|
|9eaa9a2|Hashed authored-image scope and measured contact checks|
|339f423|Readable barrier and initial actual model evidence|
|5fc4990|Measured costs, final captures and Android evidence|
|1bf8e04|Complete exported dependencies and packaged-scene boot check|

Full six-profile clean validation ran at5fc4990; only export tooling/preset/docs
changed afterward. Fresh export at1bf8e04 passes with a clean checkout afterward.
The final documentation commit/tag are reported in the task delivery, avoiding a
self-referential commit hash inside its own content. No v1.21 branch is created.

## Asset structure and governance

```text
art/characters/solkael_lionheart/
  source/chr_solkael_lionheart_v001.blend             retained
  v002/source/chr_solkael_lionheart_v002.blend        editable source
  v002/textures/{base_color,normal,orm,emissive}.png
  v002/solkael_asset.json
game/assets/characters/solkael_lionheart/
  chr_solkael_lionheart_v001.glb                     retained
  chr_solkael_lionheart_v002.glb + imported PNGs
game/scenes/characters/solkael_lionheart/
  hero_solkael_lionheart_v002.tscn
game/scenes/qa/two_fighter_slice.tscn
tools/asset_pipeline/{solkael_polish,capture_polish,report_polish}.py
tools/validation/polish.py
tools/android/{bootstrap_android,export_debug,device_probe}.py
docs/qa/evidence/v1.20/
```

No legacy file moved/renamed/deleted; no gameplay source/data, original reference
packet or production main scene changed. Eight production-approved references and
736 historical central entries retain their rights/status/bytes. Nine exact hashed
authored image outputs are separately indexed in `solkael_v002_generated_images.json`;
they are QA asset outputs, not newly approved design references. The historical
duplicate report only gains explicit QA-evidence exclusions. Existing duplicates
remain286groups/298extra origins; identical source/runtime texture bytes are
intentional generated exports, not a second character asset.

New source.blend,GLB,texture/evidence PNGs use scoped Git LFS. Recipes/manifests/import
settings use Git text.53 hydrated LFS paths were fetched in the validation clone;
fsck passes. Ignored .work contains downloads, SDK reports, debug keystore, APK/PCK,
staging projects and raw logs. No release credentials or history rewrite.

## Before / after measurements

| Measure | v001 | v002 |
|---|---:|---:|
|Triangles|24,912|27,488|
|Exported vertices|46,362|25,414|
|Materials/surfaces|9|1|
|Skinned meshes|1|1|
|Bones|71|71|
|Morphs + neutral expressions|9+1|9+1|
|Clips,30fps,no root motion|10|10|
|Textures|0|4×2048²|
|GLB bytes|4,784,156|7,262,440|
|Embedded PNG bytes|0|4,514,424|

Final GLB SHA256: `558a6566b8fa8a473f7f0b5460b68f73a365558b451a81a7208dc1fe82dc4108`.
Fresh recipe rebuild and independent export of the committed.blend produce identical
GLB bytes; Blender container bytes themselves include path/save metadata.

Production UV:32.51% triangle area occupancy, zero accidental overlaps/degenerate
triangles/OOB coordinates under independent clipping validation. Unique area-weighted
islands,.003spacing,8px gutters. Paintable first atlas; seam grouping/packing efficiency
remain debt. Base Color/Normal/ORM/Emissive are original procedural maps, no sampled
reference pixels. Neutral AO1.0, material-specific roughness/metalness; no baked-AO claim.
Raw full-mip RGBA8 upper estimate85.33MiB, shared by both instances. Actual VRAM is
renderer/compression dependent and not equivalent to that estimate.

Head mane2392triangles; tail tuft252. Opaque geometry, zero cards/transparency and
zero extra material; avoids alpha overdraw/grooming costs but still needs organic flow.
Continuous torso/upper arms, weighted spine, mouth interior/dentition/tongue, intact
eyes and closing lid surfaces are added. Limbs/armor are not a finished sculpt.

Punches add spine anticipation/head/tail recovery. Shared visual step-in is.10m
light/.24m heavy, decaying350ms. Contact-plane error is under9mm at the contractual
light/heavy contact for both sides; this is an axis-plane check, not full-body IK.
CPU-evaluated skinned floor minima remain approximately0m across all clips, including
KO. Damage/status/death remain resolver-authoritative. Ten clips/expressions remain.

## Scene, evidence and budgets

Two copies of the same mesh resource, controlled orthographic Camera3D, fighting
axis, neutral stage with depth, one shadow-casting directional key, unshadowed fill,
bounded opaque effects and minimal safe HUD. The same adapter handles either entity.
All12unchanged scenarios exercise intro/basic/heavy/skill/dodge/hit/shield/periodic/
reflection/KO/victory, speeds1/2/3, seek and cancellation.240 runtime assertions pass.
The intro is a visual prelude before the replay clock; no combat timestamp changes.

Actual renders include all four views, face/gauntlet/material, ten-expression grid,
guard/light/heavy/skill/hit/dodge/KO/victory, and barrier framing1366×768,844×390,
1080×486. Feet/mane/towers/barrier remain visible and HUD bands remain clear.
See `evidence/v1.20/REVIEW.md` and raw PNG/JSON evidence.

MEASURED: two fighters54,976base triangles,142bone instances,2surfaces sharing one
material/four images,9morph channels each.60s desktop RX7900XT/i5-13600K Vulkan Mobile
at844×390, first5s excluded: FPS p50=165; render GPU p50≈.087ms/p95≈.093ms;
render CPU p50≈.100ms/p95≈.121ms; process p50≈7.714ms/p95≈9.083ms. The engine process
monitor is not an additive wall-frame budget.16–20draw calls, roughly110k–112k
rendered primitives including shadow passes, static allocation around53–54MB and
131,776,576texture bytes for the entire viewport/stage. These are desktop diagnostics,
not Android guarantees or a minimum-device matrix.

PROPOSED:30ktriangles,1material,75bones,9morphs per fighter; one4×2048²texture set for
this mirrored pair;≤12simultaneous solid effects, one shadow light. Shared textures
must not be counted twice. Arena headroom and production phone budgets remain
unestablished. No high/medium/low branches without physical evidence.

## Android and tests

Reused Java17.0.15, Blender5.2.1LTS and Godot4.7.2stable. Installed official
Platform-Tools37.0.1, Build-Tools35.0.1, Platform35r2, command-line Tools22/latest,
CMake3.10.2.4988404, NDK28.1.13356709/r28b and exact4.7.2templates. No AndroidStudio,
replacement JDK, SDK36 or unrelated dependency. Standard SDK path is recorded in
V1_20_ANDROID.md. Only required official package licenses were accepted.

Official precompiled template inherits minAPI24/targetAPI36. Non-Gradle packaging
uses installed Build-Tools35 for signing; no Java compilation against Platform35
is claimed. Latest authorized apkanalyzer validates API36 XML. Export all game
resources avoids missing dynamic dependencies; retained v001 data is packaged but
not instantiated. Packaging minimization is future debt, no store-readiness claim.

Debug APK:38,558,965bytes, ARM64, `org.herosmash.qa`, version120/0.1.20-qa,
SHA256 `14e7ceb399cf763188270bbec9f4c40a5ca1f65962f98cdf045918a61e60b669`.
Fresh-checkout APK independently builds/boots; signing/container metadata changes
its hash, so APK byte identity is not claimed. Export command:

```powershell
& .work/venvs/canonical-ci/Scripts/python.exe tools/android/export_debug.py --godot .work/tools/godot-4.7.2/Godot_v4.7.2-stable_win64_console.exe
```

PASS: full foundation/archive/GPU resolutions, canonical11checks, combat15checks
including12000×2lab and baseline comparison, full roster/archive/phone proof,
full v001fighter/rebuild/154assertions, v002binary/UV/rig/material/face/animation,
two-fighter240assertions, exact v002rebuild/saved export, LFS hydration/fsck, SDK and
templates, APK signature/manifest/resources, exported-pack headless boot.
Remote runs34326529025/34326525522 at5fc4990 pass; final commit CI is rechecked at closure.
Node24 maintenance runs34322872209/34322865634 succeeded with empty warning annotations.

Resolved failures: missing spine vertex group; initial gamma/lid/mouth defects;
headless render-server skin bake unsupported (replaced with explicit CPU evaluation);
actual periodic tag is`dot`; same-tick start overwritten (prelude); measured light
contact overshoot; historical image-scope CI failure; initial export icon/ETC2/target
override errors; aapt35 API36 attribute incompatibility; scene-only APK missing
dynamic dependencies. A local combat invocation named the wrong comparison file;
rerun against existing`lab-summary.json` passes. These failed attempts are retained
in raw logs/clean-checkout evidence, not counted as final passes.

BLOCKED/SKIPPED: physical deployment, sustained phone timing/GPU/thermal/load/crash
assessment, device minimum matrix, iOS and store builds. No authorized phone exists.
The deploy/probe tool is ready but cannot be physically exercised. Owner final-art
review remains pending; no other hero or combat-balance change was started.

## Recommended v1.21

First obtain owner feedback on this exact model/expression sheet and connect one
authorized Android phone. Use the existing slice for≥120s sustained measurements;
record capabilities and missing counters. Prioritize lion facial planes/lids, flowing
mane, elbow/hip continuity, armor fit, less procedural paint and planted boxing/KO
weight. Only then adjust measured texture/shadow/effect budgets and trim APK resources.
Do not begin another hero, arena final art, quality tiers or minimum-device claims
before these gates. This is a recommendation, not a newly opened branch or phase.
