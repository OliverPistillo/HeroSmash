# v1.18 — Final hero roster and visual reference lock

Status: executing on `revival/v1.18-hero-reference-lock`, baseline `337710e`.
The current owner task explicitly authorizes deciding 16 launch + 4 reserve and
the production specification. It supersedes the earlier separate roster-selection
approval step below. This does not establish rights clearance or approval of
source-unsupported visual attributes: those remain marked proposal/unresolved.
No final art production is authorized by this plan.
Start from completed v1.17 and its exact validated/evidence/state commits. Preserve
the combat baseline and all v1.15/v1.16/v1.17 gates; no balance tuning in this phase.

## Deliverables

1. Inventory the20 anthropomorphic candidates already indexed in the read-only
   archive/reference manifest. Produce a provenance/rights/status table per stable
   candidate ID,linking every actual source; do not invent missing concepts.
2. Compare the16 current oracle hero IDs with20 candidates in an explicit migration
   matrix:retain,rename candidate,replace candidate,unmapped. Do not auto-transfer
   stats/skills or delete IDs based on visual resemblance.
3. Write a concrete roster proposal:identity,species,silhouette,role,favored branches,
   visual references and open conflicts. Product approval is needed for the final
   roster/branch changes; prepare the complete reviewable matrix before requesting it.
4. Lock approved reference provenance and rights classifications. Third-party
   proprietary art remains reference-only; no copying production meshes/UI/art.
5. Document shared skeleton/scale/origin/axes,naming,animation interface and glTF
   validation conventions for the subsequent Blender/Godot pipeline. Existing sample
   GLB may validate tooling; no final hero/arena assets yet.
6. Record stable-ID compatibility requirements for future data migration and replay
   versions. The current582 levels and150-card registry stay unchanged. Any roster
   data implementation requires an approved source spec and a comparison validator.

## Gates and boundaries

- Every candidate has indexed provenance and explicit rights/approval status.
- The16→20 matrix has no silent omissions or assumed stat mappings.
- Human roster/reference decisions are recorded in authoritative specs before data
  replacement; unresolved decisions remain visible.
- Canonical data,legacy/archive and deterministic combat hashes remain preserved;
  run applicable full prior gates on any data/tooling change.
- Detect existing Godot4.7.2,Blender5.2LTS and toolchain before changes. No automatic
  SDK/MCP/global dependency installation,multiplayer,final art or balance tuning.
- Update PROJECT_STATE only on actual macro completion,with exact commits and tests.

Acceptance:an approved final roster/reference contract and a source-backed migration
plan that v1.19 can execute without guessing identity,rights or shared rig conventions.
