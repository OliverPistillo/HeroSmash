# v1.20 — Solkael Polish & Device Slice

Status: IN PROGRESS. Owner authorized this phase on 2026-09-09.
Baseline: f03a1b3833055b2538f1780bcc4a649830981195, completed v1.19.
Branch: revival/v1.20-solkael-polish-device-slice. Draft PR #2 toward main.
Bootstrap: fetched origin/tags, empty working tree, exact local/remote baseline;
annotated v1.19-golden-fighter-pipeline tag created/pushed/peeled to f03a1b3.
New branch published immediately with upstream; main and PR #1 untouched.

## Authority and explicit changes in scope

Read AGENTS, state, master, architecture, v1.19 report/evidence, production bible,
approved Art Lock, v1.17 combat/replay/status/damage/lethal contracts and quality gates.
Only the eight approved Solkael Art Lock v1 files may directly guide production.
No old unknown-rights source promotion, new hero, design/balance/card changes.
Existing v1.19 source/GLB remain a reproducible baseline; refinements are versioned.
The owner now explicitly authorizes required official Android command-line tools,
their required licenses and exact Godot 4.7.2 Android export templates after detection.
This supersedes v1.19's no-install scope. It does not authorize release credentials,
iOS builds, store release, other heroes, final arena art or multiplayer.

## Ordered blocks and acceptance

1. Toolchain inventory / CI maintenance: detect paths and versions before install;
   official compatible Actions runtime upgrade in a separate commit. Keep legacy
   Node/Python workload versions stable. Verify actual remote CI.
2. Art: refine the same Solkael, continuous anatomy, muzzle/mouth cavity/teeth/tongue,
   eyelids/eyes, sun-crown mane, armor fit, integrated tower gauntlets, claws/paws,
   tail and silhouette. Compare with front/3quarter/side/back/gauntlets/materials/
   combat/expressions. No final-art auto-approval.
3. Mane/fur: choose and measure mobile-suitable stylized geometry/cards/hybrid;
   document triangles, transparency/overdraw, material count and visual limitations.
4. UV/PBR: coherent paint-ready UVs without accidental overlap, texel strategy,
   stable material names, Base Color/Normal/ORM and intentional emissive, measured
   dimensions/bytes/memory. Reference pixels never become runtime textures.
5. Face/animation: all ten expressions and ten contractual clips, weight/anticipation/
   recovery/guard/contacts/inertia/KO settling. No root motion. Validate deformation,
   eyes/eyelids/lips/jaw/teeth/ears/mane interactions; render an expression grid.
6. Contacts: floor, gauntlets, target points, head/chest/hurtbox anchors and VFX/barrier
   sockets. Visual contact follows resolver timestamps, never changes combat outcomes.
7. Two-fighter scene: reuse one GLB/wrapper twice in a separate neutral 2.5D QA arena,
   controlled Camera3D, fighting axis, depth layers, shadows, VFX root, minimal safe HUD.
   Both entities share architecture. Real streams cover attacks/skill/dodge/hit/shield/
   periodic/reflection/KO/victory, seek/cancel and x1/x2/x3. No player/enemy rule fork.
8. Landscape review: 1366x768, 844x390 and a useful Android aspect; feet, mane,
   towers/barrier/effects visible, safe HUD, no critical cropping/foreground occlusion.
9. Android: official Platform-Tools >=35, Build-Tools35.0.1, Platform35, cmdline-tools
   latest, CMake3.10.2.4988404, NDK28.1.13356709; prefer existing valid JDK17. Install
   only absent/invalid required packages. Match official templates exactly4.7.2.
   CLI debug APK, reproducible preset and command; no release/store keys or AAB claim.
10. Device: adb discovery; if authorized hardware exists, identify/model/OS/SoC/GPU/
    display/refresh/RAM, install/launch slice, collect sustained timing/memory/thermal/
    load/crash data and available counters. If absent: BLOCKED device gate, exact
    connection instructions; no desktop/emulator substitution or fabricated metrics.
11. Budgets: separate MEASURED from PROPOSED, two-fighter triangles/materials/textures/
    bones/morphs/VFX/shadows and arena headroom. Quality modes only if physical evidence
    justifies them, not three premature artistic pipelines.
12. Closure: full applicable v1.15–v1.19 gates, v1.20 asset/UV/material/rig/face/animation/
    reconstruction and two-fighter/speed/seek checks, unchanged combat hashes, landscape
    evidence, SDK/templates/APK validation and GitHub Actions. Update state only after
    technical completion, archive this plan, commit/push, verify clean tree/CI, annotate
    and publish v1.20-solkael-polish-device-slice on the final commit. No v1.21 branch.

## Separate result states

- PIPELINE VALIDATED: pending local and clean-checkout technical gates.
- ART REVIEW STATUS: requires owner review; never inferred from validator passes.
- ANDROID EXPORT VALIDATED: pending SDK/template/preset/APK work.
- PHYSICAL DEVICE VALIDATED / BLOCKED: pending adb discovery.
- TWO-FIGHTER BUDGET STATUS: pending measurement; final phone matrix not inferred.

Each stable validated block is committed/pushed and Draft PR #2 updated. Final
report includes exact commits/SHA/tag, before/after metrics, art comparison classified
matched/acceptable deviation/unresolved/requires owner review, captures, Android/APK/
device metadata, CI maintenance, failed/skipped gates, debt and v1.21 recommendation.
