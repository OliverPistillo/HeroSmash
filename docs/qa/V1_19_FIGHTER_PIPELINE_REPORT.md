# v1.19 — Solkael first fighter pipeline

The approved eight-image Art Lock now feeds an editable Blender source, validated
GLB, typed Godot wrapper and CombatEvent presentation adapter. One original Solkael
base-form pipeline model is implemented. This closes the technical first-fighter
scope; it does not assert final shipping sculpt/texture fidelity or owner acceptance
of the finished 3D art. No other hero, balance rule or gameplay data was changed.

## Git and scope

Work branch: `revival/v1.19-golden-fighter-pipeline`, from
`d5ece76e09b175e7b75d12b2d0dd4f58b6d926b9`. Main remains
`66a5ba67f0691b7d50a11fa873f4ed24c80a14ef`.
The initial tracked tree was clean; the newly supplied nine-file Art Lock packet
was untracked. Its hashes were checked and the packet committed before modeling.
This exception to an entirely empty porcelain output was recorded, not hidden.

Fetch origin/tags, the four requested historical branch pushes and existing tag
pushes succeeded. The v1.18 tag resolves exactly to d5ece76. The new branch has an
origin upstream. Draft PR [#1](https://github.com/OliverPistillo/HeroSmash/pull/1)
targets main; no merge, auto-merge, force-push or history rewriting.

| Published historical branch | Commit | Published tag |
| --- | --- | --- |
| revival/v1.15-foundation | 80c098b256f5855d4c5dfb9869135fd2bad6c709 | v1.15-foundation |
| revival/v1.16-canonical-data | 87c1d0e4ba519e082feaf70848c84862acedc0ff | v1.16-canonical-data |
| revival/v1.17-combat-balance-lab | 337710e362b1df008b74cbb1e2ba6d1c58d2f2da | v1.17-combat-lab |
| revival/v1.18-hero-reference-lock | d5ece76e09b175e7b75d12b2d0dd4f58b6d926b9 | v1.18-hero-reference-lock |

Implementation commits, in order:

- `2ccab0f`: admit approved Solkael Art Lock and govern production binaries.
- `ea584fd`: build and validate reproducible skinned Solkael asset.
- `8e69428`: present CombatEvents with tested playback and replay safety.
- `fd0163b`: saved rest-matrix validation and animated capture instrumentation.
- `1f975a5`: movie framing/container verification and capture tooling.
- `83e670a`: actual resolver identity binding and explicit UTF-8 metadata reads.
- `e5b9b2e`: reserve a caption strip outside the fighter pose envelope.

`f765864` records the reviewed evidence and macro report. The documentation
closeout follows; its exact SHA is in the task delivery report. Post-evidence
fighter 10/10, roster 12/12, 44 artifact checks and GitHub Actions passed at f765864.
No new v1.19 release tag is invented.

## Source admission and resulting structure

`references/visual/characters/solkael_lionheart/production/` contains the eight
SOLKAEL PNGs and byte-identical `SOLKAEL_ART_LOCK_v1_MANIFEST.json`. The packet moved
from the supplied `references/visual/characters/production/Solkael_Art_Lock_v1/`
after SHA-256/length validation. No legacy/archive file was moved or deleted.

The central manifest retains all 736 historical `items` unchanged and adds eight
`production_items`: front, 3quarter, side, back, gauntlets, materials, combat and
expressions, with the exact owner-supplied IDs. Each records generated-for-project
source/rights, production-approved approval and art_lock v1. The old 534 content
groups remain unknown-rights. The historical 286 duplicate groups/298 extra origins
are retained; new QA captures are excluded from source selection.

The eight PNGs total 16,774,389 bytes. Supplied manifest SHA-256:
`35011af3e80bca0ec90febd6a912ec7ceee93526598707786c5f504ba8eea2a3`.
Only these approved images guided the original geometric model. No reference
pixels became runtime textures; no autonomous references were generated.

```text
references/visual/characters/solkael_lionheart/production/  # 8 PNG + packet manifest
art/characters/solkael_lionheart/
  source/chr_solkael_lionheart_v001.blend                  # editable, Git LFS
  solkael_asset.json                                     # rig/rest/clip/morph metadata
  README.md
  exports/                                              # ignored staging only
game/assets/characters/solkael_lionheart/
  chr_solkael_lionheart_v001.glb                          # validated runtime, Git LFS
  chr_solkael_lionheart_v001.glb.import
  fighter_presentation.json
game/scenes/characters/solkael_lionheart/hero_solkael_lionheart.tscn
game/scripts/presentation/{fighter_event_adapter,solkael_fighter}.gd
game/tests/{fighter_test,fighter_review}.gd
tools/asset_pipeline/                                    # build/export/GLB/capture tools
tools/validation/{fighter,fighter_negative_test}.py
docs/qa/evidence/v1.19/                                  # hashes, gates, PNGs, 3 AVIs
```

Git LFS 3.7.1 was already present; only repo-local setup was performed. Scoped
patterns cover the eight new PNGs, source .blend, runtime GLB and three curated
AVIs. CI hydrates LFS. Historical blobs are untouched. A real GitHub clone recovered
all ten production objects before gates; final evidence hydration is checked again.
Raw captures, backups, caches and staging exports remain ignored.

## Fighter and runtime measurements

| Metric | Measured value |
| --- | --- |
| GLB size / SHA-256 | 4,784,156 bytes / 3cd9e3024dbd85b8eaf3376e0e3e2b05f2aca6a4626794157e333a39b6400554 |
| Triangles / exported vertices | 24,912 / 46,362 (UV/normal seams duplicate vertices) |
| Mesh / materials / surfaces | 1 skinned mesh / 9 opaque scalar PBR materials / 9 surfaces |
| Bones / textures | 71 / 0, texture bytes 0 |
| Facial controls | 9 independent relative morph targets + neutral = 10 expressions |
| Animation | 10 named clips, baked 30 fps, documented loops/markers, no root motion |
| Bounds | X ±1.2765 m, floor approximately 0, crown/mane top 2.099 m |
| Scale proposal | 1.95 m skull height retained as a proposal, not a dimension inferred from images |

Medium-biped semantic hierarchy includes articulated fingers, Solkael ears/mane/
four-segment tail and named sockets. Saved neutral T-pose, unit transforms, skin
weights, rest matrices, morph amplitudes and imported clip names are validated.
Reconstruction produces identical GLB and source JSON; the committed editable
.blend independently exports that same GLB without mutation. Blender container
save/path metadata prevents claiming byte-identical .blend reconstruction.

The wrapper maps immutable resolver IDs/timestamps to poses and cosmetic cues.
Tests exercise late/duplicate/conflicting events, contact offsets, reflection,
interruption, KO/revival, rewind/seek and missing clips. A replay seek cancels
cosmetics and reconstructs state without replaying one-shot effects. The adapter
does not apply damage or replace a canonical hero definition.

Desktop: i5-13600K, AMD Radeon RX 7900 XT, Vulkan Mobile, Windows; 1,740 samples
after 60 warm-up frames at each resolution, animated idle, single fighter + QA stage.

| Resolution | Render CPU p50 / p95 | Render GPU p50 / p95 | Frame p50 |
| --- | --- | --- | --- |
| 1366×768 | 0.079 / 0.104 ms | 0.088 / 0.090 ms | 6.061 ms |
| 844×390 | 0.076 / 0.100 ms | 0.094 / 0.099 ms | 6.062 ms |

Raw Godot counters: 5 draw calls, 50 rendered objects, 51,456 rendered primitives
including stage/shadows; these are viewport counters, not a claim of five material
submissions. Video memory approximately 77.5/69.4 MB, texture memory 50.4/42.3 MB
for the whole viewport/stage. The fighter itself has no texture assets. Movie-mode
timings are excluded from performance conclusions. No final phone budget is set.

## Validation and evidence

Fresh GitHub checkout at `fd0163b00f2c468de144450acd84e5907529e0d3` passed all 66
checks: fighter 10, roster 12, canonical 11, combat 15, foundation 18. The full
combat run performed 12,000 fights twice, 1,000 mirrors and 12 replay roundtrips;
all deterministic metric hashes match the v1.17 baseline. The 150-card/582-level
data, 393 web blobs and all 1,152 archive files remain preserved.

After viewer/UTF-8 fixes the complete fighter profile passed again at
`83e670a323cef662608bbb91e0c9e29e02097df9`, including independent reconstruction,
17 binary regression cases and 154 Godot assertions. Original gameplay files did
not change. Full simulation was not needlessly repeated for QA-only changes.

Actual-resolution stills, front/side/back, attacks/bulwark/KO, ten expression
portraits and the foundation sample were inspected. Three final 1366×768 movies
contain 901/361/361 frames, approximately 30/12/12 seconds; all 1,623 JPEG frames
decode. Frame-sampled visual review confirms clip geometry, barrier visibility,
reaction/KO and intact framing. Resolver footage uses real alpha entity events:
Toxin 18 cosmetic cues; Shield/healing 36; zero adapter errors. This is an explicit
QA stage and bounded replay footage, not a complete combat-screen playtest.

Exact commands/results/hashes and visual limitations are in
[evidence/REVIEW.md](evidence/v1.19/REVIEW.md), the gate JSONs and
[FIGHTER_VALIDATION.md](FIGHTER_VALIDATION.md).

## Corrected failures and remaining limits

During development: sparse GLB morph accessors, UV/tangent import errors, initial
guard alignment, cumulative/nonneutral Blender morphs and KO floor offsets were
corrected. Negative tests now reject the malformed asset conditions. Final review
also corrected movie viewport cropping, blank terminal clip captions and the QA
replay's demonstration ID mismatch. A Windows cp1252 default produced a false
historical-manifest mismatch; explicit UTF-8 reads fix it, and original items are
unchanged. These failures are not counted as final passes before correction.

Godot's AVI writer declares an outer RIFF size 70 bytes short. The evidence tool
checks all nested bounds and frame counts, then changes only that four-byte field;
original hashes and the exact correction are recorded. JPEG/audio bytes are not
edited. The single initial engine frame is reported rather than discarded.

Godot 4.7.2.stable.official.ed1daf0bf and installed Steam Blender 5.2.1 LTS execute
successfully. Python 3.12/3.14, Node 20.19.6, Java 17.0.15 and Git 2.55 were reused.
No engine, SDK, MCP, package or global dependency was installed. ANDROID_HOME points
to an absent SDK directory; adb/sdkmanager are unavailable, export templates empty.
Physical Android/iOS performance, package/signing/install tests and Apple toolchain
are unavailable, not passed. GitHub portable CI is separate from full local/device
coverage; final remote status is recorded at delivery.

Art debt is visible: segmented parametric anatomy, coarse crown/mane clumps,
simple facial/mouth forms, unpainted scalar materials and limited secondary motion.
Planar per-face UVs support tangents but are not a shipping paint atlas. KO contact
is technically grounded but needs weight/settling polish. No final art approval,
retarget across a second morphology, arena/hurtbox integration, two-fighter budgets
or finished VFX/audio is claimed. Historical gameplay/economy debt remains unchanged.

## Precise next proposal

Propose v1.20: refine this same Solkael against the approved eight boards (continuous
anatomy, crown/mane, integrated glove detail, readable mouth/expressions, contact and
KO settling), then obtain review of the concrete 3D result. Prepare a paint-ready
UV/material pass with measured costs. Exercise the existing wrapper twice in a
neutral 2.5D QA arena using unchanged resolver streams, with live/seek/cancel parity
and landscape framing. Detect an authorized physical Android device/toolchain,
report missing components before any installation, and measure sustained CPU/GPU/
memory for two fighters. Keep all other heroes, balance and multiplayer out of scope.
This proposal is not execution or authorization for a new macro phase.
