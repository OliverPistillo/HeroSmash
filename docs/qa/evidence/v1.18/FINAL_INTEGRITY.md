# Post-evidence integrity check

Executed from the clean same-branch validation clone at
`8ba23800db233878d16432a8509df328061e8f6f`, after the evidence/reference-index commit:

- `python -X utf8 tools/validation/roster.py --archive D:/Dev/HeroSmash/.work/legacy-source --proof docs/qa/evidence/v1.18 --require-clean --expected-branch revival/v1.18-hero-reference-lock --report .work/reports/roster-final-integrity.json`: 12/12 pass, including 17 adversarial tests.
- All 13 entries in `manifest.json`: file length and SHA-256 match, and checkout
  bytes equal `git show HEAD:<artifact>` bytes.
- `git status --porcelain`: empty before and after.
- Final code/contract implementation is still `50fdb58`; changes after it are
  documentation, QA evidence and explicit QA-image exclusions in the reference
  duplicate report. Full 56-check profiles at `50fdb58` remain the curated evidence.

The remaining closeout changes only state, phase-plan relocation and navigation/
completion records. No additional runtime or asset validation is implied by those
documentation edits. No final required gate is outstanding for v1.18.
