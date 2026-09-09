# Blender MCP approval routing audit — 2026-09-09

## Current acceptance after owner selected Ask for approval

**BLENDER MCP OPERATIONAL.** The actual turn now records
`approval_policy=on-request`, `approvals_reviewer=user`, profile `:workspace` and
workspace-write restrictions. The owner manually selected this task profile;
the assistant did not change permission or server configuration. A restart was
not needed for this profile change to affect the new turn.

| Check | Actual result |
| --- | --- |
| Effective turn | `01a08675-2ff6-7c51-9aad-3b418e99a243`, first context at 13:57:02.156Z |
| approval_policy / approvals_reviewer | `on-request` / `user` in the actual task rollout |
| execute_blender_code rule | Configured `prompt`; human prompting verified through actual MCP calls and explicit owner confirmation |
| Server default approval mode | Unset; no fallback value is inferred |
| Discovery | All six allowlisted tools available; five used, 21 MCP calls total |
| Human prompt | Owner confirmed the prompt and manual Approve for both marker attempts |
| Marker | Second exact `print("HS_MCP_APPROVAL_PROBE")` returned the marker successfully |
| Safe mode | Accepted the marker; later rejected `import os` at line 1 before dispatch |
| Smoke C–I | All passed; [operations and evidence](BLENDER_MCP_SMOKE_TEST.md) |

The first exact marker call was manually approved but failed with `Could not
connect to Blender`; it did not execute in Blender. No listener was present.
The existing user GUI PID 21800 was preserved. A separate GUI PID 8104 was started
with the existing dedicated profile and `--disable-autoexec`, without a file or
script argument. Its listener was verified at `127.0.0.1:9876`. The identical
marker retry received another prompt and manual approval, confirmed by the owner,
and returned `HS_MCP_APPROVAL_PROBE` before any scene mutation.

The earlier failure to apply on-request after restart is historical. Selecting
Ask for approval changed the effective task profile and resolved that prerequisite.
The successful tool interaction establishes the observed human routing; this
does not pretend that a separate config resolver is the resident Desktop server.
No new direct resident managed-policy response was available. Earlier separate
`configRequirements/read` returned null; no managed restriction was bypassed.

The final personal config hash differs from the start: three read-only rules
were added with `approval_mode=approve` for get_object_info, get_scene_info and
get_viewport_screenshot. The diff alone does not establish their origin. The
assistant issued no config write or restoration. Execute remains `prompt`, the
default remains unset, and on-request/user, the configured sandbox, command,
allowlist, environment, telemetry, safe mode, host/port and timeouts are unchanged.
Start SHA-256: `2cbc58e99c9485bffeb2a2fef911f870553cc1f0916c6542c489d4ab63702cdc`.
Final SHA-256: `1e6aaaada415826a29f4a23a7b46b3b7597cd30344c74f6c05f039438db878c3`.
No claim that the entire Blender stanza is byte-identical is made.

Sanitized local evidence: `approval-ask-profile-20260909/session-config.json`,
`live-results.json`, `image-manifest.json` and `preservation-final.json` under the
documented smoke directory. Personal settings and backups remain outside Git.
The final configuration comparison is in `config-final-diff.json` alongside it.

This completes only MCP acceptance. Solkael was not opened or edited, no
installation or protection was changed, and no artistic continuation is authorized.

## Historical check after owner restart — 15:39 Europe/Rome

**LIVE OPERATIONS NOT VERIFIED — SESSION APPROVAL PREREQUISITE NOT MET.**
The owner restart is observed, but the new turn still runs with `never/user`.
The marker probe was not sent because the required effective on-request policy
was not established. No Blender call, configuration change or scene/GUI operation
occurred in this resumed attempt. C–I were not resumed.

