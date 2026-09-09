# v1.20 environment intake — 2026-09-09

Before installation: Java Temurin17.0.15+6 at
`C:/Program Files/Eclipse Adoptium/jdk-17.0.15.6-hotspot`; both java/javac available.
Godot4.7.2.stable.official.ed1daf0bf under `.work/tools/godot-4.7.2/`;
Steam Blender5.2.1 LTS, build9e2066aef7ef. No replacement needed.

ANDROID_HOME points to `C:/Users/olive/AppData/Local/Android/Sdk`, directory absent.
ANDROID_SDK_ROOT unset; adb/sdkmanager/cmake absent from PATH. C:/Android absent.
`C:/Users/olive/AppData/Roaming/Godot/export_templates` exists but is empty.
Free space at intake: C93.46GB, D2038.71GB. Download cache stays inside .work.
Owner authorizes required official SDK packages/licenses; no Android Studio or
unrelated global dependency installation. Existing Java17 is preferred.

Verified official sources:
- [Godot stable Android export](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_android.html):
  JDK17, required SDK/NDK/CMake versions and standard Windows SDK path.
- [Android command-line tools](https://developer.android.com/studio#command-line-tools-only):
  commandlinetools-win-15859902_latest.zip, SHA256
  90ae805d20434428bffcb699c290860f19bb5f66a67e6b330067e3de801fb04a.
- [Godot4.7.2 official release](https://github.com/godotengine/godot-builds/releases/tag/4.7.2-stable):
  non-Mono export templates archive,1,281,349,702bytes, SHA256
  f298490b8d44d934be425a5a65a51bf15f422428b229a06a6e11d9ffea248011.

Detected/pinned component versions after install and physical device metadata will
be recorded by tools/android/ scripts. Missing hardware remains a blocked device
gate, not an inferred pass. No release/store credentials are generated.
