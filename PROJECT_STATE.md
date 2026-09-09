# Hero Smash — Project State

**State date:** 2026-09-09
**Macro phase completed:** v1.19 Blender Character Pipeline / First Fighter
**Phase status:** COMPLETE — technical pipeline with one Solkael model; final shipping art and physical-device acceptance pending
**Branch:** `revival/v1.19-golden-fighter-pipeline`
**Required baseline:** v1.18 / `d5ece76e09b175e7b75d12b2d0dd4f58b6d926b9`
**Full five-profile validation:** `fd0163b00f2c468de144450acd84e5907529e0d3`
**Final viewer / visual capture:** `e5b9b2ec688d19255ec338b3f41831b32db70f05`
**Committed evidence:** `f76586452135aa67ee10127d76bc60ca6f61a0ec`
**Post-evidence full fighter + roster + artifact integrity:** PASS at `f76586452135aa67ee10127d76bc60ca6f61a0ec`
**Main unchanged:** `66a5ba67f0691b7d50a11fa873f4ed24c80a14ef`

This documentation closeout follows executed local gates and actual visual review.
Its commit is named `docs: close v1.19 fighter pipeline and update project state`;
the exact closing SHA is in the task delivery report. The GitHub branch is published
with upstream; Draft PR #1 targets main without merge or auto-merge.

## 1. Current production reality

The production workspace is D:/Dev/HeroSmash. Technology remains Godot 4.7.2 stable,
typed GDScript, Mobile renderer, real-time 3D, 2.5D arenas, Android/iOS landscape,
Blender 5.2 LTS and validated GLB interchange. Existing deterministic combat/data
and the foundation main scene are unchanged. A separate Solkael source/export/
wrapper/QA pipeline is now implemented; no other hero or multiplayer was started.

The first model is an original editable parametric fighter with the approved
identity, integrated forearm tower gauntlets, sun-crown mane and palette. It is a
working model/rig/material/face/animation pipeline deliverable, not a claim of
finished sculpt, paint, realistic facial quality or owner acceptance of final art.
The QA stage is not the final arena or combat screen.

## 2. Art Lock and binary source authority

The owner approved eight exact PNGs under
`references/visual/characters/solkael_lionheart/production/`, verified against the
byte-identical SOLKAEL_ART_LOCK_v1_MANIFEST.json before admission. All eight central
manifest production_items carry generated-for-project source/rights,
production-approved approval and art_lock v1. No old unknown-rights entry changed.
Front covers neutral/silhouette functions per the owner's explicit eight-image
packet approval. No source-unsupported dimension is newly asserted as approved.

Only the newly supplied nine-file packet moved from
`references/visual/characters/production/Solkael_Art_Lock_v1/` to its canonical
folder. Initially tracked files were clean while this packet was untracked; it was
hashed and committed before modeling. No legacy/archive file moved or changed.
All 736 historical central items and 534 v1.18 content groups remain intact;
286 duplicate groups/298 extra origins remain historical reference-only data.
QA images are explicitly excluded from production-reference selection.

Editable source: `art/characters/solkael_lionheart/source/`.
Runtime authority: `game/assets/characters/solkael_lionheart/`.
Staging exports are ignored; Godot never depends on arbitrary .blend working files.
Scoped Git LFS covers eight PNGs, source .blend, runtime GLB and three curated AVIs.
Already installed LFS was initialized locally; published history was not rewritten.
Fresh GitHub hydration and fsck pass. Binary policy and admission details are in
`docs/art/BINARY_ASSET_GOVERNANCE.md` and `docs/art/SOLKAEL_ART_LOCK.md`.

## 3. Fighter and presentation contracts

GLB: 4,784,156 bytes; SHA-256
`3cd9e3024dbd85b8eaf3376e0e3e2b05f2aca6a4626794157e333a39b6400554`.
24,912 triangles, 46,362 exported vertices, one skinned mesh, nine opaque scalar
PBR materials/surfaces, 71 bones, zero textures. Nine independent relative morphs
plus neutral implement ten expressions. Ten named clips use 30 fps, documented
loops/markers and no root motion. Shared medium-biped semantics, five finger chains,
Solkael extensions, sockets and rest matrices are recorded in solkael_asset.json.
Skull height 1.95 m remains a proposal; crown/mane measured top is 2.099 m.

The reproducible recipe and saved-source exporter produce identical runtime GLB;
the committed editable source independently exports the same bytes without change.
Blender container save/path metadata is not misrepresented as deterministic.
Typed SolkaelFighter/FighterEventAdapter consume resolver IDs/timestamps and emit
cosmetic cues only. Dedupe, contact offsets, KO/revival, late events, interruption,
reflection, seek/cancellation and imported animation/morph/socket contracts pass.
The viewer binds real alpha/beta IDs; it does not replace canonical hero records.

## 4. Preserved roster, data and simulation