| Evidence | Actual current result |
| --- | --- |
| Desktop restart | New Codex0.153.4 app-server PID13016, started15:39:08.896; previous PID30588 absent |
| New task turn | 01a08664-f96e-7580-ab2a-29e82d1f33ef,13:39:20.160Z; current task rollout line584 |
| Effective turn approval_policy | never |
| Effective turn approvals_reviewer | user |
| Effective permission profile | :danger-full-access; disabled profile representation; danger-full-access sandbox |
| Resolved disk approval settings | on-request/user, independently reread for both worktrees |
| execute_blender_code approval rule | prompt in unchanged resolved Blender stanza; resident rule not directly readable |
| Session tool discovery | All six allowlisted Blender tools present; zero invoked in this attempt |
| Managed requirements | Separate installed resolver returns requirements:null; no direct resident response available |
| Human prompt / marker / smoke C–I | Not attempted because the earlier policy prerequisite failed |

The exact task database row also reports approval_mode=never. Saved app mode
remains full-access and its task permission snapshot remains never/user. The new
process launch flags contain no approval/reviewer/profile or Blender override.
These observations establish the effective mismatch after an actual restart,
but not the precise origin or precedence of the app/task override. No managed
restriction is proven and no managed setting was bypassed.

The existing diagnostic used installed config/read(includeLayers), not Blender
or synthetic marker execution. Layers remain user plus empty system; no project,
profile or managed layer was returned. Current personal config SHA-256:
`2cbc58e99c9485bffeb2a2fef911f870553cc1f0916c6542c489d4ab63702cdc`.
Compared with the prior validated fix, only the node_repl native-pipe-directory
value changed before this attempt. Approval settings and the complete Blender
stanza are identical. No configuration was edited or restored here.

Local evidence under
`D:/Dev/HeroSmash/.work/blender-mcp-smoke/approval-resume-20260909-1539/`:
resolved-config.json, current-session-evidence.json, config-preservation.json and
preservation.json. The full sanitized resolver response also remains in
approval-audit-20260909/config-read-resumed-1.json. The supplied
`D:/Dev/HeroSmash.work/blender-mcp-smoke/HANDOFF.md` path was absent; the existing
documented `D:/Dev/HeroSmash/.work/blender-mcp-smoke/HANDOFF.md` was read instead.

Starting technical commit: `1ef2c6b3130a5b95f11e06f63b523adfc5066782` on
chore/blender-mcp-bootstrap-fix. All45 Solkael/127 evidence hashes, original artistic
worktree state, main and six tags remain unchanged. Art72170ba stays excluded.
Only integration documentation is published to Draft PR3. Whitespace/link checks
and exact new-commit CI are recorded in task/PR delivery. No new runtime image
exists; previous viewport evidence is not reused as a new test.

Continuation requires the actual task to resolve approvalPolicy=on-request and
approvalsReviewer=user while preserving its existing sandbox and Blender settings.
Another restart alone is not established as a remedy. No task-permission repair
was attempted within this smoke-only request. Recheck effective settings before
the first exact marker probe; require the real human Approve/Reject interaction
before dispatch and all live probe gates before C–I. Solkael remains suspended.

## Historical minimal configuration fix

**APPROVAL CONFIG FIXED — RESTART REQUIRED.**
**LIVE OPERATIONS NOT VERIFIED.** No Blender tools were called in this task.
Blender, Solkael, the installed MCP server and all its protections were untouched.

## Observed effective values

The installed desktop executable is Codex0.153.4 at
`C:/Users/olive/AppData/Local/OpenAI/Codex/bin/fd4c151a749f3ab4/codex.exe`.
Technical branch: `chore/blender-mcp-bootstrap-fix`; clean starting commit:
`c4efd683cb500d09c5b4fe9d12887dd76bfdab1e`.

| Setting | Before: resolved disk config | Current already-running task | After: resolved disk config |
| --- | --- | --- | --- |
| approval_policy | never | never | on-request |
| approvals_reviewer | user | user | user |
| Blender default_tools_approval_mode | Unset/null | No additional Blender default override observed | Unset/null, preserved |
| execute_blender_code approval_mode | prompt | prompt in the unchanged configured stanza; resident runtime rule not directly read | prompt, preserved |
| sandbox_mode | danger-full-access | danger-full-access | danger-full-access, preserved |

