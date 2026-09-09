# v1.19 executed evidence

Full five-profile gate run: clean GitHub clone at
`fd0163b00f2c468de144450acd84e5907529e0d3`, 2026-09-09, Windows 11.
`fighter-full-fd0163b.json`, `roster-full.json`, `canonical-full.json`,
`combat-full.json`, `foundation-full.json`: 66/66 checks passed.
Full fighter reconstruction/import/tests passed again at `83e670a` after the
viewer identity and Windows UTF-8 fixes. Final screenshots/movies are recaptured
at `e5b9b2e` after reserving a caption strip below the fighter poses. No asset,
resolver or data changes occurred between these evidence commits.

The checkout was cloned from GitHub, with all ten production LFS objects hydrated;
it did not reuse a local asset cache. The ignored legacy copy and previously
installed executables were supplied by absolute paths. Full combat compared all
12 scenario metric hashes with the committed v1.17 summary: 12,000 unique fights,
12,000 repeats, 1,000 mirrors, 12 replay roundtrips, zero regressions. Full archive
checks read 1,152 files/562 image origins without modifying them. Historical
roster JSON limitations describe its v1.18 scope, not the new production approval;
the current validator now labels that historical scope explicitly.

## Reproduction commands

Run from the clean checkout with the already detected environment:

```powershell
$py = 'D:/Dev/HeroSmash/.work/venvs/canonical-ci/Scripts/python.exe'
$g = 'D:/Dev/HeroSmash/.work/tools/godot-4.7.2/Godot_v4.7.2-stable_win64_console.exe'
$b = 'C:/Program Files (x86)/Steam/steamapps/common/Blender/blender.exe'
$pill = 'C:/Users/olive/AppData/Local/Programs/Python/Python312/python.exe'
$archive = 'D:/Dev/HeroSmash/.work/legacy-source'
& $py -X utf8 tools/validation/fighter.py --godot $g --blender $b --require-clean
& $py -X utf8 tools/validation/roster.py --archive $archive --proof docs/qa/evidence/v1.18 --require-clean
& $py -X utf8 tools/validation/canonical.py --godot $g --require-clean
& $py -X utf8 tools/validation/combat.py --godot $g --require-clean --compare docs/qa/evidence/v1.17/lab-summary.json
& $py -X utf8 tools/validation/foundation.py --archive $archive --godot $g --blender $b --pillow-python $pill --visual
& $py -X utf8 tools/asset_pipeline/capture_fighter.py --godot $g --output .work/reports/fighter-release-review
& $py -X utf8 tools/asset_pipeline/inspect_fighter_movie.py .work/reports/fighter-release-review
git lfs fsck
git status --porcelain
```

The final fighter gate was also run without `-X utf8` to verify explicit metadata
encoding independently of shell defaults. Full Blender rebuild compares exact
GLB/source-manifest bytes and independently exports the committed editable source.
It intentionally does not assert identical Blender container save metadata.

## Visual review and actual limits

PNG evidence includes actual 1366×768 and 844×390 animated-profile captures,
front/side/back, light/heavy contacts, bulwark, dodge, grounded KO, victory and all
ten expression portraits. Foundation sample images were also inspected. The
final QA caption strip avoids overlap with the raised victory gauntlet. The
viewer has no interactive controls, notch simulation or finished combat UI.

The three AVIs cover the ten clips and the unchanged Toxin/Shield-healing replays.
Both movie viewport and window are 1366×768. Actual frame counts are 901/361/361,
including one initial engine frame, about 30/12/12 seconds at 30 fps. Every JPEG
frame is decoded by the existing Pillow installation; visual inspection samples
clip contacts, transitions, facial stability, KO and barrier visibility. This is
frame-sampled review, not a claim that an automated image score establishes art
quality. `barrier-event-frame-92.jpg` is an unchanged JPEG extracted from the
Shield replay. The runtime emits 18 and 36 cosmetic cues with no adapter errors.

`movie-validation.json` records a Godot writer defect: outer RIFF length is 70
bytes short while all inner chunks/index finish at EOF. The validator repairs
only that four-byte length field. Original and normalized SHA-256 values are
retained, JPEG/audio bytes unchanged. Early cropped movies and the wrong-entity
idle replay are superseded and not included as passing evidence.

Render profiling uses animated idle, 1,740 measurements after 60 warm-up frames,
existing RX 7900 XT/i5-13600K and Vulkan Mobile. See still-capture-summary.json for
CPU/GPU medians/p95, counters and memory. It measures one fighter plus the QA stage,
not physical Android, two fighters or a complete arena. Movie timings are not
performance measurements. The zero texture asset count does not imply zero
viewport render-target/shadow texture memory.

The geometry remains an original parametric first pipeline fighter. Continuous
anatomy, more faithful mane/gloves/mouth, painted UVs/materials, expressive posing,
KO settling and final art acceptance remain debt. Facial controls are independent
and technically functional, but some expressions are subtle at full-body phone
scale. No final production-art fidelity approval is claimed by these tests.

## Failed attempts and unavailable checks

Development failures and fixes are detailed in ../../V1_19_FIGHTER_PIPELINE_REPORT.md:
sparse morph parsing, missing tangent UVs, neutral morph initialization, guard/KO
alignment, viewport/caption overlap, replay identity and cp1252 false mismatch.
The historical two JS readability failures remain the expected negative baseline.
No unresolved required local gate failure is hidden by a successful process code.

Physical Android/iOS packages, signing, device install and sustained phone profiling
are unavailable: Android SDK path absent, adb/sdkmanager unavailable, Godot export
templates empty, Apple toolchain/device absent. No dependencies were installed.
Remote portable CI passed at 83e670a (runs 34293500949 and 34293497891); it is not
equivalent to the full local archive/Blender/GPU/device gates.

manifest.json hashes all curated binary/JSON artifacts, excluding itself and this
Markdown. Post-evidence validation is recorded separately in PROJECT_STATE and
the task report so a hash manifest never attempts to hash itself.