The v1.18 16-launch/4-reserve roster, all candidate identity records and 320-cell
oracle mapping remain unchanged. Other hero art-entry gates remain closed.
The canonical deck still has 150 cards, 582 levels, 12 branches, 8 active/4 banned,
90 Normal/36 Epic/24 Legendary and 84 single/66 dual records. No balance, economy,
rarity, card semantics or original oracle IDs were edited.
Ruleset combat_v1.17.1 and canonical version v1.16.1 retain dataHash
`932aaad64f3c805dbb60439d36213e253d2a7eb3d25e0e66d42bfc7c2c5359bf`.
All existing v1.17 runtime and legacy/web-prototype blobs are preserved; only the
explicitly enumerated new presentation assets/scripts/tests are added to game/.

The full 12,000-fight corpus repeated identically: all scenario metric hashes,
1,000 mirrors and 12 replay roundtrips match v1.17. Shield/healing timeouts, roughly
99% skill/Essence timeouts, fast Toxin and every prior balance signal remain
observations, not tuned or accepted production values. Thirteen limited effect
profiles and the unreviewed/unresolved numbered bindings remain exactly as before.

## 5. Executed gates and visual evidence

The clean GitHub clone passed all 66 checks: fighter 10, roster 12, canonical 11,
combat 15 and full local foundation 18. These include 17 binary regressions,
154 fighter assertions, existing 104 loader/8,150 effect assertions, full seeded
combat/replay/live-JS checks, 393 web blobs and 1,152 archive files. Relevant full
fighter/roster checks passed again after the evidence commit, along with SHA/length/
Git-blob or LFS-OID verification of all 44 curated artifacts and a clean tree.

Final 24 captures include both actual landscape sizes, all ten expressions,
front/side/back, contacts, KO/victory and three movies. All 1,623 movie JPEG frames
decode; frame-sampled review confirms geometry/framing, reactions, KO and barrier.
Toxin/Shield replay footage records 18/36 cosmetic cues and zero adapter errors.
Godot's short outer AVI RIFF-length field is corrected without image/audio edits;
the source/normalized hashes and correction are retained in movie-validation.json.
The caption strip prevents the phone victory pose from obscuring labels.

Desktop RX 7900 XT/i5-13600K, Vulkan Mobile, animated idle, 1,740 samples after
60 warm-up frames: CPU p50/p95 0.079/0.104 ms at 1366×768 and 0.076/0.100 ms at
844×390; GPU 0.088/0.090 and 0.094/0.099 ms. Raw counters show five draw calls,
50 objects and 51,456 primitives including QA stage/shadows/canvas. These are not
physical-phone results, material submission counts or two-fighter arena budgets.

No final required local gate failed. Development asset, UTF-8 and viewer issues
were fixed and documented. The two known legacy JS readability failures remain
an explicitly checked negative baseline. GitHub portable Actions passed at f765864;
final delivery records the latest remote result separately from local full gates.
Artifacts/commands/limits: `docs/qa/evidence/v1.19/REVIEW.md` and macro report.

## 6. Existing toolchain and unavailable gates

Godot 4.7.2.stable.official.ed1daf0bf and Steam Blender 5.2.1 LTS execute successfully.
Existing Python 3.12/3.14, Pillow, Node 20.19.6, Git 2.55, LFS 3.7.1 and Java 17.0.15
were reused. No engine, SDK, MCP, package or global dependency was installed.
ANDROID_HOME points to absent C:/Users/olive/AppData/Local/Android/Sdk;
adb/sdkmanager unavailable, Godot export templates empty. Physical Android/iOS
performance, packages, signing, device smoke and Apple toolchain checks are
unavailable and not passed. Final mobile budgets await representative arena/fighters.

## 7. Debt and next proposed macro phase

Visible art debt: continuous anatomy, mane/crown/glove fidelity, mouth/face polish,
paint-ready UV atlas, material finishing, secondary motion and KO settling. Current
planar UVs support tangents but not a shipping paint atlas. A second morphology,
retarget/hurtbox/arena integration, final VFX/audio and physical-device measurement
are unvalidated. Reference approval does not automatically approve the final model.

Existing gameplay/economy debt remains: 097/111/132/009 semantics, most numbered
bindings/status conversions, market UI3/helper4, interest/sell/run-HP discrepancies,
combined oracle-kit gaps and LCG review. No new rule silently resolves these.

**Proposed v1.20:** refine this same Solkael against the eight approved boards and
review the concrete 3D result; prepare UV/material and animation/contact finishing;
exercise two instances in a neutral 2.5D QA stage against unchanged resolver streams;
then detect/report an authorized Android device/toolchain and measure sustained
performance before locking budgets. No other hero, balance or multiplayer work.
This next phase has not started and no new installation is authorized by this report.

Full macro report: `docs/qa/V1_19_FIGHTER_PIPELINE_REPORT.md`.
