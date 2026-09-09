# Blender MCP live reconnect acceptance — 2026-09-09

Subsequent owner-authorized approval audit:
[APPROVAL CONFIG FIXED — RESTART REQUIRED](BLENDER_MCP_APPROVAL_AUDIT.md).
Only approval_policy changed from never to on-request; the current loaded task
still has never/user. No additional Blender calls or smoke acceptance followed.
The report below preserves the actual earlier live results.

**CONFIGURED / SERVER PREFLIGHT PASSED / SESSION TOOLS DISCOVERED /
LIVE OPERATIONS NOT VERIFIED.** Acceptance stopped at the first code-approval
probe. No artistic work resumed. Do not describe this integration as operational.

## Scope and checkpoint

Technical worktree: `D:/Dev/HeroSmash-mcp-bootstrap-fix`.
Branch: `chore/blender-mcp-bootstrap-fix`.
Clean starting/tested HEAD: `e42aa96900040fd2aabbe837db9777190dcd9800`.
Installed identity remains upstream `5f8ddaf6e987c4aa0c3467fcc548838b28f64477`
plus `hsfix1-telemetry-disabled`. No reinstall, dependency update, configuration
edit, startup/preference save, asset load, production export or scene save occurred.

This record supersedes the earlier session-discovery blocker in the
[bootstrap report](BLENDER_MCP_BOOTSTRAP_FIX.md),
[setup history](BLENDER_MCP_SETUP.md) and
[original A–I specification](BLENDER_MCP_SMOKE_TEST.md).
The earlier 15-test and STDIO preflight passes remain historical evidence; they
were not rerun or relabeled as current live acceptance.

## Discovery and real connection

The actual current session catalog exposed exactly these six Blender tools:
`get_addon_status`, `get_scene_info`, `get_object_info`,
`get_viewport_screenshot`, `execute_blender_code`, `disable_telemetry`.
This was runtime tool discovery, not `codex mcp list` or a separate SDK client.
The allowlist and the other MCP configurations were not changed.

Initial actual calls to status, scene and screenshot all failed to connect.
The first two returned text containing `Could not connect to Blender`; screenshot
returned `Screenshot failed: Could not connect to Blender` and no image.
The handoff's dedicated GUI PID27808 was absent and no listener owned port9876.
Original unsaved GUI PID196/window131226 remained open.

The existing Blender executable was launched once with `--disable-autoexec`,
the existing dedicated user-config/user-scripts profile, the documented safety
environment and the smoke directory as cwd. No .blend or Python script argument
was supplied. No setup script or alternate socket client performed scene work.
New GUI PID16264/window7146580 was identified independently through process/window
inventory and native GUI inspection. It is a fresh unsaved default `Scene` with
Cube/Camera/Light, **not** the lost unsaved `HS_MCP_SMOKE_20260909` scene.
That name difference is recorded rather than silently renaming it outside MCP.

The next actual MCP status, scene and screenshot calls succeeded. Status reports
add-on1.6, protocol5/expected5, Blender5.2.1 LTS, up_to_date=True and
telemetry_consent=False. The image returned through MCP was displayed in the
session and preserved from the exact returned PNG bytes. Native GUI images were
used only to identify the window; they are not the MCP viewport evidence.

## Protections and observable limits

| Control | Current evidence |
| --- | --- |
| Managed command | Codex PID30588 → launcher30800 → venv Python34460 → Python13128; hsfix1 launcher path verified |
| Server opt-out | Actual Python13128 process environment: DISABLE_TELEMETRY=true |
| Add-on consent | Actual get_addon_status result False, repeated after the rejected probe |
| Safe mode | Actual process environment BLENDER_MCP_SAFE_MODE=1 and actual MCP rejection below |
| Client address | Actual process environment BLENDER_HOST=127.0.0.1, BLENDER_PORT=9876 |
| Listener bind | Get-NetTCPConnection: sole listener127.0.0.1:9876, GUI PID16264; no wildcard/public bind |
| Cloud toggles | NOT VERIFIED for the newly launched scene; earlier all-False readings do not establish current scene properties |
| Code approval | Config says prompt; no human prompt observed for the first actual code call, which returned immediately |

Read-only Windows process-memory inspection also observed
`BLENDERMCP_ADDONS_DIR=D:/Dev/Tools/blender-mcp/5f8ddaf6/blender-user-scripts/addons`
and `PYTHONUTF8=1`. The two other Codex-managed server chains had the same safety
environment. The screenshot temp basename `blender_screenshot_13128.png` in current
Codex stderr associates this task's calls with the chain above.

Effective opt-out inputs are independently verified, but no fresh process-wide
network capture or collector-internals inspection was performed. Historical
instrumented zero-send tests are not proof of newly measured absence of all traffic.
The bounded current log query did not retain telemetry initialization rows.
Loopback and safe mode are not an OS filesystem/network sandbox.

The Blender TOML stanza still exactly matches activation, including per-tool
`approval_mode="prompt"`; global `approval_policy="never"` remains unchanged.
The whole personal TOML differs from the historical activation hash only in parsed
node_repl pipe-directory and reasoning-effort values. Those pre-existing differences
were observed, not edited or reset. Root cause of approval behavior is unproven.

## First code call and stop condition

