# Hero Smash Knowledge Base

This directory is the project system of record.

## Navigation

- `architecture/` — accepted technical decisions and ADRs.
- `product-specs/` — gameplay/product truths.
- `references/` — external and visual source registry.
- `migration/` — legacy inventory and migration reports.
- `codex/` — agent workflow, MCP and prompt conventions.
- `qa/` — quality gates and validation.
- `exec-plans/` — active/completed macro implementation plans.

Root documents:
- `PROJECT_MASTER.md` = product/architecture decisions.
- `PROJECT_STATE.md` = current reality.
- `AGENTS.md` = Codex navigation and guardrails.

Foundation entry points:
- `migration/MIGRATION_PROPOSAL.md` — exact approved-tree move contract and rollback.
- `migration/data_source_map.md` — canonical choices and unresolved source conflicts.
- `migration/js_to_godot_system_map.md` — preserved behavior and future parity work.
- `qa/FOUNDATION_VALIDATION.md` — local/CI commands, evidence strategy and applicability.
- `references/visual/reference_manifest.json` — frozen v1.15 reference-origin census.

Canonical-data entry points:
- `product-specs/CANONICAL_DATA.md` — portable schema fields and data ownership.
- `architecture/ADR-0003-canonical-data-and-effect-contracts.md` — effect boundaries and unresolved rules.
- `migration/V1_16_DATA_COMPARISON.md` — generated full-deck preservation report.
- `migration/V1_16_PILOT_PARITY.md` — 15 original-text/JS/proposal comparisons.
- `qa/CANONICAL_DATA_VALIDATION.md` — Python/Godot tests and clean-checkout procedure.
- `migration/V1_16_MIGRATION_REPORT.md` — completed phase, commits, differences and debt.
- `qa/evidence/v1.16/REVIEW.md` — executed results, failed attempts and limits.
- `exec-plans/completed/V1_17_COMBAT_BALANCE_LAB.md` — completed execution/closure checklist.

Combat entry points:
- `architecture/ADR-0004-headless-combat-and-replay.md` — deterministic execution boundaries.
- `product-specs/COMBAT_RULES.md` — integer clock,identity,operators and limits.
- `product-specs/DAMAGE_PIPELINE.md` — mitigation,reflection and attribution.
- `product-specs/STATUS_SEMANTICS.md` — stacking,refresh and periodic timing.
- `product-specs/LETHAL_RESOLUTION.md` — prevention,rebirth and finalKO.
- `product-specs/CARD_LEVEL_PROGRESSION.md` — exact582-level APIs and unresolved bindings.
- `product-specs/REPLAY_FORMAT.md` — input,event,replay and metric contracts.
- `qa/COMBAT_VALIDATION.md` — headless CLI,lab and clean-checkout commands.
- `migration/V1_17_LEGACY_DIVERGENCES.md` — executable JS observations and decisions.
- `migration/V1_17_UNRESOLVED_SEMANTICS.md` — explicit semantic and economy debt.
- `qa/V1_17_BALANCE_REPORT.md` — 12,000-fight results,performance,retention and tests.
- `qa/evidence/v1.17/REVIEW.md` — executed clean-checkout evidence and machine metrics.
- `exec-plans/active/V1_18_HERO_ROSTER_REFERENCE_LOCK.md` — current roster/reference phase.

Roster and visual-production entry points:
- `product-specs/roster/LAUNCH_ROSTER.md` — 16 launch / 4 reserve and all-candidate audit.
- `product-specs/roster/SCORING_MATRIX.md` — 15-criterion ordinal selection rationale.
- `product-specs/roster/BRANCH_COVERAGE.md` — all 12 branches and explicit Ice exception.
- `product-specs/roster/ORACLE_MIGRATION_MATRIX.md` — 320 cells, preserved oracle requirements and six combined-kit gaps.
- `product-specs/roster/heroes/` — 16 generated identity sheets.
- `references/visual/v1.18/README.md` — current inventory, duplicates, provenance and limited direction selections.
- `references/visual/v1.18/RIGHTS_REVIEW.md` — explicit rights classes and production admission rules.
- `art/CHARACTER_PRODUCTION_BIBLE.md` — shared reference, rig, Blender/GLB/Godot and animation contract.
- `art/EXPRESSION_LIBRARY.md` — ten shared expressions and morphology rules.
- `art/BRAND_UI_LANGUAGE.md`, `art/CARD_VISUAL_LANGUAGE.md` — tokens, hierarchy and state grammar.
- `art/UNRESOLVED_AND_REFERENCE_GAPS.md` — per-hero view gaps and unresolved decisions.
- `qa/ROSTER_REFERENCE_VALIDATION.md` — reproducible spec/rights/phone-proof checks and prior gates.
- `exec-plans/active/V1_19_BLENDER_CHARACTER_PIPELINE.md` — proposed next phase, not started.
