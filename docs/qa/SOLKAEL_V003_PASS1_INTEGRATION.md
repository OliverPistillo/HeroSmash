# Solkael v003 Pass 1 — integration checkpoint

2026-09-09. **BASELINE INTEGRATED; INTERACTIVE PASS 1 NOT STARTED.**
This report records Git recovery and technical baseline validation. It is not the
completed Pass 1 review pack. Artistic status remains **OWNER REVIEW REQUIRED**.

## Git integration

After `git fetch origin --tags --prune`, PR #3 was OPEN/Draft, MERGEABLE/CLEAN,
with exact head `51c4e148e3c736f7c11a5e8a7be1324d27fcac10` and two successful
portable-gates checks. The owner explicitly authorized Ready and merge into
`revival/v1.20-solkael-polish-device-slice`.

PR #3 was made Ready and merged at 2026-09-09T15:07:50Z with the expected-head
guard. Updated remote base/merge commit:
`904ca9fcd52fdb4ab7e7460e0bf20c38022b3ba8`.
Technical branch retained at `51c4e148e3c736f7c11a5e8a7be1324d27fcac10`.
`main` remains `66a5ba67f0691b7d50a11fa873f4ed24c80a14ef`.
The annotated historical v1.20 tag still peels to
`de770dff30dcc533d547074c975fdaa0962abda9`; tag object:
`ebed04d029dda56054f405f1482fe6b4a6a8bfc6`.

Created/published `art/solkael-v003-owner-polish` with its own origin upstream
from that updated base. Isolated worktree:
`D:/Dev/HeroSmash/.work/worktrees/solkael-v003-owner-polish`.
The original checkout has two local commits and uncommitted work; it was not
pulled across divergent history. Fetch plus the new clean checkout provides
updated remote v1.20 without altering the original local branch.

## Controlled recovery of 72170ba

Inspected `git show --stat`, `--name-status`, `--format=fuller`, shared-tool diffs
and merge base. Original commit `72170ba0295aa992ca1ac7a7954cdb41da5222d3`
has parent/merge base `de770dff30dcc533d547074c975fdaa0962abda9`.

It contains 32 files: versioned v003 source/manifest/textures/runtime export,
generated-image provenance, v003 plan, QA wrappers/selection, reconstruction,
export/capture/packaging and validation support. No gameplay/balance edits or
file-path overlap with the MCP PR. The historical asset includes body, armor,
material and animation changes; recovery preserves them as the model baseline.
No new head or body polish was performed in this task yet.

Selective recovery:

- `d24c314`: 18 asset/provenance/LFS files from 72170ba.
- `ae4add78c7025dfa24e56c6b36d1caa8f4eb7702`: 13 plan/export/QA support files.
- Excluded `tools/android/export_debug.py`: old optional v003 Android packaging
  support is outside this pass's needs. The baseline file remains unchanged.

All 31 paths matched the source commit in Git after recovery. All 16 recovered
asset/sidecar files also matched original working-file SHA-256. The new worktree
was clean at `ae4add7` before and after baseline validation. Original commit,
history, dirty plan and untracked review evidence survive.

## Technical baseline validation

Tested commit `ae4add78c7025dfa24e56c6b36d1caa8f4eb7702`, clean checkout.
Existing Blender 5.2.1 LTS, Godot 4.7.2 and Python venv were reused.
No installation, server or permission configuration was changed.

Command, using the existing installed executables:

```text
python -X utf8 tools/validation/solkael_v003.py --blender <existing Blender 5.2.1> --godot <existing Godot 4.7.2 console> --rebuild --report .work/reports/v003/pass1-baseline-validation.json
git lfs fsck
```

All nine gates pass: v002/gameplay/Art Lock preservation; rig/bind/clip/name
contracts; negative UV controls; independent GLB/UV/material/morph gate;
saved-source export; isolated reconstruction; Godot import; v002 runtime suite;
v003 runtime suite. Each runtime suite reports 240 assertions. LFS fsck passes.
Saved-source and isolated exports equal the recovered GLB byte-for-byte.

| Metric | Preserved v002 | Recovered v003 | Historical delta |
| --- | ---: | ---: | ---: |
| Triangles | 27,488 | 34,584 | +7,096 |
| Exported vertices | 25,414 | 38,470 | +13,056 |
| Bones | 71 | 71 | 0 |
| Morph targets, excluding neutral | 9 | 9 | 0 |
| Materials / surfaces | 1 / 1 | 1 / 1 | 0 |
| Textures, 2048 square | 4 | 4 | 0 |

These are historical deltas, not Pass 1 results. No new mesh edits occurred.
v003 GLB SHA-256:
`d4abdf5aa8cdcd632c57173ed5b5bd879da78273c48081973f2d9ead52aaa368`.
v002 GLB SHA-256:
`558a6566b8fa8a473f7f0b5460b68f73a365558b451a81a7208dc1fe82dc4108`.
The gate verified 30 original v002 evidence images and all eight Art Lock images.
Additional local audit records 88 protected file hashes and recovered assets.
Final comparison also passes all45 original Solkael and127 original evidence
hashes; original HEAD/status remain unchanged. The roster/reference portable gate
passes all12 checks, including generated-document reproducibility. No reference
inventory regeneration or image reclassification was necessary.

Reports: [baseline validation](evidence/v1.20/v003/pass1-integration/baseline-validation.json)
and [integration provenance](evidence/v1.20/v003/pass1-integration/integration-provenance.json).
The [roster report](evidence/v1.20/v003/pass1-integration/roster-validation.json)
records the final documentation edits as an expected dirty tree during that check.

## Current prerequisite and next step

New actual turn `01a086af-9512-7313-9a06-f6e42766ed2c` records
`approval_policy=on-request`, `approvals_reviewer=auto_review`, model `gpt-6-astra`,
effort `xhigh`. This differs from the prior smoke's validated human reviewer and
the new request for Ultra. No evidence establishes that a managed requirement
prevents changing reviewer; no managed-policy bypass was attempted.

Zero Blender MCP calls in this turn. Dedicated GUI unused for artistic edits.
Automatic sandbox reviews for Git/CLI validation do not count as human MCP approval.
Headless validation opens background copies for export/reconstruction; recovered
source and existing GUI are intact.

The owner was asked to restore human approval and informed of the effort mismatch.
Before continuing, recheck effective settings and require real human code approval.
The scoped [execution plan](../exec-plans/active/SOLKAEL_V003_TARGETED_POLISH.md)
then starts with MCP scene/object inspection and an initial viewport screenshot.

All eight Art Lock images were visually inspected. Existing v002/v003 renders
were inspected only as historical model evidence. Recovered v003 still has an
overly domed forehead, round muzzle/chin separation, exposed neutral teeth and
repetitive mane locks compared with Art Lock's integrated facial planes and flowing
crown. These are targets to evaluate interactively, not claimed fixes.
34,584 triangles and 20.31% UV occupancy remain existing review debt.

No Pass 1 renders, completed review report or owner-review ZIP exist yet.
No new Android export, physical-device profile or separate 12,000-fight local run.
No artistic merge, tag movement or owner art approval occurred.
