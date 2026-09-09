# Hero Smash — Project State

**State date:** 2026-09-09
**Macro phase completed:** v1.20 Solkael Polish & Device Slice — technical iteration
**Status:** COMPLETE TECHNICAL PIPELINE; owner final-art review pending; physical-device gate BLOCKED
**Branch:** `revival/v1.20-solkael-polish-device-slice`
**Baseline:** `f03a1b3833055b2538f1780bcc4a649830981195` / completed v1.19
**Full clean-checkout validation:** `5fc4990f6c8883c0f964bc10851032ea1d96101f`
**Final Android correction and clean export:** `1bf8e0495d0d33abc3f74735f45d9e8e4679bb9f`
**Remote implementation CI:** PASS, runs34326978019 and34326973733
**Closure tag:** `v1.20-solkael-polish-device-slice` resolves the final documentation commit, verified in task delivery
**Main unchanged:** `66a5ba67f0691b7d50a11fa873f4ed24c80a14ef`

This update follows executed local/fresh-checkout gates. The closing commit is named
`docs: close v1.20 technical slice with explicit art and device gates`; its exact SHA
is in the task delivery and annotated tag. Draft PR#2 targets main without merge or
auto-merge. PR#1 is untouched. No v1.21 branch exists.

## Current production reality

Workspace D:/Dev/HeroSmash. Godot4.7.2stable, typed GDScript, Mobile renderer,
real-time3D characters,2.5D stage, Android/iOS landscape, Blender5.2LTS and GLB
interchange remain locked. Existing deterministic combat/data and production
bootstrap main scene are unchanged. No other hero, balance rule or multiplayer added.

Solkael v002 is a first textured polish iteration: continuous torso/upper-arm rings,
spine weighting, muzzle bridge, mouth cavity/teeth/tongue/chin, intact eyes/closing
lid surfaces, layered opaque mane and original PBR atlas. It remains visibly simpler
than the Art Lock: NOT final art, finished sculpt/paint or owner artistic acceptance.

Two instances of one shared v002GLB/wrapper replay all12unchanged CombatResolver
scenarios in a separate neutral QA stage with controlled camera, depth/shadows,
bounded solid effects and safe minimal HUD. Both sides share presentation logic.
Toxin/reflection cues, x1/x2/x3, seek/cancel, KO/victory and contact checks pass.
Visual step-in is.10m light/.24m heavy; it never changes simulation timestamps or
damage/status/death. A one-second intro prelude holds the replay clock before t=0.

## Canonical sources and binaries

Only the eight unchanged Solkael Art Lock v1 production-approved PNGs guide art.
Their source_type/rights_status remain generated-for-project, approval
production-approved, art_lock v1. No unknown-rights image is promoted.736historical
central entries/534v1.18content groups remain intact;286duplicate groups/298extra
origins remain reference-only. Nine exact hashed authored QA image outputs have a
separate generated-output manifest; they are not new design references.

v001 source/GLB/recipe are retained byte-for-byte. No legacy/archive file moved,
renamed or deleted in v1.20. New editable source:
`art/characters/solkael_lionheart/v002/source/chr_solkael_lionheart_v002.blend`;
four PNG maps and source manifest stay alongside. Runtime authority is the versioned
v002GLB/wrapper under game/assets and game/scenes/characters/solkael_lionheart.
Sources/GLB/texture/evidence PNGs use scoped Git LFS; recipes/manifests/import settings
use text Git.53LFS paths hydrate in the clean clone; fsck passes. No history rewrite.

## Measured fighter and stage

GLB7,262,440bytes, SHA256
`558a6566b8fa8a473f7f0b5460b68f73a365558b451a81a7208dc1fe82dc4108`.
27,488triangles/25,414exported vertices, one mesh/material/surface,71bones,
four2048²textures,9independent morphs+neutral,10clips at30fps, no root motion.
Fresh recipe and saved-source export produce identical GLB bytes. v001 remains
24,912triangles/9materials/0textures for comparison.

UV overlap/degeneracy/OOB checks pass; area occupancy32.51%, unique islands with
8px gutters. PBR maps are original mathematical detail, no reference pixels or
baked-AO claim. Head mane2392triangles/tail tuft252; zero alpha cards/transparency.
Atlas grouping/efficiency and shading quality remain art debt.85.33MiB is the raw
RGBA8 full-mip estimate, not measured Android residency.

