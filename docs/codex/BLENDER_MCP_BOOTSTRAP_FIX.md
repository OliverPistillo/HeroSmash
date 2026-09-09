# Blender MCP bootstrap repair — hsfix1

Current acceptance: **BLENDER MCP OPERATIONAL** after the owner selected Ask for
approval. The actual turn uses on-request/user; manual approval, marker execution
and all C–I gates passed. See [the completed suite](BLENDER_MCP_SMOKE_TEST.md) and
[approval evidence](BLENDER_MCP_APPROVAL_AUDIT.md). The installed bootstrap repair
remains unchanged. Solkael remains suspended.

## Historical bootstrap and first reconnect checkpoint

Updated 2026-09-09 after the owner-controlled session reconnect.
**CONFIGURED / SERVER PREFLIGHT PASSED / SESSION TOOLS DISCOVERED /
LIVE OPERATIONS NOT VERIFIED.** Solkael art remains suspended.
Current acceptance and approval anomaly: [live reconnect report](BLENDER_MCP_LIVE_RECONNECT.md).
The detailed bootstrap/preflight record below describes the earlier repair.

| Capability | Result |
| --- | --- |
| CONFIGURATION WRITTEN | Yes; only mcp_servers.blender.command changed after tests |
| SERVER PREFLIGHT PASSED | Yes; 15 unit tests and real STDIO initialization passed |
| SESSION TOOLS DISCOVERED | Yes; exactly six in the reconnected session; four actually invoked |
| LIVE OPERATIONS VERIFIED | No; A/B pass, E/I partial, C/D/F/G/H not run; stopped at code-approval anomaly |

## Identity and scope

Community upstream: https://github.com/ahujasid/blender-mcp .
Mandatory source commit: `5f8ddaf6e987c4aa0c3467fcc548838b28f64477`.

This installation is explicitly **upstream commit plus local patch**, not pristine
upstream. Patch ID: `hsfix1-telemetry-disabled`.

Patch SHA-256:
`c58383fdcd9c109cb819f0d91b9c0809fd5dcf74f98ae06b871f55e342700ad8`.

The complete applicable patch is
`tools/mcp_bootstrap/patches/hsfix1-telemetry-disabled.patch`.
`tools/mcp_bootstrap/patch_identity.json` records the upstream and installed SHA-256
for all ten Python files. Fresh archive application reproduces every installed
file. A scoped .gitattributes keeps the patch LF bytes stable on Windows and permits
the single-space blank context lines required by unified diff. Source whitespace
is checked separately in the upstream checkout.

New variant: `D:/Dev/Tools/blender-mcp/5f8ddaf6-hsfix1/`.
Original installation: `D:/Dev/Tools/blender-mcp/5f8ddaf6/`, preserved for rollback.
Server package remains **1.9.1**, add-on **1.6**, add-on protocol **5**, MCP SDK
**1.30.0**, Python **3.12.0**, existing Blender **5.2.1 LTS**.
The original add-on/profile is reused; no add-on reinstall or extra Blender GUI.

Only three upstream files change: telemetry.py, consent_prompt.py, trajectory.py.
server.py, telemetry_decorator.py, safe_mode.py, add-on and execution/protocol
contracts are byte-identical. No production pipeline/gameplay/art changes.

## Reproduced cause and consumer audit

The unpatched collector failed with DISABLE_TELEMETRY=true, using the original
venv executable and modules under its own site-packages. Full traceback and all
resolved module paths were preserved locally before changing source:
`5f8ddaf6-hsfix1/logs/unpatched-{traceback.txt,reproduction.json}`.

```text
telemetry.py, line 74, in __init__
    from .config import telemetry_config
ModuleNotFoundError: No module named 'blender_mcp.config'
```

