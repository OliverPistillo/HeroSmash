# v1.19 validation

Run from a clean `revival/v1.19-golden-fighter-pipeline` checkout with hydrated Git
LFS objects. Reuse detected Godot 4.7.2 and Blender 5.2 LTS; no automatic installation.

```powershell
python tools/validation/fighter.py --godot .work/tools/godot-4.7.2/Godot_v4.7.2-stable_win64_console.exe --blender 'C:/Program Files (x86)/Steam/steamapps/common/Blender/blender.exe' --require-clean
```

Ten full asset checks cover protected data, approved image bytes and explicit rights,
LFS hydration, GLB skin/material/morph/clip structure, runtime/source contracts,
17 binary regression tests (one positive control), isolated reconstruction, export
of the committed editable source, import and typed wrapper/event tests, clean tree.
The portable CI variant omits only the Blender reconstruction check and labels it.

The real Godot suite includes chronological cues, duplicates, conflicting IDs,
late delivery, contact timing, interruption/KO, revival, seeking before/after KO,
reflection, dodge, shield, missing clips, imported bones/sockets/loops/expressions,
and real streams from all twelve unchanged resolver scenarios. Source/target IDs
remain resolver IDs; the visual Solkael does not replace an oracle hero definition.
Critical basic hits can select the heavy clip without adding another contact cue.
Seek and KO emit cosmetic cancellation to attached presentation consumers.

The independent binary validator rejects nonfinite/OOB/sparse data, nonneutral or
excessively displaced morphs, wrong naming/scale/floor, invalid weights/joints,
missing clips/expressions, nonopaque materials and external texture dependencies.
UV/tangent import errors are failures even if Godot returns exit code zero.

For actual Mobile-renderer review:

```powershell
$env:HERO_FIGHTER_CAPTURE = 'D:/Dev/HeroSmash/.work/reports/fighter/idle-844x390.png'
$env:HERO_FIGHTER_CLIP = 'idle'
$env:HERO_FIGHTER_POSE = '0'
& '.work/tools/godot-4.7.2/Godot_v4.7.2-stable_win64_console.exe' --path game --rendering-method mobile --resolution 844x390 --script res://tests/fighter_review.gd
```

The QA viewer uses actual pixel UI sizing, an explicit stage/camera and a manually
clocked AnimationPlayer. `HERO_FIGHTER_EXPRESSION` selects any shared expression,
`HERO_FIGHTER_YAW` rotates the model. `HERO_FIGHTER_VIDEO=1` plus Godot's
`--write-movie <output.avi> --fixed-fps 30` records all ten clips for 900 frames.
Add `HERO_FIGHTER_REPLAY=1` for a recorded unchanged Toxin scenario rather than the
clip catalog; no simulation parameters or damage timing are altered.
The viewer binds the actual resolver entity ID and requires nonzero cosmetic cues.
`HERO_FIGHTER_SCENARIO=04_shield_healing` selects the unchanged barrier fixture.

`tools/asset_pipeline/capture_fighter.py --godot <existing-executable> --output <directory>`
captures the complete evidence set. `--movies-only` repeats only the three movies.
Movies use 1366×768 for both project viewport and window, avoiding a MovieWriter
crop found when the window alone was changed to 844×390. One initial engine frame
precedes the 900/360 scripted frames. Run `inspect_fighter_movie.py <directory>`:
it checks all chunk boundaries/frame counts and fixes only the observed 70-byte
outer RIFF-length discrepancy, preserving JPEG/audio bytes. Validated movies and
original SHA-256 values are recorded separately; no ffmpeg installation is required.

Capture/import visual evidence at 1366×768 and 844×390, including front/side/back,
barrier contact, attack, KO and expressions. Review raw screenshots and actual
footage. Viewport CPU/GPU timing and engine counters are labeled desktop QA-stage
measurements; movie mode is not used for performance conclusions. Scene render
memory includes the viewport/stage/shadows, not only the texture-free fighter.

Previous full profiles remain required: canonical, full repeated combat with the
v1.17 summary comparison, foundation including full archive and GPU screenshots,
and roster with full archive and its historical phone proof. The v1.18 baseline
gate permits only new enumerated Solkael presentation files; it continues to reject
any change to an existing v1.17 runtime/legacy blob. New production image scope is
validated separately by exact packet hash, not excluded by a blanket path rule.

Physical Android/iOS, signing and final shipping-art polish remain explicit debt
when no device/toolchain or final art review exists. Passing the pipeline does not
clear other heroes or change any balance signal.