Null above means the server-level default is not explicitly set in the resolved
configuration, not that every tool requires approval. This audit does not assign
or invent a fallback value; the explicit execute_blender_code rule remains prompt.
Read-only tools and other MCP/app-specific settings were not edited.

An incompatible effective setting was identified: the running task uses `never`,
despite the configured per-tool `prompt` rule. Exact routing causality remains
unverified. The reviewer
was already `user`, not `auto_review`. Changing a disk value does not prove that
an existing task has adopted it, or that the human prompt now works.

## Layer and session evidence

This audit did not rely only on a TOML text search. The installed executable's
generated protocol confirms `config/read` with `includeLayers` and optional `cwd`,
and `configRequirements/read`. A separate, read-only instance of that same
executable was initialized over STDIO with `--strict-config`, then received:

```json
{"id":2,"method":"config/read","params":{"includeLayers":true,"cwd":"D:/Dev/HeroSmash"}}
{"id":3,"method":"config/read","params":{"includeLayers":true,"cwd":"D:/Dev/HeroSmash-mcp-bootstrap-fix"}}
{"id":4,"method":"configRequirements/read"}
```

Both worktree resolutions agree. Returned layers are the user config
`C:/Users/olive/.codex/config.toml`, profile=null, and an empty system layer at
`C:/ProgramData/OpenAI/Codex/config.toml`. All relevant value origins point to the
user layer. No project/profile/enterprise/MDM layer was returned. The system file,
system/user requirements.toml and legacy user managed_config.toml were absent.
`configRequirements/read` returned `requirements:null` before and after the change.
Both diagnostic processes exited0 on stdin EOF; no thread or MCP operation was
sent through them and no desktop process was stopped.

The diagnostics are **not attached to the desktop's existing STDIO connection**.
They establish the installed resolver's disk layers and available requirements.
The actual running task is independently established by its own persisted
turn-context record, rather than mislabeled as the separate process's state:

- Task `01a08635-5f9d-7e41-b4f8-5b4fe17c95b5`, current turn
  `01a08644-fc52-72b0-98be-cc7ec12ed6d6`, timestamp13:04:23.175Z.
- Its rollout line348 records approval_policy=never, approvals_reviewer=user,
  sandbox_policy.type=danger-full-access and permission_profile.type=disabled.
  The previous turn at line8 has the same values.
- The exact task row in read-only state_5.sqlite also records approval_mode=never.
- The app's local mode is full-access. Its saved permission snapshot for this
  task contains never/user and activePermissionProfile.id=:danger-full-access.
  This corroborates saved app/task state; it does not establish override precedence.
- Desktop PID30588 launch flags set code_mode_host and the codex_app MCP entry.
  They contain no approval-policy/reviewer or Blender override. Their unrelated
  settings were not reproduced in a public report or changed.

The actual desktop log shows config/read and configRequirements/read requests,
but their response bodies were not available in the bounded inspection. No
supported local control endpoint for its existing STDIO connection was found.
Therefore no managed restriction was returned by the diagnostic resolver, but
the resident desktop's current managed-policy response is not directly verified.
No managed policy was edited, bypassed or asserted absent solely from missing files.
If a later actual-session read reveals a policy forbidding human prompts, stop
with **POLICY BLOCKED**.

The installed protocol also exposes approval overrides on turn/start and
thread/settings/update. These endpoints were inspected as schemas only, not
called on the active task. The next session must recheck its effective values;
the saved Full Access task/app state may still require attention. Restart alone
is not claimed to guarantee that an app/task override disappears.

## Minimal authorized change and backup

The only modified configuration file is `C:/Users/olive/.codex/config.toml`.
Before writing, a new exclusive backup preserved its exact bytes at:

