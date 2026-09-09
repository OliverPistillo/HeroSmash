"""Local unit regressions for the installed Hero Smash telemetry patch.

Run with the dedicated installation's Python, for example:
  <venv>/Scripts/python.exe tools/mcp_bootstrap/test_telemetry_disabled.py -v

Only the standard-library unittest framework is required. The tested package and
its existing dependencies must be installed in that interpreter. Real decorated
server functions are exercised with a strict, entirely simulated Blender
transport. These tests are NOT live MCP, Blender GUI, or general network-isolation
evidence. In particular, the harmless Python example is never executed in Blender.
"""

from __future__ import annotations

import asyncio
import base64
import builtins
from collections import deque
from contextlib import ExitStack, contextmanager
from dataclasses import FrozenInstanceError
import json
import os
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import AsyncMock, patch

import httpx
from blender_mcp import consent_prompt, server, telemetry, telemetry_decorator
from blender_mcp import trajectory


DISABLE_KEYS = (
    "DISABLE_TELEMETRY",
    "BLENDER_MCP_DISABLE_TELEMETRY",
    "MCP_DISABLE_TELEMETRY",
)
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a"
    "w4sAAAAASUVORK5CYII="
)
GOAL = "Verify only the local telemetry-disabled unit regression."


class StrictBlenderTransport:
    """Every expected command and parameter must be explicitly listed by a test."""

    def __init__(self):
        self.expected = deque()
        self.calls = []
        self.unexpected = []

    def expect(self, command, params=None, result=None):
        self.expected.append((command, params, result))

    def send_command(self, command, params=None):
        self.calls.append((command, params))
        if not self.expected:
            self.unexpected.append((command, params))
            raise AssertionError(f"Unexpected simulated Blender command: {command}")
        expected_command, expected_params, result = self.expected.popleft()
        params_match = expected_params(params) if callable(expected_params) else params == expected_params
        if command != expected_command or not params_match:
            self.unexpected.append((command, params))
            raise AssertionError(
                f"Expected {expected_command!r}/{expected_params!r}; got {command!r}/{params!r}"
            )
        if isinstance(result, BaseException):
            raise result
        if callable(result):
            return result(params)
        return result


class DisabledTelemetryTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.dict(os.environ, {
            **{key: "" for key in DISABLE_KEYS},
            "DISABLE_TELEMETRY": "true",
            "BLENDER_MCP_SAFE_MODE": "1",
        }))
        self.stack.enter_context(patch.object(telemetry, "_telemetry_collector", None))
        self.stack.enter_context(patch.object(trajectory, "_trajectory_recorder", None))
        self.stack.enter_context(patch.object(server, "_addon_handshake", None))
        self.stack.enter_context(patch.object(server, "_addon_handshake_checked", False))
        self.transport = StrictBlenderTransport()
        self.connection = self.stack.enter_context(
            patch.object(server, "get_blender_connection", return_value=self.transport)
        )
        self.http_attempts = {}
        for label, target in (
            ("httpx.post", patch.object(httpx, "post")),
            ("httpx.Client.send", patch.object(httpx.Client, "send")),
            ("httpx.AsyncClient.send", patch.object(httpx.AsyncClient, "send", new_callable=AsyncMock)),
            ("trajectory._post_row", patch.object(trajectory.TrajectoryRecorder, "_post_row")),
        ):
            instrument = self.stack.enter_context(target)
            instrument.side_effect = AssertionError(f"Unexpected telemetry attempt: {label}")
            self.http_attempts[label] = instrument

    def tearDown(self):
        self.assertEqual(self.transport.unexpected, [], "An unexpected Blender command was attempted")
        self.assertEqual(list(self.transport.expected), [], "Expected simulated commands were not consumed")
        for label, instrument in self.http_attempts.items():
            self.assertEqual(instrument.call_count, 0, label)

    @contextmanager
    def no_collection_side_effects(self):
        """Count blocked attempts even if upstream best-effort handlers catch them."""
        instruments = []
        with ExitStack() as stack:
            for label, target in (
                ("UUID persistence", patch.object(telemetry.TelemetryCollector, "_get_or_create_uuid")),
                ("telemetry directory", patch.object(telemetry.TelemetryCollector, "_get_data_directory")),
                ("UUID generation", patch.object(telemetry.uuid, "uuid4")),
                ("worker start", patch.object(telemetry.threading.Thread, "start")),
                ("queue construction", patch.object(telemetry.queue, "Queue")),
                ("filesystem mkdir", patch.object(Path, "mkdir")),
                ("filesystem read_text", patch.object(Path, "read_text")),
                ("filesystem write_text", patch.object(Path, "write_text")),
                ("consent state read", patch.object(consent_prompt, "_read_state")),
                ("consent state write", patch.object(consent_prompt, "_write_state")),
            ):
                instrument = stack.enter_context(target)
                instrument.side_effect = AssertionError(f"Unexpected collection activity: {label}")
                instruments.append((label, instrument))
            yield
            for label, instrument in instruments:
                self.assertEqual(instrument.call_count, 0, label)

    @contextmanager
    def intercept_optional_config(self, exception):
        """Intercept only this package's relative config import, not all imports."""
        original_import = builtins.__import__
        attempts = []

        def import_guard(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "config" and level == 1 and (globals or {}).get("__package__") == "blender_mcp":
                attempts.append((name, fromlist, level))
                raise exception
            return original_import(name, globals, locals, fromlist, level)

        with patch.object(builtins, "__import__", side_effect=import_guard):
            yield attempts

    def test_all_existing_disable_flags_skip_optional_config_and_collection_setup(self):
        for key in DISABLE_KEYS:
            for value in ("true", "1", "yes", "on", "TRUE"):
                with self.subTest(key=key, value=value):
                    with patch.dict(os.environ, {**{item: "" for item in DISABLE_KEYS}, key: value}):
                        with self.no_collection_side_effects():
                            with self.intercept_optional_config(AssertionError("Must not import config")) as attempts:
                                collector = telemetry.TelemetryCollector()
                                self.assertIs(collector.config.enabled, False)
                                collector.record_event(telemetry.EventType.STARTUP)
                                self.assertEqual(collector.upload_screenshot(PNG, "unit"), "")
                            self.assertEqual(attempts, [])

    def test_disabled_configuration_is_immutable(self):
        collector = telemetry.get_telemetry()
        self.assertIs(collector.config.enabled, False)
        with self.assertRaises(FrozenInstanceError):
            collector.config.enabled = True
        self.assertFalse(telemetry.is_telemetry_enabled())

    def test_absent_and_false_flags_fail_closed_when_config_is_missing(self):
        for value in (None, "false", "0"):
            with self.subTest(value=value):
                with patch.dict(os.environ):
                    for key in DISABLE_KEYS:
                        os.environ.pop(key, None)
                    if value is not None:
                        os.environ["DISABLE_TELEMETRY"] = value
                    missing = ModuleNotFoundError("No module named 'blender_mcp.config'", name="blender_mcp.config")
                    with self.no_collection_side_effects():
                        with self.intercept_optional_config(missing) as attempts:
                            with self.assertLogs("blender-mcp-telemetry", level="WARNING") as messages:
                                collector = telemetry.TelemetryCollector()
                            self.assertIs(collector.config.enabled, False)
                            self.assertEqual(len(attempts), 1)
                            self.assertTrue(any("config" in message.lower() for message in messages.output))
                            collector.record_event(telemetry.EventType.STARTUP)
                            self.assertEqual(collector.upload_screenshot(PNG, "unit"), "")

    def test_malformed_or_nested_configuration_errors_are_not_silently_swallowed(self):
        errors = (
            SyntaxError("Malformed optional configuration"),
            ModuleNotFoundError("Missing dependency inside config", name="unit_nested_dependency"),
            ImportError("Configuration does not export telemetry_config"),
        )
        for error in errors:
            with self.subTest(error=type(error).__name__):
                with patch.dict(os.environ, {key: "false" for key in DISABLE_KEYS}):
                    with self.no_collection_side_effects():
                        with self.intercept_optional_config(error):
                            with self.assertRaises(type(error)) as caught:
                                telemetry.TelemetryCollector()
                            self.assertIs(caught.exception, error)

    def test_real_consent_values_cache_and_invalidation_remain_available(self):
        collector = telemetry.get_telemetry()
        self.transport.expect("get_telemetry_consent", result={"consent": False})
        self.assertIs(collector.check_user_consent(), False)
        self.assertIs(collector.check_user_consent(), False)
        self.assertEqual(len(self.transport.calls), 1)
        collector.invalidate_consent_cache()
        self.transport.expect("get_telemetry_consent", result={"consent": True})
        self.assertIs(collector.check_user_consent(), True)
        self.assertTrue(collector._check_user_consent())
        self.assertEqual(len(self.transport.calls), 2)
        collector.invalidate_consent_cache()
        self.transport.expect("get_telemetry_consent", result=ConnectionError("Unit transport unavailable"))
        self.assertIsNone(collector.check_user_consent())
        self.assertIs(collector.config.enabled, False, "Observed consent must never enable telemetry")

    def test_disabled_consent_prompt_never_elicits_or_reads_writes_state(self):
        context = types.SimpleNamespace(
            request_context=types.SimpleNamespace(session=object()),
            elicit=AsyncMock(side_effect=AssertionError("Must not ask to re-enable disabled telemetry")),
        )
        with self.no_collection_side_effects():
            self.assertEqual(asyncio.run(consent_prompt.maybe_prompt_for_consent(context)), "")
        context.elicit.assert_not_called()
        self.connection.assert_not_called()

    def test_recorders_and_uploads_are_noops_including_shutdown_and_private_sender(self):
        with self.no_collection_side_effects():
            collector = telemetry.get_telemetry()
            recorder = trajectory.get_trajectory_recorder()
            self.assertIs(recorder, trajectory.get_trajectory_recorder())
            self.assertFalse(recorder._can_write())
            recorder.note_client("unit-client", "1")
            recorder.note_goal(GOAL)
            recorder.note_agent_observation(modality="scene_info", tool_name="get_scene_info", summary={})
            self.assertIsNone(recorder.snapshot_world_state())
            self.assertIsNone(recorder.maybe_auto_capture({"objects_added": ["unit"]}))
            self.assertEqual(recorder.drain_human_activity(), 0)
            self.assertFalse(recorder.record_step(tool_name="execute_blender_code", raw_code="unit"))
            self.assertFalse(recorder.record_observe_step(tool_name="get_scene_info", modality="scene_info"))
            self.assertFalse(recorder.record_feedback(feedback="accept"))
            self.assertFalse(recorder.close_episode("session_end"))
            self.assertTrue(recorder.flush(0.01))
            telemetry.record_startup()
            telemetry.record_tool_usage("unit", True, 0.01)
            event = telemetry.TelemetryEvent(
                telemetry.EventType.STARTUP, "unit-customer", "unit-session", 0.0, "unit", "unit"
            )
            collector._send_event(event)
            self.assertEqual(collector.upload_screenshot(PNG, "unit"), "")
        self.connection.assert_not_called()

    def test_get_addon_status_real_function_returns_handshake_and_actual_consent(self):
        self.transport.expect("get_addon_info", result={
            "protocol_version": 5,
            "addon_version": [1, 6],
            "capabilities": ["get_scene_info", "execute_code"],
            "blender_version": "5.2.1",
        })
        self.transport.expect("get_telemetry_consent", result={"consent": False})
        with self.no_collection_side_effects():
            result = asyncio.run(server.get_addon_status(ctx=None, user_prompt=GOAL))
        payload = json.loads(result)
        self.assertTrue(payload["up_to_date"])
        self.assertEqual(payload["protocol_version"], 5)
        self.assertEqual(payload["addon_version"], [1, 6])
        self.assertIs(payload["telemetry_consent"], False)

    def test_get_scene_info_real_decorated_function_preserves_transport_result(self):
        expected = {"name": "HS_MCP_UNIT_ONLY", "object_count": 1, "objects": [{"name": "unit"}]}
        self.transport.expect("get_scene_info", result=expected)
        with self.no_collection_side_effects():
            result = asyncio.run(server.get_scene_info(ctx=None, user_prompt=GOAL))
        self.assertEqual(json.loads(result), expected)

    def test_get_object_info_real_decorated_function_preserves_transform(self):
        expected = {"name": "unit", "type": "MESH", "location": [1.0, 2.0, 3.0]}
        self.transport.expect("get_object_info", {"name": "unit"}, expected)
        with self.no_collection_side_effects():
            result = asyncio.run(server.get_object_info(ctx=None, object_name="unit", user_prompt=GOAL))
        self.assertEqual(json.loads(result), expected)

    def test_viewport_tool_returns_simulated_fixture_image_without_upload(self):
        with tempfile.TemporaryDirectory(prefix="hs-mcp-unit-") as directory:
            expected_path = os.path.join(directory, f"blender_screenshot_{os.getpid()}.png")

            def fixture_result(params):
                # Test fixture only: no Blender, screenshot capture or telemetry I/O.
                with open(params["filepath"], "wb") as handle:
                    handle.write(PNG)
                return {"success": True}

            self.transport.expect("get_viewport_screenshot", {
                "max_size": 64, "filepath": expected_path, "format": "png",
            }, fixture_result)
            # Upstream screenshot handling separately reads actual add-on consent.
            # Even True must not upload while collection is globally disabled.
            self.transport.expect("get_telemetry_consent", result={"consent": True})
            with patch.object(server.tempfile, "gettempdir", return_value=directory):
                with self.no_collection_side_effects():
                    result = server.get_viewport_screenshot(ctx=None, max_size=64, user_prompt=GOAL)
            self.assertEqual(result.data, PNG)
            self.assertFalse(Path(expected_path).exists(), "Fixture should follow normal screenshot cleanup")

    def test_disable_telemetry_real_function_applies_optout_and_refreshes_cache(self):
        collector = telemetry.get_telemetry()
        self.transport.expect("get_telemetry_consent", result={"consent": True})
        self.assertIs(collector.check_user_consent(), True)
        self.transport.expect("set_telemetry_consent", {"consent": False}, {"consent": False})
        with self.no_collection_side_effects():
            result = server.disable_telemetry(ctx=None, user_prompt=GOAL)
        self.assertIn("Data collection is now OFF", result)
        self.transport.expect("get_telemetry_consent", result={"consent": False})
        self.assertIs(collector.check_user_consent(), False)

    def test_execute_function_passes_harmless_code_to_fake_transport_only(self):
        code = "import bpy\nprint('HS_MCP_LOCAL_UNIT_ONLY')"
        self.transport.expect("execute_code", {"code": code}, {"result": "HS_MCP_LOCAL_UNIT_ONLY"})
        with self.no_collection_side_effects():
            result = asyncio.run(server.execute_blender_code(ctx=None, code=code, user_prompt=GOAL))
        self.assertIn("Code executed successfully", result)
        self.assertEqual(self.transport.calls, [("execute_code", {"code": code})])

    def test_safe_mode_rejection_never_dispatches_execute_code(self):
        with self.no_collection_side_effects():
            result = asyncio.run(server.execute_blender_code(ctx=None, code="import os", user_prompt=GOAL))
        self.assertIn("Rejected by safe mode", result)
        self.assertIn("BLENDER_MCP_SAFE_MODE", result)
        self.connection.assert_not_called()

    def test_sync_async_decorators_preserve_values_and_exceptions(self):
        for decorator in (
            telemetry_decorator.telemetry_tool,
            telemetry_decorator.rich_telemetry_tool,
            telemetry_decorator.trajectory_tool,
        ):
            with self.subTest(decorator=decorator.__name__):
                sentinel = {"actual_tool_result": object()}
                failure = RuntimeError("Unit operation failure must propagate")

                def sync_success(**kwargs):
                    return sentinel

                async def async_success(**kwargs):
                    return sentinel

                def sync_failure(**kwargs):
                    raise failure

                async def async_failure(**kwargs):
                    raise failure

                with self.no_collection_side_effects():
                    self.assertIs(decorator("unit")(sync_success)(user_prompt=GOAL), sentinel)
                    self.assertIs(asyncio.run(decorator("unit")(async_success)(user_prompt=GOAL)), sentinel)
                    with self.assertRaises(RuntimeError) as caught:
                        decorator("unit")(sync_failure)(user_prompt=GOAL)
                    self.assertIs(caught.exception, failure)
                    with self.assertRaises(RuntimeError) as caught:
                        asyncio.run(decorator("unit")(async_failure)(user_prompt=GOAL))
                    self.assertIs(caught.exception, failure)


if __name__ == "__main__":
    unittest.main()
