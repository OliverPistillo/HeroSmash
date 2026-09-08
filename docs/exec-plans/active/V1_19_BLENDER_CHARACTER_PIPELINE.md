# v1.19 — Blender Character Pipeline / First Production Fighter

Status: IN PROGRESS — owner authorized execution and Solkael Art Lock on 2026-09-09.
Branch: `revival/v1.19-golden-fighter-pipeline`; baseline `d5ece76`.
Preserve the completed v1.18 contracts and the v1.17 combat baseline.
The eight exact approved production references are admitted by
`docs/art/SOLKAEL_ART_LOCK.md` and central manifest `production_items`.
The owner approval supersedes the former unknown-rights entry status for these
new files only. Historical v1.18 references remain uncleared. Front also provides
neutral/silhouette review; eight files are not falsely reported as ten images.

Initial Git audit: HEAD/tag exact; no tracked changes, only the owner-supplied
Art Lock packet untracked. Record and commit that packet before modeling to obtain
a clean starting tree. Fetch and requested branch/tag pushes succeeded; Draft PR
#1 already exists toward main, without auto-merge. No force-push or main mutation.

Binary governance uses existing Git LFS 3.7.1 with repository-local setup, dedicated
new asset patterns and hydrated CI checkout. Source/exports/runtime follow the
machine-readable convention paths (the architecture tree is conceptual).

## Candidate and scope

First fighter: **Solkael Lionheart**, base form, medium_biped, tower gauntlets.
Rationale: the clearest named identity/weapon reference, readable defensive shape,
shared biped topology and no special flight/serpentine locomotion. This choice is a
production-pipeline proposal; it does not clear the legacy concept's rights.

## Ordered work

1. Read current state/master/bible and detect the existing toolchain. Do not upgrade
   Godot 4.7.2 or Blender 5.2 LTS or install Android/MCP/global dependencies silently.
2. Resolve authorship/rights and intended use, or establish independently authored
   original design. Complete a consistent ten-view packet and review the proposed
   proportions, skull height, gauntlet attachment, dominant hand, mane/tail envelope
   and face. Record concrete approval/evidence. **No final modeling before this.**
3. Create a disposable geometric convention fixture and a repeatable Blender export
   script. Validate units, one-time axis conversion, root/floor, rest pose, names,
   material/texture references and GLB output. Rebuild from a clean checkout.
4. Build one original approved base-form fighter, source `.blend` separated from
   exports. Implement the medium shared semantic hierarchy with documented rest
   matrices and Solkael extensions. Establish face controls for the ten expressions.
5. Author the ten minimum clips at 30 fps, correct loops, no root motion, and the
   seven semantic marker names as applicable. Integrate a typed Godot wrapper that
   consumes resolver event IDs/timestamps and never computes or applies damage.
6. Produce landscape footage and profile the representative fighter in the existing
   sample context. Record actual triangle/material/bone/texture/draw/CPU/GPU costs;
   label measurements by hardware. Do not lock final phone budgets from desktop
   data or assume one fighter predicts a two-fighter arena.

## Deliverables and exit gates

- Approved consistent reference packet and rights admission record.
- Reproducible Blender fixture/export/validation tooling, one source fighter and
  its validated GLB; no accidental `.blend` runtime dependency.
- Rig/face/clip manifest and rest/socket/texture/material validation reports.
- Godot import, wrapper boot, scale/origin screenshots, clip coverage and KO/seek/
  interrupted-event synchronization evidence. No duplicate VFX/damage events.
- Clean-checkout reconstruction plus all applicable v1.15–v1.18 gates, unchanged
  canonical data and full combat hashes. Document any newly justified exception.
- Actual-resolution visual review and measured performance report; physical mobile
  test if an authorized device/toolchain exists, otherwise explicitly pending.
- State update only on actual completion, with exact commits, failures and debt.

Out of scope: the other 15 final launch fighters, all reserve production, evolution
forms, final arenas, 150 card illustrations, combat balancing, economy changes,
multiplayer and automatic SDK/signing installation. Android/iOS export and device
coverage remain separate explicit work if tools are unavailable.
