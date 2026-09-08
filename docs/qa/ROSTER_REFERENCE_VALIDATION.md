# Roster and reference validation v1.18

No engine/global dependencies are installed by these commands. Existing local
Godot 4.7.2, Blender 5.2.1 LTS, Python/Pillow and the canonical CI venv are reused.
`tools/validation/roster.py` uses only the Python standard library. The optional
phone diagram renderer uses already installed Pillow and an explicitly supplied
local font; neither font nor source imagery is embedded as production art.

## Rebuild authored specifications

```powershell
python -X utf8 tools/art/reference_lock.py
python -X utf8 tools/art/roster_lock.py
python -X utf8 tools/validation/roster.py --archive D:/Dev/HeroSmash/.work/legacy-source
```

The reference generator reads the historical manifest and authored review overlay,
consolidates canonical Git blob/archive hashes and inventories all tracked images.
QA screenshots are explicitly excluded as design sources. Full local validation
also hashes every archive image and compares the entire image-path set. Foundation
validation independently checks all 1,152 archive files, including non-images.
No reference image is written. Captured candidate JSON retains original bytes.

The roster generator writes matrices, 16 sheets, gaps/rights reports and readable
contract views from JSON. Validators compare a rebuild byte-for-byte (allowing
only Markdown checkout line endings) and reject hand-edited generated documents.

## Full closure from a clean local clone

Clone the requested branch with full local history into a new ignored `.work/`
directory. Use the already installed tools via absolute paths; do not copy Godot
caches. Run from that clone, on `revival/v1.18-hero-reference-lock`:

```powershell
& C:/Users/olive/AppData/Local/Programs/Python/Python312/python.exe -X utf8 tools/art/card_specimen.py --font C:/Windows/Fonts/arial.ttf --output .work/reports/card-proof
python -X utf8 tools/validation/roster.py --archive D:/Dev/HeroSmash/.work/legacy-source --proof .work/reports/card-proof --require-clean --expected-branch revival/v1.18-hero-reference-lock
& D:/Dev/HeroSmash/.work/venvs/canonical-ci/Scripts/python.exe -X utf8 tools/validation/canonical.py --godot D:/Dev/HeroSmash/.work/tools/godot-4.7.2/Godot_v4.7.2-stable_win64_console.exe --require-clean --expected-branch revival/v1.18-hero-reference-lock
& D:/Dev/HeroSmash/.work/venvs/canonical-ci/Scripts/python.exe -X utf8 tools/validation/combat.py --godot D:/Dev/HeroSmash/.work/tools/godot-4.7.2/Godot_v4.7.2-stable_win64_console.exe --require-clean --compare D:/Dev/HeroSmash/docs/qa/evidence/v1.17/lab-summary.json
python -X utf8 tools/validation/foundation.py --archive D:/Dev/HeroSmash/.work/legacy-source --godot D:/Dev/HeroSmash/.work/tools/godot-4.7.2/Godot_v4.7.2-stable_win64_console.exe --blender 'C:/Program Files (x86)/Steam/steamapps/common/Blender/blender.exe' --pillow-python C:/Users/olive/AppData/Local/Programs/Python/Python312/python.exe --visual
git status --porcelain
```

The phone proof renders Normal/Epic/Legendary, one/two branches and all state types
at 844×390 and 667×375 with explicit safe insets. It checks text ink bounds, overlap
and 44-high action targets. Inspect the diagrams; they are conceptual layout
evidence with synthetic values, not a new card dataset, final UI or device test.
Same-font clean-checkout re-rendering must reproduce their hashes. The font hash is
recorded, so other platforms do not silently claim identical font metrics.

## Applicability and retained debt

The complete old canonical/combat/foundation profiles remain mandatory, including
two repeated 12,000-fight batches and comparison with v1.17 result/event/metric
hashes. The two historical legacy readability failures remain an explicit accepted
negative baseline, never a new pass. Actual final-character rig/GLB/animation and
event-synchronized footage are inapplicable until v1.19 produces an admitted asset.
Remote CI, phone GPU/performance, Android export/SDK, Apple signing and font/art
rights clearance are not inferred from local specification or sample-GLB passes.