Two fighters54,976base triangles,142bone instances,2surfaces sharing one material/
texture set. One shadow key and≤12solid VFX.60s desktop RX7900XT/i5-13600K profile
at844×390 is separate from physical mobile evidence. Proposed30ktriangles/1material/
75bones/9morphs per fighter are engineering envelopes only. Phone budgets, arena
headroom and minimum-device matrix remain unestablished.

## Validation and toolchain

PASS: full foundation/archive/GPU at both landscape resolutions; canonical11checks;
combat15checks including12,000fights repeated and compared with v1.17; full roster/
archive/historical phone proof; full v001fighter/rebuild/154assertions; v002binary/
UV/material/rig/expression/animation and240two-fighter assertions; saved/isolated GLB
reconstruction; LFS hydration/fsck; actual model/landscape renders and exported-pack
headless boot. Gameplay dataHash remains
`932aaad64f3c805dbb60439d36213e253d2a7eb3d25e0e66d42bfc7c2c5359bf`.
Resolved failures and corrected comparison-command invocation are in the report.

Reused Godot4.7.2.stable.official.ed1daf0bf, Blender5.2.1LTS, Java17.0.15,
Python3.12, Pillow, Node20.19.6, Git/LFS/gh. Official Android installation was
explicitly authorized: Platform-Tools37.0.1, Build-Tools35.0.1, Platform35r2,
cmdline-tools22/latest, CMake3.10.2.4988404, NDK28.1.13356709/r28b, exact4.7.2
templates. No AndroidStudio, replacement JDK, SDK36 or unrelated global tools.

Debug ARM64 APK38,558,965bytes, org.herosmash.qa/version120: signature, manifest,
critical packaged dependencies and independent pack boot pass. Fresh checkout
repeats export. Official precompiled template inherits minAPI24/targetAPI36;
required SDK35 remains installed and Build-Tools35 signs it. This documented
discrepancy is not Java compilation against Platform35. No AAB/store/release
credentials. Debug key/APKs/staging stay ignored under.work.

**PHYSICAL DEVICE BLOCKED:** repeated adb discovery finds no authorized phone.
No actual deployment, thermal, sustained phone frame/GPU/memory/load/crash evidence.
Connection/deploy commands are in V1_20_ANDROID.md. iOS/Apple/store remain out of scope.
Official Actions moved to pinned Node24v6 separately; CI succeeds without the prior
Node20 action-runtime warning. Legacy Node workload remains pinned20.19.6.

## Debt and next proposed macro phase

Owner art review is required. Lion facial planes/lids, organic mane rhythm, elbow/
hip continuity, armor wrap, paint grouping/roughness detail, planted boxing weight,
secondary motion and KO aesthetics remain unresolved. Runtime captures make these
limitations reviewable; technical checks never auto-approve shipping art.

Physical Android/device matrix/arena headroom are blocked by absent hardware.
No quality tiers without measurements. APK currently packages all game resources,
including retained v001; trim only with dependency/boot validation. Existing gameplay/
economy debt remains:097/111/132/009 semantics, numbered/status bindings, market UI3/
helper4, interest/sell/run-HP discrepancies, oracle-kit gaps and LCG review. No new
rule silently resolves them.

**Proposed v1.21:** owner-guided revision of this exact Solkael plus one authorized
physical Android profile of≥120s; then adjust measured budgets and packaging. No
additional hero, final arena, balance, multiplayer or automatic phase start.

Report: `docs/qa/V1_20_POLISH_DEVICE_REPORT.md`.
Art review: `docs/qa/evidence/v1.20/REVIEW.md`.
Prior state/history: `docs/qa/V1_19_FIGHTER_PIPELINE_REPORT.md`.

## Blender MCP bootstrap repair — 2026-09-09

Owner-authorized integration repair; no artistic macro phase completed. Solkael
art remains suspended. Original D:/Dev/HeroSmash stays on
revival/v1.20-solkael-polish-device-slice at
555d26c9fe9373379d316c4d655f7dbd8ff100cd, preserving its pre-existing v003 commit,
tracked art-plan diff and untracked evidence. All 45 Solkael and 127 evidence files
match their before/after hashes. Main, tags and production pipeline are unchanged.

The separate technical worktree D:/Dev/HeroSmash-mcp-bootstrap-fix uses
chore/blender-mcp-bootstrap-fix, based directly on remote v1.20
de770dff30dcc533d547074c975fdaa0962abda9. Only the inspected documentation commit
555d26c was imported (as 7e0ab92); art commit72170ba is not an ancestor of this branch.