The fixed source has one direct config import, in telemetry.py. Its .gitignore
line15 excludes src/blender_mcp/config.py; no tracked config/template/generator is
provided. Consumer review covered telemetry, both telemetry decorator families,
trajectory wrappers/recorder, consent prompting and server startup/shutdown plus
the six requested tools. No generic config package, fabricated endpoint/credential
or downloaded fork configuration was introduced.

## Correction

- Collector initializes the real add-on consent cache/lock first. An existing
  disable flag selects an immutable enabled=False configuration before importing
  optional config, creating identifiers, persistent state, queues or workers.
- Without any disable flag, an absent optional module also selects disabled mode
  with an explicit warning. Only ModuleNotFoundError naming blender_mcp.config is
  handled; nested import errors and malformed configurations propagate. No silent
  telemetry activation occurs when configuration/flags are absent.
- record_event, upload_screenshot and the private sender cannot send when disabled.
  Consent reads still return the actual add-on response True/False, or None when
  unreachable. Add-on consent never overrides the server's global opt-out.
- Consent prompting returns before state reads/writes or elicitation while the
  server is disabled; repairing initialization must not invite opt-in implicitly.
- The trajectory factory returns an explicit disabled recorder with all twelve
  interfaces used by the consumers, including shutdown/flush. It allocates no
  queue, worker, timer, identifier or scene/screenshot/client-history storage.
  Decorators and tool implementations retain their existing behavior.

No blanket exception handler was added around actual tool errors. Unit tests prove
sync/async return values and exception identity are preserved.

## Executed preflight

| Gate | Result |
| --- | --- |
| Original failure reproduction | PASS: expected ModuleNotFoundError with opt-out true, full traceback retained |
| A: imports/component initialization | PASS in the corrected venv; also exercised by real server lifespan |
| B: telemetry paths of six authorized tools | PASS: actual decorated functions, strict simulated Blender transport; no real code/scene edits |
| C: missing config/flags | PASS: absent, false and zero flags fail closed with warning; malformed/nested errors propagate |
| D: instrumented telemetry sends | PASS: zero calls to httpx.post, Client.send, AsyncClient.send and trajectory._post_row |
| E: safe mode regression | PASS: harmless code reaches only the fake; import os rejected before execute dispatch |
| F: real STDIO entry point | PASS: initialize, notifications/initialized, tools/list; graceful stdin EOF shutdown, exit0 |
| Dependency/source validation | PASS: pip check, all32 runtime versions unchanged, ten installed source files match declared identity |
| Patch applicability | PASS: fresh fixed Git archive plus patch reproduces installed source bytes |

The unit suite has **15 tests**, including 15 disable-flag/value subcases, true/
false/unreachable consent and cache invalidation, screenshots suppressed from
upload even with add-on consent=True, no-op recorder interfaces, and sync/async
success/error behavior in all three decorator families. Guards count attempted
UUID, queue, worker, persistent-state and elicitation activity: zero.

This instrumentation concerns the telemetry components exercised by these tests.
It is **not a general capture or firewall verification of all process traffic**.
Simulated fixture PNGs are not viewport evidence. Real session MCP tools called:0.

STDIO result: protocol `2025-11-25`, server name BlenderMCP, launcher PID11088,
elapsed0.672s, exit0, forced_cleanup=False, stdout reader finished. serverInfo.version
reports the FastMCP SDK version1.30.0; distribution metadata remains blender-mcp1.9.1.
The upstream catalog contains **28** tools. All six required names are present;
the six-tool allowlist is applied separately by Codex and does not alter that
upstream catalog. No tools/call message was sent by the diagnostic client.

The unchanged server lifespan performed its normal get_addon_info handshake with
the existing GUI, observing add-on1.6/protocol5/Blender5.2.1LTS, then disconnected.
Therefore this test is not described as zero Blender socket traffic. No scene or
asset modification occurred. No diagnostic server/client remains connected.

Local evidence is under `5f8ddaf6-hsfix1/logs/`: unit-preflight.log and
stdio-preflight/{stdio-preflight.json,stderr.log,client-stdin.jsonl,
server-stdout.jsonl,upstream-tool-catalog.json}. Raw diagnostics remain outside Git.

