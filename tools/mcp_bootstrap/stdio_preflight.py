"""Diagnose a local MCP server over STDIO without invoking any tools.

This is an external protocol diagnostic, never proof that a running Codex session
has discovered the server or can operate Blender. The upstream server may perform
its own read-only Blender handshake during startup, independently of this client.
Only initialize, notifications/initialized and tools/list are initiated here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from typing import Any, BinaryIO


PROTOCOL_VERSION = "2025-11-25"  # Installed MCP SDK 1.30.0's latest version.
EXPECTED_UPSTREAM_TOOL_COUNT = 28
CODEX_ALLOWLIST = frozenset({
    "get_addon_status", "get_scene_info", "get_object_info",
    "get_viewport_screenshot", "execute_blender_code", "disable_telemetry",
})
SAFETY_ENV = {
    "DISABLE_TELEMETRY": "true",
    "BLENDER_MCP_SAFE_MODE": "1",
    "BLENDER_HOST": "127.0.0.1",
    "BLENDER_PORT": "9876",
    "BLENDERMCP_ADDONS_DIR":
        "D:/Dev/Tools/blender-mcp/5f8ddaf6/blender-user-scripts/addons",
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONUTF8": "1",
}
# Explicit OS/runtime inheritance, not a copy of the caller's entire environment.
INHERITED_ENV_NAMES = (
    "APPDATA", "HOMEDRIVE", "HOMEPATH", "LOCALAPPDATA", "PATH", "PATHEXT",
    "PROCESSOR_ARCHITECTURE", "SYSTEMDRIVE", "SYSTEMROOT", "TEMP", "TMP",
    "USERNAME", "USERPROFILE", "COMSPEC", "WINDIR",
)
MAX_JSON_LINE_BYTES = 8 * 1024 * 1024


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def positive_seconds(value: str) -> float:
    seconds = float(value)
    if not 0 < seconds <= 300:
        raise argparse.ArgumentTypeError("timeout must be finite and within (0, 300]")
    return seconds


class ProtocolError(RuntimeError):
    pass


class JsonlClient:
    def __init__(
        self, process: subprocess.Popen[bytes], outgoing_log: BinaryIO,
        incoming_log: BinaryIO, total_deadline: float, request_timeout: float,
    ) -> None:
        self.process = process
        self.outgoing_log = outgoing_log
        self.incoming_log = incoming_log
        self.total_deadline = total_deadline
        self.request_timeout = request_timeout
        self.incoming: queue.Queue[tuple[str, Any]] = queue.Queue()
        self.request_id = 0
        self.sent_methods: list[str] = []
        self.server_requests_rejected: list[str] = []
        self.reader = threading.Thread(
            target=self._read_stdout, name="mcp-stdio-diagnostic-reader", daemon=True,
        )
        self.reader.start()

    def _read_stdout(self) -> None:
        assert self.process.stdout is not None
        try:
            while True:
                line = self.process.stdout.readline(MAX_JSON_LINE_BYTES + 1)
                if not line:
                    self.incoming.put(("eof", None))
                    return
                self.incoming_log.write(line)
                self.incoming_log.flush()
                if len(line) > MAX_JSON_LINE_BYTES:
                    raise ProtocolError("server exceeded the JSONL line size limit")
                message = json.loads(line.decode("utf-8"))
                if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
                    raise ProtocolError("server emitted a non-JSON-RPC message")
                self.incoming.put(("message", message))
        except Exception as exc:
            self.incoming.put(("error", f"{type(exc).__name__}: {exc}"))

    def send(self, message: dict[str, Any]) -> None:
        if time.monotonic() >= self.total_deadline:
            raise TimeoutError("total protocol deadline exceeded")
        method = message.get("method")
        if method is not None:
            if method not in {"initialize", "notifications/initialized", "tools/list"}:
                raise ProtocolError(f"diagnostic must never initiate {method}")
            self.sent_methods.append(method)
        raw = (json.dumps(message, ensure_ascii=False) + "\n").encode("utf-8")
        self.outgoing_log.write(raw)
        self.outgoing_log.flush()
        assert self.process.stdin is not None
        self.process.stdin.write(raw)
        self.process.stdin.flush()

    def request(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self.request_id += 1
        request_id = self.request_id
        message: dict[str, Any] = {"jsonrpc": "2.0", "id": request_id, "method": method}
        if params is not None:
            message["params"] = params
        self.send(message)
        deadline = min(self.total_deadline, time.monotonic() + self.request_timeout)
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f"deadline exceeded waiting for {method}")
            try:
                kind, response = self.incoming.get(timeout=remaining)
            except queue.Empty as exc:
                raise TimeoutError(f"deadline exceeded waiting for {method}") from exc
            if kind == "eof":
                raise ProtocolError(f"server closed stdout before replying to {method}")
            if kind == "error":
                raise ProtocolError(response)
            if "method" in response:
                # No sampling, elicitation, roots or other client capabilities were
                # advertised. Reject unsolicited requests without performing them.
                if "id" in response:
                    requested = str(response["method"])
                    self.server_requests_rejected.append(requested)
                    self.send({
                        "jsonrpc": "2.0", "id": response["id"],
                        "error": {"code": -32601,
                                  "message": "Diagnostic client has no such capability"},
                    })
                continue
            if response.get("id") != request_id:
                raise ProtocolError("unexpected response ID with only one request outstanding")
            if "error" in response:
                raise ProtocolError(f"{method} returned {json.dumps(response['error'])}")
            result = response.get("result")
            if not isinstance(result, dict):
                raise ProtocolError(f"{method} did not return an object result")
            return result


def shutdown(process: subprocess.Popen[bytes], timeout: float) -> dict[str, Any]:
    result: dict[str, Any] = {"stdin_closed": False, "forced_cleanup": False}
    try:
        if process.stdin is not None:
            process.stdin.close()
        result["stdin_closed"] = True
    except OSError as exc:
        result["stdin_close_error"] = str(exc)
    try:
        result["exit_code"] = process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        result["forced_cleanup"] = True
        result["graceful_timeout_seconds"] = timeout
        if os.name == "nt":
            # Only the process tree we just launched; never a port-based lookup or
            # unrelated Blender/Codex process. A forced exit is always a failed gate.
            taskkill = Path(os.environ.get("SYSTEMROOT", "C:/Windows")) / "System32/taskkill.exe"
            try:
                cleanup = subprocess.run(
                    [str(taskkill), "/PID", str(process.pid), "/T", "/F"],
                    capture_output=True, timeout=timeout, check=False,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
                result["tree_cleanup_exit_code"] = cleanup.returncode
            except (OSError, subprocess.TimeoutExpired) as exc:
                result["tree_cleanup_error"] = f"{type(exc).__name__}: {exc}"
        if process.poll() is None:
            process.kill()
        try:
            result["exit_code"] = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            result["exit_code"] = None
            result["process_still_running"] = True
    result["graceful"] = (
        result["stdin_closed"] and not result["forced_cleanup"]
        and result.get("exit_code") == 0
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--command", required=True, type=Path,
                        help="Absolute executable path; no shell and no implicit updater")
    parser.add_argument("--output-dir", required=True, type=Path,
                        help="Local diagnostics directory; existing diagnostic files are preserved")
    parser.add_argument("--request-timeout", type=positive_seconds, default=15.0)
    parser.add_argument("--total-timeout", type=positive_seconds, default=60.0,
                        help="Total protocol deadline, followed by bounded process cleanup")
    parser.add_argument("--shutdown-timeout", type=positive_seconds, default=5.0)
    args = parser.parse_args()
    if not args.command.is_absolute() or not args.command.is_file():
        parser.error("--command must identify an existing absolute executable path")
    if not args.output_dir.is_absolute():
        parser.error("--output-dir must be absolute")
    command = args.command.resolve(strict=True)
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    paths = {key: output / filename for key, filename in {
        "report": "stdio-preflight.json", "stderr": "stderr.log",
        "incoming": "server-stdout.jsonl", "outgoing": "client-stdin.jsonl",
        "catalog": "upstream-tool-catalog.json",
    }.items()}
    occupied = [str(path) for path in paths.values() if path.exists()]
    if occupied:
        parser.error("choose a fresh output directory; diagnostics already exist: " + ", ".join(occupied))
    environment = {key: os.environ[key] for key in INHERITED_ENV_NAMES if key in os.environ}
    environment.update(SAFETY_ENV)
    started = time.monotonic()
    report: dict[str, Any] = {
        "kind": "external-diagnostic-stdio-only",
        "started_at": utc_now(), "status": "FAIL",
        "session_tools_discovered": "NOT TESTED",
        "live_operations_verified": "NOT TESTED",
        "tools_call_count": 0,
        "scope": "Protocol bootstrap only; upstream may perform its own Blender startup handshake",
        "launch": {
            "command": str(command), "args": [], "cwd": str(output), "transport": "stdio",
            "explicit_environment": SAFETY_ENV,
            "inherited_environment_names": sorted(set(environment) - set(SAFETY_ENV)),
            "environment_note": "Launch inputs, not an independent read of the child environment",
        },
        "timeouts_seconds": {
            "request": args.request_timeout, "total_protocol": args.total_timeout,
            "shutdown_per_stage": args.shutdown_timeout,
        },
        "files": {key: str(path) for key, path in paths.items()},
        "codex_allowlist_expected": sorted(CODEX_ALLOWLIST),
        "allowlist_note": "Codex filters tools separately; this diagnostic sees the upstream catalog",
    }
    process: subprocess.Popen[bytes] | None = None
    client: JsonlClient | None = None
    try:
        with (
            paths["stderr"].open("xb") as stderr,
            paths["incoming"].open("xb") as incoming,
            paths["outgoing"].open("xb") as outgoing,
        ):
            try:
                process = subprocess.Popen(
                    [str(command)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                    stderr=stderr, cwd=output, env=environment,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
                report["server_command_pid"] = process.pid
                report["pid_note"] = "PID of the launched STDIO command (a launcher may have a Python child)"
                client = JsonlClient(process, outgoing, incoming,
                                     started + args.total_timeout, args.request_timeout)
                initialized = client.request("initialize", {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {},
                    "clientInfo": {"name": "hero-smash-stdio-preflight", "version": "1.0"},
                })
                report["initialize_result"] = initialized
                if initialized.get("protocolVersion") != PROTOCOL_VERSION:
                    raise ProtocolError("server did not negotiate the expected protocol version")
                if not isinstance(initialized.get("capabilities", {}).get("tools"), dict):
                    raise ProtocolError("server did not advertise the tools capability")
                client.send({"jsonrpc": "2.0", "method": "notifications/initialized"})
                report["initialized_notification_sent"] = True
                tools: list[dict[str, Any]] = []
                cursor: str | None = None
                for page_number in range(1, 6):
                    page = client.request("tools/list", {"cursor": cursor} if cursor else None)
                    page_tools = page.get("tools")
                    if not isinstance(page_tools, list) or not all(isinstance(t, dict) for t in page_tools):
                        raise ProtocolError("tools/list returned an invalid tools array")
                    tools.extend(page_tools)
                    cursor = page.get("nextCursor")
                    if not cursor:
                        break
                    if not isinstance(cursor, str):
                        raise ProtocolError("tools/list returned an invalid cursor")
                else:
                    raise ProtocolError("tools/list exceeded the five-page diagnostic limit")
                names = [tool.get("name") for tool in tools]
                if not all(isinstance(name, str) and name for name in names):
                    raise ProtocolError("tool catalog contains an invalid name")
                serialized = json.dumps(tools, indent=2, ensure_ascii=False).encode("utf-8")
                paths["catalog"].write_bytes(serialized)
                report["catalog"] = {
                    "count": len(tools), "expected_upstream_count": EXPECTED_UPSTREAM_TOOL_COUNT,
                    "pages": page_number, "names": sorted(names),
                    "sha256": hashlib.sha256(serialized).hexdigest(),
                    "required_codex_tools_present": CODEX_ALLOWLIST.issubset(names),
                    "duplicate_names": len(set(names)) != len(names),
                }
                if (len(tools) != EXPECTED_UPSTREAM_TOOL_COUNT
                        or not CODEX_ALLOWLIST.issubset(names)
                        or len(set(names)) != len(names)):
                    raise ProtocolError("upstream catalog does not satisfy the pinned-server expectations")
                report["protocol_check"] = "PASS"
            except Exception as exc:
                report["protocol_check"] = "FAIL"
                report["error"] = f"{type(exc).__name__}: {exc}"
            finally:
                if process is not None:
                    report["shutdown"] = shutdown(process, args.shutdown_timeout)
                if client is not None:
                    client.reader.join(timeout=args.shutdown_timeout)
                    report["stdout_reader_finished"] = not client.reader.is_alive()
                    report["sent_methods"] = client.sent_methods
                    report["server_requests_rejected"] = client.server_requests_rejected
                    report["tools_call_count"] = client.sent_methods.count("tools/call")
                if process is not None and process.stdout is not None and not (
                    client is not None and client.reader.is_alive()
                ):
                    process.stdout.close()
    except Exception as exc:
        report["diagnostic_error"] = f"{type(exc).__name__}: {exc}"
    report["finished_at"] = utc_now()
    report["elapsed_seconds"] = round(time.monotonic() - started, 3)
    if (report.get("protocol_check") == "PASS"
            and report.get("shutdown", {}).get("graceful") is True
            and report.get("stdout_reader_finished") is True
            and report["tools_call_count"] == 0):
        report["status"] = "PASS"
    paths["report"].write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"status": report["status"], "report": str(paths["report"])}))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