**Current after reconnect: CONFIGURED / SERVER PREFLIGHT PASSED /
SESSION TOOLS DISCOVERED / LIVE OPERATIONS NOT VERIFIED.** See the current
acceptance note below; the remaining bootstrap details describe the earlier repair.

Mandatory community upstream5f8ddaf6e987c4aa0c3467fcc548838b28f64477 plus explicit
local patch hsfix1-telemetry-disabled, SHA-256
c58383fdcd9c109cb819f0d91b9c0809fd5dcf74f98ae06b871f55e342700ad8.
This is modified upstream, not a pristine upstream installation. The separate
5f8ddaf6-hsfix1 venv uses the same 32 runtime dependency versions; original source,
venv, add-on and dedicated preferences remain intact for rollback. Server1.9.1,
add-on1.6/protocol5, MCP SDK1.30.0, Python3.12.0, Blender5.2.1LTS unchanged.

The missing config import is bypassed only through an explicit disabled telemetry
path. Missing optional config also fails closed with a warning. Real add-on consent
reads remain distinct; opt-in prompts and trajectory capture are suppressed while
disabled. No endpoints, credentials, safe-mode or execution-contract changes.

PASS: 15 unit tests, six real decorated tool functions with simulated transport,
instrumented zero telemetry attempts, safe-mode regression, source/patch hashes,
fresh patch application, dependency consistency and preservation checks. Real
STDIO initialize/initialized/tools-list returned 28 upstream tools and closed
gracefully with exit0; Codex retains the separate six-tool allowlist. The diagnostic
performed the normal read-only add-on handshake, with no tools/call or scene edits.

Only the Codex server command changed after backup; prompt approval, safety env,
STDIO/timeouts and other MCPs are preserved. Existing add-on consent=False/cloud
opt-outs and loopback127.0.0.1:9876 are preserved. This is not OS filesystem or
general network confinement. Human approval UI and real session tool availability
still require verification. All original live A–I gates remain pending.

Report, reproducible commands and residual upstream debt:
docs/codex/BLENDER_MCP_BOOTSTRAP_FIX.md. Patch/tests: tools/mcp_bootstrap/.
Local continuation: D:/Dev/HeroSmash/.work/blender-mcp-smoke/HANDOFF.md.
After an owner-controlled reconnect, resume only the actual session MCP smoke
tests on the disposable scene. Art remains suspended after those checks as well.

## Blender MCP live reconnect acceptance — 2026-09-09

Integration-only acceptance attempt completed on chore/blender-mcp-bootstrap-fix
from exact clean/tested commit e42aa96900040fd2aabbe837db9777190dcd9800; no artistic
macro phase or product decision changed. Six actual session tools were discovered;
four were invoked. After relaunching only the absent dedicated GUI with its existing
profile, real MCP status/scene/viewport reads succeeded. New unsaved Scene contains
only Cube/Camera/Light; original GUI PID196 is preserved.

The first read-only execute_blender_code was rejected on a preference read by
actual safe mode before Blender dispatch. No expected human approval prompt was
observed. Per owner instruction, no scene mutation or second code probe followed.
A/B PASS, E/I PARTIAL, C/D/F/G/H NOT RUN; LIVE OPERATIONS NOT VERIFIED.
Managed hsfix1 command, actual safe-mode/telemetry opt-out environment, add-on
consent=False and loopback listener were observed separately. Current cloud flags
and successful code approval remain unverified. No permission/configuration fix,
dependency change, new asset, scene save or production migration was made.

45 Solkael files and127 pre-existing evidence hashes, original branch/HEAD/diff,
main and tags remain unchanged. Art72170ba remains excluded from the technical
branch. Only integration documentation is updated; actual tool JSON and MCP PNG
stay in the documented smoke directory. Whitespace/link checks and new-commit CI
results are reported with publication in Draft PR3 and the task delivery.

Report: docs/codex/BLENDER_MCP_LIVE_RECONNECT.md. Remaining work is intended approval
verification, fresh cloud opt-out verification and the pending approved live suite.
No automatic next macro phase: Solkael v003 remains suspended.

## Blender MCP approval audit/fix — 2026-09-09

Integration configuration phase completed on chore/blender-mcp-bootstrap-fix from
exact clean baseline c4efd683cb500d09c5b4fe9d12887dd76bfdab1e. No art/product decision
or production system changed. Installed0.153.4 config/read(includeLayers) resolved
the user and empty system layers for both worktrees; configRequirements/read
returned null. Active-task records independently show never/user with Full Access.
The resident desktop's managed-policy response was not directly available.