Two preparation issues were resolved: the first unit fixture omitted the normal
screenshot tool's separate consent read (fixed to True to test upload suppression);
the first fresh-patch byte comparison encountered global Git CRLF conversion
(fixed with explicit core.autocrlf=false). Neither required changing production
code, the package patch, safe mode or dependencies. Final required preflight gates
have no failures. Original live A–I have not been executed.

## Reproduce the variant

Inspect destinations first. Do not overwrite an existing installation. Keep the
original profile, add-on and old venv intact. Example commands assume a fresh
variant destination and this technical worktree's checked-out files:

```powershell
$mcpFixRoot = 'D:/Dev/Tools/blender-mcp/5f8ddaf6-hsfix1'
$mcpFixRepo = 'D:/Dev/HeroSmash-mcp-bootstrap-fix'
$mcpFixPython = 'C:/Users/olive/AppData/Local/Programs/Python/Python312/python.exe'
git clone --config core.autocrlf=false --no-checkout https://github.com/ahujasid/blender-mcp.git "$mcpFixRoot/src"
git -C "$mcpFixRoot/src" checkout --detach 5f8ddaf6e987c4aa0c3467fcc548838b28f64477
Get-FileHash -Algorithm SHA256 "$mcpFixRepo/tools/mcp_bootstrap/patches/hsfix1-telemetry-disabled.patch"
# Require the exact patch hash above before proceeding.
git -C "$mcpFixRoot/src" -c core.autocrlf=false apply --check "$mcpFixRepo/tools/mcp_bootstrap/patches/hsfix1-telemetry-disabled.patch"
git -C "$mcpFixRoot/src" -c core.autocrlf=false apply "$mcpFixRepo/tools/mcp_bootstrap/patches/hsfix1-telemetry-disabled.patch"
& $mcpFixPython -m venv "$mcpFixRoot/venv"
$env:PIP_CONSTRAINT="$mcpFixRepo/docs/codex/blender-mcp.build-constraints.txt"
& "$mcpFixRoot/venv/Scripts/python.exe" -m pip install -c "$mcpFixRepo/docs/codex/blender-mcp.dependencies.txt" "$mcpFixRoot/src"
Remove-Item Env:PIP_CONSTRAINT
$env:DISABLE_TELEMETRY='true'
$env:BLENDER_MCP_SAFE_MODE='1'
$env:BLENDER_HOST='127.0.0.1'
$env:BLENDER_PORT='9876'
$env:PYTHONDONTWRITEBYTECODE='1'
& "$mcpFixRoot/venv/Scripts/python.exe" "$mcpFixRepo/tools/mcp_bootstrap/verify_installation.py" --installation "$mcpFixRoot"
& "$mcpFixRoot/venv/Scripts/python.exe" "$mcpFixRepo/tools/mcp_bootstrap/test_telemetry_disabled.py" -v
& "$mcpFixRoot/venv/Scripts/python.exe" "$mcpFixRepo/tools/mcp_bootstrap/stdio_preflight.py" --command "$mcpFixRoot/venv/Scripts/blender-mcp.exe" --output-dir "$mcpFixRoot/logs/stdio-repeat"
```

The first hsfix1 install used the unchanged runtime constraints and recorded its
isolated build dependencies: packaging 26.3, setuptools 84.0.0, wheel 0.48.0. The separate
build constraints record those versions for subsequent builds; original build
dependencies were not previously recorded. This is not a wheel-hash lock or a claim
of byte-identical venv reconstruction. No global package/tool upgrade was performed.
The original-failure reproduction script must use the old venv; it intentionally
returns failure if that original missing-module error is no longer reproduced.

## Configuration, security and rollback

