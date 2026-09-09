# v1.15 environment detection — 2026-09-08

Initial working tree clean; branch `revival/v1.15-foundation` at `4ef9eeb503c3c1c69efa36b7b1a3ae5d23cc4816`; main `66a5ba67f0691b7d50a11fa873f4ed24c80a14ef`. Foundation docs already committed in that starting branch. No external-original access.

| Tool | Detected executable / status | Exact version |
|---|---|---|
| Git | `C:\Program Files\Git\cmd\git.exe` | 2.55.0.windows.3 |
| Python used | `C:\Python314\python.exe` | 3.14.7 |
| Other Python launchers | `py -0p`: local pythoncore-3.14-64, Program Files Python313 (normal/free-threaded), local Python312 | Additional interpreters detected; not upgraded |
| Node | Volta shim `C:\Program Files\Volta\node.exe` | 20.19.6 |
| Java | `C:\Program Files\Eclipse Adoptium\jdk-17.0.15.6-hotspot\bin\java.exe` | Temurin 17.0.15+6 |
| Blender | `C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe` | 5.2.1 LTS, hash 9e2066aef7ef, 2026-08-25 build |
| Godot before work | Not in PATH, searched Dev/Downloads/WinGet/Programs/Steam locations | Not found |
| Godot admitted after reporting detection | `.work/tools/godot-4.7.2/Godot_v4.7.2-stable_win64_console.exe` | 4.7.2.stable.official.ed1daf0bf |
| Android | `ANDROID_HOME=C:\Users\olive\AppData\Local\Android\Sdk` does not exist; adb/sdkmanager absent from PATH/searched locations | SDK/build tools/platform tools not found |
| Pillow default Python | `importlib.util.find_spec('PIL')` | Not installed in default interpreter |

Detection included PATH, uninstall registry and Steam library metadata. Blender was found through Steam after the registry entry exposed that origin. No Blender/SDK/MCP/global package install or upgrade was performed. No Android package build or device profiling is claimed. Java alone is not an Android toolchain.

Godot official source: https://godotengine.org/download/archive/4.7.2-stable/ and official `godotengine/godot-builds` release API. ZIP SHA-256 verified against release asset digest: `731980f9608d61333e5baf54a2ef17210acc7a538446c0cb9969f002aca1e953`. Portable ZIP extracted only in ignored `.work/tools/godot-4.7.2`; no PATH or system installation changes. Release metadata retained locally in `.work/tools/godot-release.json`.

Commands: `Get-Command`, `py -0p`, `python --version`, `git --version`, `node --version`, `java -version`, explicit Blender/Godot paths with `--version`. Default Python console encoding required `-X utf8` for emoji-containing legacy records; the initial probe's encoding failure did not change files.

Additional detection: `C:\Users\olive\AppData\Local\Programs\Python\Python312\python.exe` already provides Pillow **12.1.0** and PyYAML, used for arena validation and local workflow parsing. Checked Unity editor roots contain no `adb.exe`/`sdkmanager.bat`; `%APPDATA%\Godot\export_templates` exists but is empty. No SDK/templates were installed during this task.
