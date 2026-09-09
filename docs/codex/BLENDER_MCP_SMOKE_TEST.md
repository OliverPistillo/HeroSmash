# Blender MCP smoke test record

## Approval audit follow-up

**APPROVAL CONFIG FIXED — RESTART REQUIRED / LIVE OPERATIONS NOT VERIFIED.**
[Effective layers, session state and minimal fix](BLENDER_MCP_APPROVAL_AUDIT.md)
are recorded separately. No Blender calls were made during that audit. C–I are
not resumed until the marker-only probe receives actual human approval after
restart and returns successfully. Earlier partial results below remain historical.

## Current live acceptance after reconnect

**CONFIGURED / SERVER PREFLIGHT PASSED / SESSION TOOLS DISCOVERED /
LIVE OPERATIONS NOT VERIFIED.** The actual reconnected session discovered six
tools, invoked four, and obtained/displayed an authentic MCP viewport image.
A/B passed after relaunching the absent dedicated GUI; E/I are partial. The first
read-only code probe was rejected by safe mode without an observed human approval
prompt. No scene mutations were attempted, as explicitly required by the owner.
C/D/F/G/H were not run; no unique object or smoke .blend exists.

See [the current A–I results and exact evidence](BLENDER_MCP_LIVE_RECONNECT.md).
No full live acceptance or artistic resumption is claimed. The sections below
retain the historical setup/repair checkpoint, not the current discovery result.

## Historical bootstrap repair

hsfix1 passed the 15-test unit preflight and real STDIO initialize/list/shutdown.
See [the repair evidence](BLENDER_MCP_BOOTSTRAP_FIX.md). These newly authorized
diagnostics validate server bootstrap; they do not satisfy any original live A–I
gate below. Session tools are still absent. **SESSION RECONNECT REQUIRED.**
All source/export hashes below remain identical after the repair. Historical
statements about no separate diagnostic client apply to the earlier setup only.

## Historical setup and pending live suite

Recorded 2026-09-09. **CONFIGURED / RESTART REQUIRED / NOT OPERATIONAL.**
Solkael art work remains suspended. This report separates preparation diagnostics
from the required Codex-session MCP operations.

## Checkpoint and scope

- Branch: `revival/v1.20-solkael-polish-device-slice`.
- Starting HEAD: `72170ba0295aa992ca1ac7a7954cdb41da5222d3`.
- The pre-existing v003 commit, modified `SOLKAEL_V003_TARGETED_POLISH.md` and
  untracked owner-review/v003 evidence were preserved. They are outside this task.
- Temporary directory: `D:/Dev/HeroSmash/.work/blender-mcp-smoke/`.
- Dedicated GUI scene: `HS_MCP_SMOKE_20260909`, unsaved, default Cube/Camera/Light.
- No Solkael file was opened in Blender. No production code or pipeline was run.

## Preparation checks (not live MCP acceptance)

| Check | Result and evidence |
| --- | --- |
| Source and installed files | PASS: mandatory `5f8ddaf6e987c4aa0c3467fcc548838b28f64477`; ten installed upstream Python files match exact Git source bytes |
| Dedicated Python environment | PASS: Python 3.12.0, package 1.9.1, MCP SDK 1.30.0, `pip check`; resolved dependencies recorded |
| Add-on | PASS: version 1.6/protocol 5, fixed bundled source installed and enabled in a dedicated profile |
| TOML and unrelated configuration | PASS: TOML parses; original bytes preserved as prefix; parsed configuration differs only by the new Blender server |
| Actual desktop CLI | PASS: Codex 0.153.4 `mcp list` and `mcp get blender --json`; existing node_repl/cua_repl entries retained |
| Tool names | PASS, static catalog only: six requested names exist among 28 upstream tools; config allowlists exactly six |
| Per-tool approval configuration | PASS, parser only: execute_blender_code approval_mode=prompt accepted; invalid enum rejected; actual approval UI NOT VERIFIED |
| Effective server environment | PARTIAL: required values present in config readback and the installed-module diagnostic process; Codex-managed server process environment NOT VERIFIED |
| Add-on telemetry consent | PASS, GUI setup diagnostic: False; saved dedicated preferences before listener startup |
| Cloud integrations | PASS, GUI setup diagnostic: Poly Haven, Hyper3D, Hunyuan3D, Sketchfab and Poly Pizza all False; no API keys configured |
| Real GUI and socket | PASS, preparation only: Blender 5.2.1 LTS GUI PID27808; both socket and Windows listener report 127.0.0.1:9876 |
| Existing user GUI/profile | PASS: original unsaved GUI PID196 preserved; normal profile untouched |
| Safe-mode preflight | PASS, local validator only: `import os` rejected; harmless bpy example accepted without execution; this is not smoke I |
| Telemetry collector preflight | FAIL: installed mandatory source raises `ModuleNotFoundError: No module named 'blender_mcp.config'` |
| Actual session discovery | BLOCKED: zero Blender tools and no callable MCP reload tool in the session catalog |