After successful tests, only mcp_servers.blender.command changed in
`C:/Users/olive/.codex/config.toml`, from the old venv launcher to
`D:/Dev/Tools/blender-mcp/5f8ddaf6-hsfix1/venv/Scripts/blender-mcp.exe`.
Prior backup: `5f8ddaf6-hsfix1/backups/config-before-hsfix1.toml`.
Parsed before/after and exact-byte replacement prove every other setting preserved.
Desktop Codex0.153.4 mcp get reports the corrected command. The example TOML matches.

Preserved: STDIO, six tools, execute_blender_code approval_mode=prompt, timeouts30/
120s, DISABLE_TELEMETRY=true, BLENDER_MCP_SAFE_MODE=1, BLENDER_HOST=127.0.0.1,
BLENDER_PORT=9876, original add-on directory and all other MCP/global settings.
Actual human approval UI and future Codex-managed process environment are still
unverified. No global permission change or bypass was introduced.

The diagnostic child received explicit launch environment values; stderr confirms
the disabled collector path. That launch record is not an independent environment
read of a future Codex-managed process. Existing add-on consent=False/profile and
five disabled cloud toggles were left unchanged. Actual listener remains solely
127.0.0.1:9876 in existing Blender PID27808. The original GUI PID196 remains open.
Consent/cloud must also be rechecked through the real session during live acceptance.

The socket remains unauthenticated; loopback is not a filesystem sandbox. Safe mode,
cwd and venv do not restrict bpy filesystem access to the smoke directory. No public
ports, firewall changes, cloud integrations, keys or OS protection changes.

Rollback changes only the command back to the original launcher after stopping any
diagnostic client. Restore the entire personal backup only after checking later
unrelated edits. The old source, venv, add-on and preferences remain intact. Disabling
Codex's entry or stopping the listener does not prevent add-on autostart on the next
dedicated GUI launch; disable the add-on in that dedicated profile and save only
its user preferences for a persistent disable. Preserve other GUI work and profiles.

Two unrelated upstream caveats remain documented: disable_telemetry's generic text
mentions minimal anonymous counts even though global opt-out suppresses all sends;
the enabled-consent _apply_consent path references a nonexistent telemetry symbol.
The latter is unreachable under this disabled profile and was not refactored.

## Preservation, Git and handoff

Original worktree `D:/Dev/HeroSmash` stays on revival/v1.20-solkael-polish-device-slice
at `555d26c9fe9373379d316c4d655f7dbd8ff100cd`, with its original tracked diff and
untracked art evidence. All 45 Solkael and 127 pre-existing evidence file hashes match
before/after; all 3,822 old-installation files match. Main and tags remain unchanged.
Full local before/after records: hsfix1/baseline.json and preservation-after.json.
The six source/GLB SHA-256 pairs are also in BLENDER_MCP_SMOKE_TEST.md and remain
unchanged. No Solkael file was opened.

Technical worktree: `D:/Dev/HeroSmash-mcp-bootstrap-fix`.
Branch: `chore/blender-mcp-bootstrap-fix`, based directly on verified remote v1.20
`de770dff30dcc533d547074c975fdaa0962abda9`.
The inspected docs-only commit555d26c was cherry-picked alone as
`7e0ab92a6650213667a1d2f8b07e2cae32c03fb2`; no conflict and no art ancestor imported.
Patch, tests, constraints and command example are committed as
`fdb23c1dba34cd0524fe8084f089050c09cfe3a6`.
Commit72170ba and its assets are excluded. Only integration files may enter the PR,
which targets revival/v1.20-solkael-polish-device-slice as Draft, without merge.

Local handoff: `D:/Dev/HeroSmash/.work/blender-mcp-smoke/HANDOFF.md`.
After an owner-controlled session reconnect, resume only the actual MCP gates A–I
in BLENDER_MCP_SMOKE_TEST.md. No automatic app restart was performed. Do not treat
this diagnostic client, fixture image, CLI or native screenshot as live acceptance.
Game/Godot/production export gates were not run for this isolated integration patch.
Art remains suspended even after the future live checks.
