# Android QA export and physical-device gate

Existing Java17.0.15 Temurin was reused. Official required packages now live at
`C:/Users/olive/AppData/Local/Android/Sdk`: Platform-Tools37.0.1, Build-Tools35.0.1,
Platform35 revision2, cmdline-tools22.0/latest, CMake3.10.2.4988404 and
NDK28.1.13356709/r28b. Official4.7.2.stable templates are under
`C:/Users/olive/AppData/Roaming/Godot/export_templates/4.7.2.stable`.
Archive hashes/source URLs and prior inventory are in V1_20_ENVIRONMENT.md.
No Android Studio, replacement Java, SDK36 or additional global dependency installed.

```powershell
& .work/venvs/canonical-ci/Scripts/python.exe tools/android/export_debug.py --godot .work/tools/godot-4.7.2/Godot_v4.7.2-stable_win64_console.exe
```

This creates `.work/builds/hero-smash-v120-debug.apk`, ARM64, package
`org.herosmash.qa`, versionCode120/versionName0.1.20-qa. A disposable staging copy
sets the QA main scene/icon and Android texture import, leaving `game/project.godot`
and its production bootstrap unchanged. Editor configuration is isolated, SDK/JDK
paths are detected, and an ignored debug-only keystore is generated if absent.
The tracked export preset selects the slice and necessary data. APK ZIP structure,
apksigner verification and actual apkanalyzer XML are required to pass.

The exact official template targets/compiles API36 with minAPI24. Non-Gradle export
cannot override these; the preset deliberately inherits the official values. The
requested Platform35 is installed but no Java source compilation is performed.
Build-Tools35 signs this template successfully. `aapt35 dump badging` could not parse
one API36 attribute, so the authorized latest apkanalyzer validates XML instead.
This compatibility discrepancy is recorded in the active plan. No store/AAB or
release-signing readiness is claimed.

## Physical phone

Current adb discovery: no connected authorized physical device. **BLOCKED**.
No phone model/SoC/GPU/RAM/thermal/FPS/load/crash result exists to report.

1. Connect an Android phone with a USB data cable, unlock it, enable Developer
   options and USB debugging, then accept this computer's RSA prompt on the phone.
2. Run `& "$env:LOCALAPPDATA/Android/Sdk/platform-tools/adb.exe" devices -l`;
   it must list the phone as `device`, not `unauthorized` or `offline`.
3. Run `python tools/android/device_probe.py --deploy --seconds 120` using the
   existing project Python. It rejects emulators, collects properties/display/RAM,
   installs the debug APK and launches the two-fighter slice, sampling thermal and
   memory state and saving logcat. Review `SLICE_SAMPLE` timing lines and crash logs.
4. Record at least120s after load, distinguish warm-up/sustained data and note
   unavailable vendor GPU counters. One phone does not define the minimum matrix.

Physical deployment/profile code cannot be exercised until a real phone is connected.
Desktop measurements are explicitly separate. No quality tiers are introduced
without physical evidence that they are needed.
