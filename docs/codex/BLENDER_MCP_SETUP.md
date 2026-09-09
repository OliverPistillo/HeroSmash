# Blender MCP setup

## Current repair supersedes the original installation below

The owner authorized the minimal local hsfix1 repair on 2026-09-09. Current identity
is upstream5f8ddaf6 plus the identified patch, in a separate installation.
**SERVER PREFLIGHT PASSED / SESSION RECONNECT REQUIRED / LIVE NOT VERIFIED.**
Use [the repair report and reproduction procedure](BLENDER_MCP_BOOTSTRAP_FIX.md).
The example TOML now selects the repaired launcher. Original source/venv/add-on
remain intact for rollback; the following sections document the earlier setup and
its then-unresolved defect, not the current patched installation.

## Historical original setup

**CONFIGURED; RESTART REQUIRED; NOT OPERATIONAL.** Recorded 2026-09-09.
This is tooling preparation, not completion of an artistic macro phase.

The integration started on `revival/v1.20-solkael-polish-device-slice` at
`72170ba0295aa992ca1ac7a7954cdb41da5222d3`, including pre-existing v003 work.
Working-tree state matched the prior audit. No reset, cleanup, art edit, production
pipeline change or new branch was performed. Solkael remains suspended.

| Capability | Observed status |
| --- | --- |
| CONFIGURED | Package, add-on, dedicated Blender profile and targeted Codex entry installed |
| SESSION TOOLS DISCOVERED | NO: the actual session exposes no Blender tools or MCP reload tool |
| LIVE OPERATIONS VERIFIED | NO: the required session MCP smoke operations remain pending |

## Fixed source and versions

Community integration: https://github.com/ahujasid/blender-mcp . Mandatory commit:
`5f8ddaf6e987c4aa0c3467fcc548838b28f64477`.

- Package **1.9.1**, add-on **1.6**, add-on protocol **5**, MCP SDK **1.30.0**.
- Existing Python **3.12.0** creates the dedicated venv.
- Existing Blender **5.2.1 LTS**, build `9e2066aef7ef`, embeds Python **3.13.13**.
- Desktop Codex **0.153.4** was used for configuration validation, at
  `C:/Users/olive/AppData/Local/OpenAI/Codex/bin/fd4c151a749f3ab4/codex.exe`.
  The PATH CLI was **0.147.0**; neither was updated.
- No Blender/Godot/Python update or global Python installation was performed.

| Installed item | SHA-256 |
| --- | --- |
| Root/bundled/installed add-on | `f43469c8518c7021e0060e32cfe52e3beb126b0f62fbae7293106642a3ebda89` |
| Server module | `cb42d7a4e69b7711c018a5d3c1ee2d6c90d2fb0a5a5d27e8571469f3f2a902dc` |
| Safe-mode module | `d3bc1f43f4707476e595efed111d514b3f81bf4358993b8accb18962c5c4bf35` |
| Local venv launcher | `24a9704689b41e11cfca74647bbff7122a81063911ef88cfad6225cc9d50634f` |

All ten installed upstream Python files match the fixed checkout byte-for-byte.
Full hashes are in the local `installed-integrity.json`. The launcher hash is
specific to this path/runtime. Initial Windows CRLF conversion was detected before
installation; tracked files were restored to the exact LF Git blobs of the same
commit. No upstream source patch or substitute config module was added.

`blender-mcp.dependencies.txt` records the resolved venv distributions and can
constrain a repeat installation. The raw local freeze also records the checkout
URL. This is **not a wheel-hash lock**; isolated build-tool dependencies were not
locked. Bit-identical reconstruction of the entire venv is not claimed. `pip check`
passed.

## Paths, backups and scope

All installation components are under `D:/Dev/Tools/blender-mcp/5f8ddaf6/`:

| Relative path | Purpose |
| --- | --- |
| `src/` | Mandatory upstream checkout |
| `venv/` | Dedicated Python environment |
| `blender-user-scripts/addons/blender_mcp.py` | Installed add-on |
| `blender-user-config/userpref.blend` | Dedicated Blender preferences |
| `backups/before-setup-20260909/` | Personal TOML backup and before-hash checkpoint |
| `logs/` | Raw local diagnostics |

Smoke artifacts and continuation instructions belong only in
`D:/Dev/HeroSmash/.work/blender-mcp-smoke/`.

`CODEX_HOME` was unset. The effective config was
`C:/Users/olive/.codex/config.toml`; project/ancestor config files were absent.
The TOML was backed up before modification. Its original byte prefix is preserved,
and parsing before/after proved all settings identical except the added
`mcp_servers.blender`. Existing MCPs, plugins, authentication settings, model and
global permissions were preserved. `codex mcp list` still reports `node_repl` and
plugin-provided `cua_repl`, plus `blender`.

