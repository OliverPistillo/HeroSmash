# Tooling

Target categories:
- `migration/`
- `validation/`
- `simulation/`
- `asset_pipeline/`

Prefer small deterministic CLI tools that Codex and CI can run without manual editor interaction.

Canonical data (v1.16): use `migration/canonical_data.py --check` for schema/source
checks and an exact generated diff. Omit `--check` to regenerate the five datasets
and two comparison reports from locked legacy inputs and guarded effect proposals.
`validation/canonical.py --godot <existing-executable>` runs all portable gates;
`--require-clean` records clean files before and after import/tests. Dependencies
are pinned in `requirements-canonical.txt` and belong in a local virtual environment.
See `docs/qa/CANONICAL_DATA_VALIDATION.md` for complete commands and scope.