`D:/Dev/HeroSmash/.work/blender-mcp-smoke/approval-audit-20260909/backups/config-before-human-approval.toml`.

The entire edit was one top-level byte replacement:

```diff
-approval_policy = "never"
+approval_policy = "on-request"
```

`approvals_reviewer="user"` and the Blender per-tool prompt rule were already
present and stayed byte-identical. A parsed before/after comparison proves every
other value unchanged; an exact byte comparison proves no unrelated formatting
change. Concurrent-write guards checked the original bytes before replacement.

| File state | SHA-256 |
| --- | --- |
| Before / backup | e50774e8463d053cfa8b6394580dc38c497437b4ca06a475f81127d18950f511 |
| After | fc0bba693f9d7f508fd400120b613898e26201620061841bf0b49216d54e7dc7 |

Preserved: sandbox, server command, allowlist, telemetry, safe mode, host/port,
timeouts, plugins, accounts and all other MCP/app-specific settings. No installation,
dependency, listener, GUI or production changes occurred. The top-level policy
is the explicitly owner-requested global setting; no per-app/MCP rewrite was added.
Rollback, if requested later, should replace only this field after checking for
subsequent edits, rather than blindly restoring the full personal backup.

## Validation and first probe after owner restart

PASS: TOML parse, exactly-one-field parsed diff, exact-byte backup/comparison,
strict installed-version config resolution for both worktrees, requirements read,
and preservation checks. The actual running task has not been reconfigured.
No Codex restart was performed by this task.

The unchanged installed safe-mode validator statically accepts this exact probe:

```python
print("HS_MCP_APPROVAL_PROBE")
```

This was validation only, with no probe execution and no Blender connection.
After an owner-controlled restart/session refresh, resume **only this collaudo**.
First verify actual-session on-request/user and the tool's prompt rule, including
app/task and managed overrides. The first execute_blender_code call must contain
only the marker probe above: no preference read, filesystem access or object edit.

| Probe requirement | Current result |
| --- | --- |
| A: human prompt before execution | NOT RUN after fix |
| B: user can choose Approve/Reject | NOT RUN |
| C: code dispatched only after approval | NOT RUN |
| D: safe mode accepts actual live request | NOT RUN; static validation only PASS |
| E: actual MCP returns HS_MCP_APPROVAL_PROBE | NOT RUN |

If no prompt appears, stop immediately and collect actual-session configuration.
Only a successful human-approved A–E probe permits the already authorized C–I
suite on the temporary smoke scene. No continuation is automatic.

Current smoke C–I: **not resumed**. C/D/F/G/H remain not run; E retains only the
previous initial viewport and I only the previous unrelated safe-mode rejection.
Those historical partial results are not upgraded by this configuration change.
No new screenshots or artistic assets exist. Solkael remains suspended.

## Evidence and publication

Local evidence is confined to
`D:/Dev/HeroSmash/.work/blender-mcp-smoke/approval-audit-20260909/`:
sanitized config-read-before/after.json, config-change.json,
current-session-evidence.json, preservation.json, read-only diagnostic script and
installed-version generated protocol. Personal backup/config and unrelated
account/log data stay outside Git. No secret or raw full-session log is published.

The original artistic worktree, recorded45 Solkael/127 evidence hashes, main and
tags remain preserved. Art72170ba is excluded. Only this report and integration
status documentation are committed to chore/blender-mcp-bootstrap-fix and Draft
PR3. No merge, force push, tag change or art commit. Documentation whitespace/link
checks and exact published-commit CI are recorded in the task delivery and PR.
No game, production export or repeated server bootstrap tests were run locally.

Official references: [configuration and reviewer/requirements fields](https://learn.chatgpt.com/docs/config-file/config-reference)
and [app-server configuration RPCs](https://learn.chatgpt.com/docs/app-server).
These describe the supported interfaces; local version-generated schemas and
actual returned records establish the observed values above.