The first and only execute_blender_code request was a read-only probe. It guarded
against a background/file-backed/unexpected scene and attempted to print the scene,
filepath, consent, five cloud toggles and default Cube transforms. No object/material
creation, property assignment, save, restore or listener operation was requested.
The exact submitted code and response are in the local session JSON listed below.

Its line11 read was:

```python
"telemetry_consent": bpy.context.preferences.addons["blender_mcp"].preferences.telemetry_consent,
```

Actual tool response, also corroborated by managed-server stderr at
14:50:52.089 Europe/Rome:

```text
Rejected by safe mode - line 11: 'preferences' reached through an unresolvable receiver; module navigation must start from a plain name so it can be checked against the path rules
```

The validator rejected the entire script before dispatch to Blender. Therefore
the guards and printed values were **not executed** and are not observations.
No approval prompt was observed; approval of accepted/executed code remains
unverified. The owner explicitly required stopping further modifications when
the expected confirmation was absent, so no second code call, workaround, guard
change or scene mutation was attempted. Only status/scene reads followed.
This is an approval anomaly plus a real safe-mode rejection, not successful
approval and not a completed create/edit/restore suite.

## A–I results and call inventory

| Gate | Result |
| --- | --- |
| A: add-on status | PASS after dedicated GUI relaunch; first attempt failed to connect |
| B: disposable scene | PASS for the newly identified unsaved GUI; historical scene name was not retained |
| C: approved unique object creation | NOT RUN; approval anomaly stopped scene mutations before creation |
| D: unique object properties | NOT RUN; no smoke object exists and get_object_info was not invoked |
| E: framed smoke-object viewport | PARTIAL; real initial MCP PNG returned/displayed, but no unique object was created/framed |
| F: transform/material edit, verify, restore | NOT RUN; no before/after/restore series exists |
| G: save/reopen temporary .blend | NOT RUN; no .blend saved or reopened |
| H: controlled listener stop/start and MCP retry | NOT RUN; initial missing-GUI recovery does not satisfy this gate |
| I: approved harmless prohibited construct | PARTIAL; benign preference read rejected by actual MCP safe mode, but approval unverified and planned negative control not run |

Four distinct tools were actually invoked, nine calls total:
get_addon_status×3, get_scene_info×3, get_viewport_screenshot×2,
execute_blender_code×1. get_object_info and disable_telemetry were discovered but
not invoked. No other Blender tool, raw TCP execution or substitute client was used.

Initial-success and final get_scene_info results are identical: `Scene`, three
objects, two material datablocks. Cube location[0,0,0], Light[4.08,1.01,5.9],
Camera[7.36,-6.93,4.96], as rounded by that tool. Complete rotation/scale/material
inspection and numerical edit/restore validation are not claimed.

## Authentic local evidence and preservation

Evidence directory:
`D:/Dev/HeroSmash/.work/blender-mcp-smoke/live-20260909-reconnected/`.

- `session-evidence.json`: discovery names, actual scene/error/status responses,
  exact first code request/rejection and GUI identification.
- `viewport-initial-mcp.png`: actual returned viewport,1000×581,241528bytes,
  SHA-256 `419c1407c489e43e8521307b04623c04773103d960bca36a7ca6ec03e036b1df`.
- `preservation-final.json`: final rehash against the existing checkpoint.

GUI stdout/stderr files are in the parent smoke directory. The current Codex
`logs_2.sqlite` was queried read-only for relevant MCP stderr; unrelated logs,
personal configuration and raw process memory are not published. Images, raw
diagnostics and temporary files remain local, as required by the setup policy.

The recorded 45 Solkael files and127 prior evidence files match the hsfix1 baseline;
the45 also match the original pre-setup checkpoint. The original worktree remains
at555d26c9fe9373379d316c4d655f7dbd8ff100cd on its original branch, with the same
pre-existing art-plan change and untracked owner-review/v003 evidence.
Its binary diff SHA-256 remains
`c5c29d32277fb119ec211714e6c59dbd98e8d880dc7638f37065fbbf63a28214`.
Main and all six tags are unchanged. Art72170ba is not an ancestor of the technical
branch. No Solkael asset was opened in Blender. Original GUI PID196 was preserved.

## Validation, publication and remaining work

Executed: actual MCP calls above, process/loopback/window checks, scoped live log
and effective-environment inspection, checkpoint SHA-256 comparisons, Git ancestry,
documentation whitespace and relative-link checks. No code changed, so server
unit/preflight, Godot, Android and production export checks were not rerun locally.
They cannot substitute for pending live gates. The unchanged GitHub CI is checked
against the new published documentation commit; its exact SHA and run results
are recorded in Draft PR3 and the task delivery.

Only this report and the current-capability notes in PROJECT_STATE/setup/smoke/
bootstrap documentation belong to the new commit. Publish to the existing
chore/blender-mcp-bootstrap-fix branch and retain Draft PR3 against v1.20; no merge,
force push, tag change or artistic commit is included.

Remaining acceptance requires resolving/observing the intended approval behavior,
rechecking cloud opt-outs for the disposable scene, then executing approved C–I
with genuine MCP before/after/restore images. This task does not authorize a blind
configuration fix or automatically start another phase. Solkael v003 stays suspended.
