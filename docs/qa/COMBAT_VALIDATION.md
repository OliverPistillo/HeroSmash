# v1.17 combat and balance lab

Use existing Godot4.7.2,Python3.12 with `tools/requirements-canonical.txt`,Node20.19.6.
No command installs tools. Example from the production root:

```powershell
$combatGodot = 'D:/Dev/HeroSmash/.work/tools/godot-4.7.2/Godot_v4.7.2-stable_win64_console.exe'
$combatPython = 'D:/Dev/HeroSmash/.work/venvs/canonical-ci/Scripts/python.exe'
& $combatPython -X utf8 tools/validation/combat.py --godot $combatGodot --require-clean
```

The gate verifies baseline tag/ancestor,engine,exact generation,schema,582 levels,
JS divergences,mathematical/headless tests,replay tampering,12×1000 fights twice,
1000 mirrored comparisons,12 replay file roundtrips and replay schemas. Godot error
text fails even when exit code is0. `--smoke-only` uses10 seeds/scenario and cannot
close the macro phase. Prior full canonical/foundation profiles remain required:

```powershell
& $combatPython -X utf8 tools/validation/canonical.py --godot $combatGodot --require-clean
& $combatPython -X utf8 tools/validation/foundation.py --archive .work/legacy-source --godot $combatGodot --blender 'C:/Program Files (x86)/Steam/steamapps/common/Blender/blender.exe' --pillow-python 'C:/Users/olive/AppData/Local/Programs/Python/Python312/python.exe' --visual
```

## Execute, save and verify

```powershell
& $combatGodot --headless --path game --script res://tests/combat_cli.gd -- list
& $combatGodot --headless --path game --script res://tests/combat_cli.gd -- run 10_reflection_lethal 5 D:/Dev/HeroSmash/.work/reports/replay.json
& $combatGodot --headless --path game --script res://tests/combat_cli.gd -- verify D:/Dev/HeroSmash/.work/reports/replay.json
& $combatGodot --headless --path game --script res://tests/combat_cli.gd -- input D:/Dev/HeroSmash/.work/reports/custom-input.json D:/Dev/HeroSmash/.work/reports/custom-replay.json
& $combatGodot --headless --path game --script res://tests/combat_cli.gd -- profile 04_shield_healing 0
```

Single-fight output directories must exist. `run` accepts an optional final horizon
in milliseconds. `batch SCENARIO FIRST COUNT OUTPUT [HORIZON]` saves metrics without
retaining every event. Custom loadouts use `product-specs/REPLAY_FORMAT.md`.
`batch-seeds SCENARIO 0,5,42 OUTPUT [HORIZON]` accepts an explicit ordered list of
unique unsigned32-bit seeds; its output records that list. The gate checks0,5 and
4294967295 at a1000ms horizon in addition to the full fixed corpus.

```powershell
& $combatPython -X utf8 tools/balance_lab/run.py --godot $combatGodot --output .work/reports/combat-lab --workers 4 --count 1000 --first-seed 0 --horizon-ms 45000
```

Python only orchestrates/aggregates. Four independent Godot processes run scenarios
after one import. Two passes compare every seed; each scenario's first seed is also
saved/reloaded/regenerated. `summary.json` includes outcomes,durations,damage,healing,
shield,crit/dodge denominators,skills,status/uptime,prevention/rebirth/KO,lethal source,
HP,events,runtime. `pass1/` and `pass2/` hold full per-fight records. Only runtime is
excluded from deterministic metrics hashes.

Clone the same branch under ignored `.work/`, preserving tags, and run all full
gates there using absolute existing-tool/archive paths. `combat.py --compare
ABSOLUTE_PREVIOUS_SUMMARY` compares the entire deterministic metrics corpus. CI uses
a clean checkout/full history and runs the full repeated lab; local passes do not
prove remote CI execution or cross-platform hash equivalence.

No combat presentation changed. Foundation still tests its existing GLB/Blender/
screenshots. Android/iOS device performance/export/signing and final-art gates remain
non-applicable or unavailable and must not be inferred from desktop runtime.
