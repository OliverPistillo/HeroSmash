# Solkael v003 — owner-guided Pass 1

Status: BASELINE INTEGRATED; INTERACTIVE PASS 1 NOT STARTED.
Final artistic status must remain **OWNER REVIEW REQUIRED**.
Authority: owner's 2026-09-09 request, "INTEGRA BLENDER MCP E AVVIA SOLKAEL V003 / PASS 1".

## Branch and recovered baseline

Work only on `art/solkael-v003-owner-polish`, based on updated remote v1.20
`904ca9fcd52fdb4ab7e7460e0bf20c38022b3ba8` after the authorized merge of PR #3.
The original worktree, uncommitted review work and commit
`72170ba0295aa992ca1ac7a7954cdb41da5222d3` remain intact.

The old commit was inspected before recovery: 31 of 32 files were transferred
in two commits, asset baseline `d24c314` and export/QA support `ae4add7`.
`tools/android/export_debug.py` was excluded: this pass does not need the old
Android packaging extension. No paths overlapped the MCP merge.
See [integration evidence](../../qa/SOLKAEL_V003_PASS1_INTEGRATION.md).

Recovered v003 includes historical body, armor, material and animation edits
from 72170ba. Those bytes are the technical baseline, not new edits or acceptance
of those areas in Pass 1. Preserve them throughout this pass. The existing broad
`solkael_v003.py` remains a baseline reconstruction recipe; do not change its
body or animation routines as part of head polish.

## Current execution prerequisite

Actual turn `01a086af-9512-7313-9a06-f6e42766ed2c` resolves
`approval_policy=on-request`, `approvals_reviewer=auto_review`, model
`gpt-6-astra`, effort `xhigh`. The owner requested human review and Ultra.
No Blender MCP call has been made in this turn. No configuration was modified.

Before interactive work, verify a new effective turn with reviewer `user` and
the requested Ultra effort. Keep `execute_blender_code` set to `prompt` and
require real human tool approval before dispatch. Automatic review or ordinary
chat consent does not substitute. Preserve safe mode, telemetry opt-out, cloud
opt-out, allowlist, server and loopback settings.

## Authorized visual scope

Use only the eight production-approved Art Lock v1 images in
`references/visual/characters/solkael_lionheart/production/` as the visual target.
v002 and recovered v003 are technical/model baselines, not visual authorities.

Work one observable macro area at a time:

1. Face/muzzle: stronger lion bridge, separate muzzle masses, cheek/jaw planes,
   upper lip, integrated mouth cavity and chin; noble, stoic guardian in neutral.
2. Eyes/lids: readable iris/pupil, organic upper/lower lids, closure without
   penetration; focused/aggressive driven mainly by lids/brows. Ears only if needed.
3. Mane/sun crown: grouped opaque masses, deliberate crown and side/back flow;
   remove uniform radial spikes without expensive grooming.
4. Evaluate neutral, focused, aggressive, pain_heavy and victory, preserving identity.

No intentional edits to torso, shoulders, arms, hips, legs, paws, tail, gauntlet
or armor design, global materials, combat animations, gameplay or another hero.

## Interactive work and reproducibility

Open recovered v003 in the dedicated GUI; inspect scene/object via MCP and
capture the initial MCP viewport. After each macro edit inspect front, three-quarter
and side; restore locally if it reduces Art Lock resemblance. Check dependent
morphs before the next area. Save a new Pass 1 source, never over v002.
Keep versioned CLI export/validation and a reproducible record of MCP edits.

Protect baseline rig/rest/bind hierarchy, non-head geometry/weights, materials,
textures and actions by comparison with recovered v003. Retain nine morph names
plus neutral, ten clip contracts at 30 fps, 71 bones, one material and four
2048-square maps unless an authorized head-only exception is explicitly documented.

## Required evidence and stop

Generate authentic model renders: `01_front.png`, `02_3quarter.png`, `03_side.png`,
`04_face_closeup.png`, `05_neutral.png`, `06_focused.png`, `07_aggressive.png`,
`08_pain_heavy.png`, `09_victory.png`, `10_mane_front.png`,
`11_mane_3quarter.png`, `12_mane_back.png`.

Deliver `SOLKAEL_V003_PASS1_REVIEW.md` with exact changes, triangle/bone/morph
deltas, Art Lock and v002 comparisons, hashes, validation and unresolved problems.
Use **OWNER REVIEW REQUIRED**, never final-art approval. Package report and
renders as `.work/review-packages/Solkael_v003_PASS1_OWNER_REVIEW.zip`.

Final checks: source opens, rig/morph validity, saved-source export, valid GLB,
Godot import smoke and v002/reference/gameplay preservation. Recovered baseline
already passes nine checks, including exact reconstruction and 240 runtime
assertions for each version; these do not validate future edits.
No separate 12,000-fight rerun is required for head-only work with unchanged gameplay.

Publish small commits to a Draft PR titled
`Solkael v003 — Owner-guided art polish`, base
`revival/v1.20-solkael-polish-device-slice`. Do not merge the artistic PR.
Stop after the Pass 1 pack and wait for OWNER REVIEW before Pass 2.