The normal Blender 5.2 profile had no userpref.blend and remains untouched. The
dedicated profile avoids interference from the previously open unsaved GUI.
Original PID196/window131226 was preserved. Setup GUI PID27808/window1379414 is a
separate process. These are observed IDs, not permanent launch identifiers.

## Reproduce in a new, inspected destination

If the destination exists, inspect it first; do not blindly replace it. Reuse the
existing Python and Blender executables. The constraints below record the versions
actually resolved during this installation; the first install used the fixed local
checkout and recorded its resulting dependency set.

```powershell
$blenderMcpRoot = 'D:/Dev/Tools/blender-mcp/5f8ddaf6'
$blenderMcpPython = 'C:/Users/olive/AppData/Local/Programs/Python/Python312/python.exe'
# Only when this destination is absent:
git clone --config core.autocrlf=false --no-checkout https://github.com/ahujasid/blender-mcp.git "$blenderMcpRoot/src"
git -C "$blenderMcpRoot/src" checkout --detach 5f8ddaf6e987c4aa0c3467fcc548838b28f64477
git -C "$blenderMcpRoot/src" rev-parse HEAD
Get-FileHash -Algorithm SHA256 -LiteralPath "$blenderMcpRoot/src/addon.py"
& $blenderMcpPython -m venv "$blenderMcpRoot/venv"
& "$blenderMcpRoot/venv/Scripts/python.exe" -m pip install -c D:/Dev/HeroSmash/docs/codex/blender-mcp.dependencies.txt "$blenderMcpRoot/src"
& "$blenderMcpRoot/venv/Scripts/python.exe" -m pip check
```

Set these **process-scoped** values before invoking the server entry point,
including its add-on installer. Do not assume another GUI inherits them.

```powershell
$env:DISABLE_TELEMETRY='true'
$env:BLENDER_MCP_SAFE_MODE='1'
$env:BLENDER_HOST='127.0.0.1'
$env:BLENDER_PORT='9876'
$env:BLENDERMCP_ADDONS_DIR='D:/Dev/Tools/blender-mcp/5f8ddaf6/blender-user-scripts/addons'
$env:PYTHONUTF8='1'
& 'D:/Dev/Tools/blender-mcp/5f8ddaf6/venv/Scripts/blender-mcp.exe' install-addon --addons-dir 'D:/Dev/Tools/blender-mcp/5f8ddaf6/blender-user-scripts/addons'
```

The explicit installer copies the bundled add-on from the fixed installed package.
No updater or uvx/latest command is used. Verify its hash against the table above.

## Opt-out before the interactive listener

Add-on registration auto-starts its listener. Its background guard refuses to
create a socket. A **configuration-only** background process therefore persisted
opt-out in a new dedicated profile before GUI startup. This is not an MCP smoke
test. No startup.blend or project scene was saved.

For both preparation and the dedicated GUI:

```powershell
$env:BLENDER_USER_CONFIG='D:/Dev/Tools/blender-mcp/5f8ddaf6/blender-user-config'
$env:BLENDER_USER_SCRIPTS='D:/Dev/Tools/blender-mcp/5f8ddaf6/blender-user-scripts'
```

The installed Blender `--help` confirms these variables. Save the following
configuration script outside the game repository as `bootstrap_preferences.py`.
Create the dedicated config directory first.

```python
import bpy, addon_utils
from pathlib import Path
base = Path('D:/Dev/Tools/blender-mcp/5f8ddaf6')
assert bpy.app.background and not bpy.data.filepath
assert Path(bpy.utils.user_resource('CONFIG')).resolve() == (base/'blender-user-config').resolve()
module = addon_utils.enable('blender_mcp', default_set=True, persistent=True)
assert module is not None
prefs = bpy.context.preferences.addons['blender_mcp'].preferences
prefs.telemetry_consent = False
module.sync_edit_capture_handlers()
cloud = ['blendermcp_use_polyhaven', 'blendermcp_use_hyper3d',
         'blendermcp_use_hunyuan3d', 'blendermcp_use_sketchfab',
         'blendermcp_use_polypizza']
for scene in bpy.data.scenes:
    scene.blendermcp_auto_start_server = False
    for name in cloud:
        setattr(scene, name, False)
server = getattr(bpy.types, 'blendermcp_server', None)
assert not server or not server.running
assert prefs.telemetry_consent is False
bpy.ops.wm.save_userpref()
```

Run existing Blender with `--background --disable-autoexec --python-exit-code 1
--python <absolute bootstrap path>`. Do not save factory preferences over a normal
user profile. The observed refusal to start a background listener is the expected
upstream safeguard during configuration.

