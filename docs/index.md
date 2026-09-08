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
- `references/visual/reference_manifest.json` — indexed, reference-only visual origins.

Canonical-data entry points:
- `product-specs/CANONICAL_DATA.md` — portable schema fields and data ownership.
- `architecture/ADR-0003-canonical-data-and-effect-contracts.md` — effect boundaries and unresolved rules.
- `migration/V1_16_DATA_COMPARISON.md` — generated full-deck preservation report.
- `migration/V1_16_PILOT_PARITY.md` — 15 original-text/JS/proposal comparisons.
- `qa/CANONICAL_DATA_VALIDATION.md` — Python/Godot tests and clean-checkout procedure.
