# Executed v1.18 evidence

Full final profiles ran at `50fdb5820a4b5241885378dcb5215d68bf31920b` from
`D:/Dev/HeroSmash/.work/clean-v118-validation`, on the exact requested branch.
The clone was created fresh at `22db872`, then fast-forwarded to the small final
text/rig-summary correction and the complete profiles rerun. Tracked state was
clean before and after. No source workspace cache was copied and no tool installed.

| Profile | Result | Evidence |
| --- | --- | --- |
| v1.18 roster/reference | 12/12; 17 adversarial tests | `roster-gates.json` |
| v1.16 canonical | 11/11 | `canonical-gates.json` |
| v1.17 combat | 15/15; 12,000 fights repeated | `combat-gates.json`, `lab-summary.json` |
| v1.15 full local foundation | 18/18 | `foundation-gates.json` |
| Phone planning proof | 4 diagrams, no text overlap, safe-area bounds | `card-proof.json`, four PNGs |

The final lab reproduced all v1.17 deterministic metric/event/result comparisons:
12,000 unique + 12,000 repeated fights, 1,000 mirror comparisons, 12 replay file
roundtrips and zero replay-hash failures. Runtime duration measurements may vary;
they are excluded from deterministic comparisons. Raw repeated records remain in
the ignored clean-clone lab output; v1.17's curated full corpus remains available
and is not duplicated here. Canonical dataHash remains
`932aaad64f3c805dbb60439d36213e253d2a7eb3d25e0e66d42bfc7c2c5359bf`.

Both actual Godot Mobile sample screenshots were inspected. They show the unchanged
foundation cube/plane, not a final fighter. The four phone diagrams were inspected
at their actual pixel dimensions. Re-rendering with the same recorded local font
from the clean checkout reproduced all five diagram/report artifacts byte-for-byte.
The card diagrams contain synthetic placeholders and no copied reference pixels.
Body/effect text is 14 px; secondary labels are 12 px; the primary action is 44 px
high. This is conceptual hierarchy evidence, not physical phone usability approval.

The archive audit hashes all 562 image origins; full foundation hashes all 1,152
archive files and preserves 393 web blobs. The source snapshot matches the exact
original local `hero.json.txt` bytes. The external OneDrive original was not accessed.
No legacy image or code was edited, moved or deleted. Newly captured screenshots
are QA evidence and are explicitly excluded from design-reference selection.

Final failure count is zero. During authoring, the phone renderer rejected a font
with a negative left bearing at a text boundary; positioning was corrected. Review
also corrected a synthetic MAX label to its maximum display level, aligned card
body size to brand tokens and added Fenrox to the readable rig summary. The final
17-test suite includes the minimum-body-size regression. The historical two legacy
readability identifiers remain the accepted, actively checked negative baseline.

CI YAML was parsed and the portable roster step is wired after the prior gates.
GitHub Actions/Linux execution was not run here. Android SDK/ADB/sdkmanager and
usable export templates are not detected; `ANDROID_HOME` is set but its directory
is absent and the export-template root is empty. Apple signing/toolchain and mobile
device/performance checks are unavailable. No final model, rig, animation, arena,
runtime UI or production-rights approval is claimed. Those asset-entry checks are
future v1.19 work, not skipped required specification gates.

`manifest.json` hashes the curated JSON/PNG bytes after LF normalization; it does
not hash itself or this explanatory Markdown. Exact commands and captured test
output are in the gate reports and `../../ROSTER_REFERENCE_VALIDATION.md`.