Start a **new GUI** with the same dedicated profile and safety environment, without
`--background`, `--factory-startup` or a .blend argument. Preserve all other windows.
Verify consent=False again and set the five cloud toggles False in the disposable
scene. Those toggles and auto_start are Scene properties; save_userpref does not
persist them. A minimal launch is:

```powershell
Start-Process -FilePath 'C:/Program Files (x86)/Steam/steamapps/common/Blender/blender.exe' -ArgumentList @('--disable-autoexec') -WorkingDirectory 'D:/Dev/HeroSmash/.work/blender-mcp-smoke' -WindowStyle Normal
```

The executed local `prepare_smoke_gui.py` also named the disposable scene
`HS_MCP_SMOKE_20260909`, verified loaded consent/cloud settings and wrote diagnostic
JSON. It did not create the test object or perform any live smoke operation.
The GUI contains only default Cube/Camera/Light and has no saved filepath.

Both the add-on socket and Windows listener reported **127.0.0.1:9876**, PID27808.
BLENDER_HOST configures the client, not the listener. No public bind, firewall
change, tunnel, account or cloud API was used.

## Codex configuration and restart

Append only the Blender tables from `blender-mcp.config.example.toml` to the backed-up
effective TOML and validate the result. The example has the absolute venv launcher,
finite startup/tool timeouts30/120 seconds, six requested tools, safety environment
and `execute_blender_code.approval_mode='prompt'`. Local installed catalog inspection
confirmed the six names; it did not discover them in this session.

Desktop Codex0.153.4 accepted the schema. A negative approval enum was rejected at
the exact per-tool field. `mcp get blender --json` reports the correct STDIO command,
cwd, environment and allowlist; it omits the approval field, which was independently
checked in the parsed TOML. `mcp list` reports all three expected local servers.

The pre-existing global approval policy remains `never`. The per-tool prompt is
configured, but the actual human approval UI is unverified. Do not silently grant
global permissions if this prevents explicit approval of the live smoke code.

No Blender tools appeared in the actual session after configuration. No reload tool
is exposed. A separate app-server or manual socket/SDK client would not verify this
session. **RESTART REQUIRED**: owner-controlled connection/session restart, then
resume only this integration. Codex was not terminated or restarted automatically.

## Known defect in the mandatory pin

`src/blender_mcp/config.py` is absent from the fixed Git tree and explicitly ignored.
No template or generation procedure is supplied. TelemetryCollector imports
`.config.telemetry_config` before checking DISABLE_TELEMETRY. An installed-module
preflight actually reproduced:

```text
ModuleNotFoundError: No module named 'blender_mcp.config'
```

The safety environment was observed in that diagnostic process. This is **not**
measurement of a future Codex-managed server process; that check remains pending.
No stub, monkeypatch, alternate package or new commit was introduced.

Static analysis predicts that startup can continue because telemetry failures are
caught, but get_addon_status fails when querying collector consent. disable_telemetry
can apply opt-out before returning a collector error. These are predictions, not
completed MCP calls. **Restart alone does not fix this defect.** A separately
authorized correction is needed for an entirely passing mandatory smoke suite.

## Security, rollback and publication

DISABLE_TELEMETRY=true is configured for server launch and was present during
installer/preflight. Add-on consent=False was independently observed in the GUI.
All five cloud integrations are False; no API keys were configured. The collector
failure is not claimed as a successful telemetry test or network isolation.

The upstream socket is unauthenticated. Venv, cwd and safe mode do not confine the
filesystem. Safe mode validates MCP Python AST, but bpy save/import/export retain
the user's filesystem permissions. No OS sandbox or system-protection change was
made. Never route a rejected construct around the guard using a raw socket.

To disable, set only mcp_servers.blender.enabled=False, refresh when possible, and
stop the dedicated GUI listener from its MCP panel. Preserve other windows/MCPs.
That stops the current connection only: the enabled add-on auto-starts again when
the dedicated profile is reopened. For persistent rollback, disable **MCP for
Blender** in the preferences of the dedicated GUI/profile and save only its
userpref.blend. Do not save startup files or scenes. Alternatively, leave that
profile and launcher unused. Disabling the Codex entry does not disable the add-on.
To restore, remove only the added Blender TOML tables after checking later edits.
Restore a full personal backup only if unrelated settings still match. The dedicated
profile/add-on/venv can remain inactive; no recursive deletion is required. The
normal Blender profile needs no restore. Never reset the game repository or tags.

Backups, upstream checkout, venv, preference binaries, logs, screenshots and future
smoke scenes stay outside Git. Only reproducible docs and the project-state capability
note belong to this task's commit. Push is withheld: origin remains at
`de770dff30dcc533d547074c975fdaa0962abda9`, and a push would include pre-existing
art commit72170ba beyond this task's publication scope.