Local diagnostic records are under `D:/Dev/Tools/blender-mcp/5f8ddaf6/`:
`installed-integrity.json`, `runtime-preflight.json`, `preferences-setup.json`,
`gui-setup.json`, `codex-config-validation.json` and `solkael-integrity-after.json`.
Raw logs, personal backups and preferences stay outside Git.

The background run only saved add-on preferences in the dedicated profile. Its
expected refusal to start a background listener is an upstream guard, not evidence
of interactive MCP or a failure of the GUI. The GUI diagnostic script only prepared
the disposable scene and collected settings; it did not execute the smoke suite.

## Required live suite

**Actual Blender MCP tools called by this Codex session: NONE.**
No raw TCP or separate SDK client was used as a substitute.

| Gate | Required operation | Actual result |
| --- | --- | --- |
| A | get_addon_status: versions, protocol, connection, consent | NOT RUN: session tools unavailable |
| B | get_scene_info: match the disposable GUI scene | NOT RUN: session tools unavailable |
| C | approved execute_blender_code: create uniquely named smoke object | NOT RUN: no smoke object created |
| D | get_object_info: verify object name/type/transform | NOT RUN: session tools unavailable |
| E | get_viewport_screenshot: frame the object and show the actual MCP image in the session | NOT RUN: no MCP viewport image |
| F | approved code: change transform/material, inspect and capture; restore and inspect | NOT RUN: no test edits |
| G | approved code: save/reopen only inside the smoke directory | NOT RUN: no smoke .blend saved |
| H | controlled GUI listener stop/start on this scene; successful new MCP call | NOT RUN: live reconnection not verified |
| I | approved harmless prohibited construct rejected through execute_blender_code | NOT RUN: local AST validation is not this gate |

`GUI_SETUP_ONLY.jpg` in the smoke directory is a native computer-use screenshot
showing the dedicated GUI. It is explicitly **not MCP viewport evidence** and does
not satisfy E or F. No Godot render or previously generated art is used as evidence.

## Two independent blockers and continuation

1. The running Codex session cannot discover the new tools without an owner-controlled
   connection/session refresh. **RESTART REQUIRED**. No hosting app was terminated.
2. The mandatory upstream tree omits `src/blender_mcp/config.py` and ignores that
   filename. `TelemetryCollector` imports it before checking DISABLE_TELEMETRY.
   Static analysis predicts get_addon_status and disable_telemetry error paths;
   these predictions are not reported as actual MCP call results. A restart cannot
   repair the missing module. No stub, monkeypatch or different revision was used.

After the owner-controlled refresh, resume only this integration. First confirm the
six actual session tools and observe explicit approval for execute_blender_code.
Record the real managed-server environment, independently of the GUI. Read local
`HANDOFF.md`, recheck the branch/assets and identify the dedicated GUI/listener.
Do not infer success from codex mcp list. Do not open Solkael.

Attempt A and record its real result before continuing. The known upstream defect
requires a separately authorized correction for a fully passing suite; do not
silently alter the mandatory pin. Continue applicable independent gates only through
actual session tools, preserving safe mode and human code approval. For H, use the
dedicated GUI MCP sidebar to Disconnect/Connect; do not stop the listener from its
own in-flight code request. Save only within the smoke directory. Forward MCP image
content so the session actually sees it. Stop after this assignment.

## Solkael integrity

All **45** recorded source/export/texture/manifest/import/wrapper files are unchanged
from the starting checkpoint, including ignored .blend backups and export copies.
The following SHA-256 values are identical **before and after** this task:

| Artifact | Before SHA-256 = after SHA-256 |
| --- | --- |
| v001 source .blend | `9119d863149a2c6b3dc24fe3064acba715e76453bf95852b9336bb1bca2aadb2` |
| v001 GLB, both copies | `3cd9e3024dbd85b8eaf3376e0e3e2b05f2aca6a4626794157e333a39b6400554` |
| v002 source .blend | `9d4165f9cc7dc562db5bda05e4f0420bdccd53908004a828d93ea9acb036ff0b` |
| v002 GLB | `558a6566b8fa8a473f7f0b5460b68f73a365558b451a81a7208dc1fe82dc4108` |
| v003 source .blend | `b665dac352ad7a20f6c9f8da86e1edb4c9bf61d682dec2b1ff1a91546d21f732` |
| v003 GLB | `d4abdf5aa8cdcd632c57173ed5b5bd879da78273c48081973f2d9ead52aaa368` |

Full before records: installation directory
`backups/before-setup-20260909/checkpoint-before.json`.
Full comparison: `solkael-integrity-after.json` in the installation directory.

## Scope of validation and publication

Applicable checks are configuration parsing/readback, dependency consistency,
source/add-on hashing, loopback verification, preservation checks and documentation
whitespace/link checks. Game simulation, Android, production Blender export and
Godot render gates were not rerun: no game or production pipeline changes were made.
They would not establish MCP functionality.

Only the setup/smoke documentation, config example, dependency constraints and the
project-state capability note belong in the documentation commit. No push: the
branch would also publish pre-existing art commit `72170ba`. The remote was fetched
and inspected at `de770dff30dcc533d547074c975fdaa0962abda9`.

See [setup and rollback](BLENDER_MCP_SETUP.md). No artistic approval or new macro
phase is declared.