After an exact local backup, only approval_policy in the effective user config
changed never→on-request. Reviewer user and execute_blender_code prompt were already
correct. Every other byte/value, including sandbox, other MCPs and Blender's server,
allowlist, telemetry/safe mode, addresses and timeouts, is preserved. Strict fresh
config resolution now returns on-request/user/prompt. The active task still has
never/user; no runtime override, restart or Blender call was attempted.

**APPROVAL CONFIG FIXED — RESTART REQUIRED / LIVE OPERATIONS NOT VERIFIED.**
Marker-only probe passes static safe-mode validation; human prompt and live A–E
probe are not verified. C–I remain pending. Owner restart must be followed by an
actual-session override check before the first marker probe; saved Full Access
state is not assumed to disappear automatically. No blind managed-policy workaround.

Only integration documentation is published in Draft PR3; personal backup and
sanitized audit/preservation evidence remain in the documented smoke directory.
TOML, exact-change, layer-resolution, preservation and documentation checks pass;
published-commit CI is reported in PR/task delivery. No game/export/preflight rerun.
Report: docs/codex/BLENDER_MCP_APPROVAL_AUDIT.md. No automatic continuation of Solkael.

## Blender MCP smoke resume after owner restart — 2026-09-09 15:39

Attempted only the authorized smoke continuation on chore/blender-mcp-bootstrap-fix,
starting at exact clean commit1ef2c6b3130a5b95f11e06f63b523adfc5066782. Actual new
Desktop PID13016 confirms restart. New turn01a08664-f96e-7580-ab2a-29e82d1f33ef
nevertheless records approval_policy=never, approvals_reviewer=user and Full Access.
Fresh disk/layer resolution remains on-request/user with the unchanged per-tool
prompt rule; the resident tool rule is not directly readable. Managed requirements
return null from the separate resolver, with no direct resident response available.

The effective on-request prerequisite failed, so zero Blender calls were made:
no marker/prompt test and no C–I continuation. No setting, installation, scene or
production system changed. All45 Solkael/127 evidence hashes, original worktree,
main and six tags are preserved; art72170ba is excluded. Only current integration
documentation is updated. Whitespace/link and published-commit CI results accompany
PR/task delivery. LIVE OPERATIONS NOT VERIFIED. Effective task approval settings
must be corrected/verified before another marker attempt; restart alone has not
resolved them. No automatic permission repair or artistic macro phase follows.

## Blender MCP live acceptance completed — 2026-09-09

**BLENDER MCP OPERATIONAL.** Integration acceptance completed on
`chore/blender-mcp-bootstrap-fix`, starting at exact clean commit
`c41114b0c068c4627331ef4b95982c87244e08c9`; the resulting documentation commit and
its CI are recorded in Draft PR #3. No product decision or artistic phase changed.

The owner selected Ask for approval. The actual task records on-request/user;
the owner explicitly confirmed human prompts and manual Approve for both exact
marker attempts. The first failed to connect; starting the existing dedicated GUI
allowed the identical retry to return HS_MCP_APPROVAL_PROBE. All C–I then passed
through session MCP, with only the specified GUI listener controls for H.
Temporary edits were restored numerically and visually. Save/reopen discarded an
intentional unsaved change. Disconnect/Connect was verified by failed/successful
MCP reads; the negative import was rejected by actual safe mode before dispatch.

Only integration documentation and authentic smoke screenshots are published.
Screenshots use docs/qa/evidence/blender-mcp/20260909; the generated duplicate report
adds exactly two QA-evidence exclusions while the art reference inventory is unchanged.
The temporary .blend and sanitized detailed results remain in the smoke directory.
All 45 Solkael, 127 prior evidence, 3822 original-installation and 20 hsfix1 source/
installed hashes pass; 32 dependency versions, original worktree, main and six
tags are preserved. Art commit 72170ba remains excluded. Whitespace/link checks,
artifact hashes and exact published-commit CI accompany delivery. No game runtime,
production Blender export or historical preflight test was rerun for this docs phase.

Known debt: the add-on sidebar can show Not connected after reopening while its
persistent listener is live; Connect resynchronizes the indicator, and the real
reconnect test passed. Personal configuration comparison is recorded in the audit.
Reports: docs/codex/BLENDER_MCP_SMOKE_TEST.md and BLENDER_MCP_APPROVAL_AUDIT.md.
No next macro phase is started. Solkael v003 remains suspended.
