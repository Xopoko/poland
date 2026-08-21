from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "poland.py"


def run_cli(*arguments: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", str(CLI), *arguments],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )


class CliTests(unittest.TestCase):
    def assert_success_envelope(self, result: subprocess.CompletedProcess[str], operation: str):
        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual("poland.response.v1", payload["contract"])
        self.assertTrue(payload["ok"])
        self.assertEqual(operation, payload["command"])
        self.assertEqual("OFFLINE_PACKAGED_DATA", payload["data_mode"])
        self.assertNotIn("error", payload)
        self.assertIn("data_version", payload)
        self.assertIn("as_of", payload)
        return payload

    def test_read_only_commands_return_stable_envelopes(self):
        for operation, arguments in (
            ("overview", ("overview",)),
            ("sources", ("sources", "--query", "112")),
            ("source", ("source", "udsc-home")),
            (
                "channels",
                (
                    "channels",
                    "portal",
                    "--channel-kind",
                    "information_portal",
                    "--access-scope",
                    "public",
                    "--limit",
                    "2",
                    "--as-of",
                    "2026-08-20",
                ),
            ),
            ("channel", ("channel", "bip", "--as-of", "2026-08-20")),
            (
                "route",
                ("route", "health access", "--voivodeship", "mazowieckie", "--as-of", "2026-08-20"),
            ),
            ("checklist", ("checklist", "foreign-document-use", "--as-of", "2026-08-20")),
            ("terms", ("terms", "eZUS")),
            ("regions", ("regions", "Warsaw")),
            ("freshness", ("freshness", "--as-of", "2026-08-20")),
            ("boundary", ("boundary", "submit application")),
        ):
            self.assert_success_envelope(run_cli(*arguments), operation)

    def test_sources_accept_powiat_jurisdiction_filter(self):
        payload = self.assert_success_envelope(
            run_cli("sources", "--jurisdiction", "powiat"),
            "sources",
        )
        self.assertEqual([], payload["result"])

    def test_validate_uses_envelope_even_when_bundle_is_invalid(self):
        result = run_cli("validate", "--as-of", "2026-08-20")
        self.assertIn(result.returncode, {0, 1}, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual("validate", payload["command"])
        self.assertTrue(set(payload["warnings"]).issubset(set(payload["result"]["warnings"])))

    def test_route_citations_and_input_are_not_echoed(self):
        payload = self.assert_success_envelope(
            run_cli(
                "route",
                "health access",
                "--insurance-context",
                "public-insurance",
                "--voivodeship",
                "mazowieckie",
                "--as-of",
                "2026-08-20",
            ),
            "route",
        )
        self.assertTrue(payload["citations"])
        self.assertTrue(all("source_id" in item and "url" in item for item in payload["citations"]))
        self.assertNotIn("matched_query", payload["result"])
        self.assertNotIn("profile", payload)

    def test_sensitive_fact_is_rejected_without_echo(self):
        secret_like = "password=do-not-log-this"
        result = run_cli("route", "health-access", "--matter", secret_like)
        self.assertEqual(2, result.returncode)
        self.assertNotIn(secret_like, result.stderr)
        payload = json.loads(result.stderr)
        self.assertFalse(payload["ok"])
        self.assertEqual("SENSITIVE_INPUT_REJECTED", payload["error"]["code"])
        self.assertNotIn("citations", payload)

    def test_channel_discovery_is_bounded_read_only_and_source_backed(self):
        payload = self.assert_success_envelope(
            run_cli(
                "channels",
                "portal",
                "--channel-kind",
                "information_portal",
                "--access-scope",
                "public",
                "--limit",
                "1",
                "--as-of",
                "2026-08-20",
            ),
            "channels",
        )
        self.assertEqual(1, len(payload["result"]))
        channel = payload["result"][0]
        self.assertEqual("information_portal", channel["channel_kind"])
        self.assertEqual("public", channel["access_scope"])
        self.assertFalse(channel["protected_interaction_supported"])
        self.assertEqual("public_read_only_handoff", channel["channel_state"])
        self.assertFalse(channel["caller_owned_operator_eligible"])
        self.assertFalse(channel["bundled_interface_can_interact"])
        self.assertTrue(payload["citations"])

        protected = self.assert_success_envelope(
            run_cli("channel", "e-tax-office", "--as-of", "2026-08-20"),
            "channel",
        )
        self.assertEqual("authenticated", protected["result"]["access_scope"])
        self.assertFalse(protected["result"]["protected_interaction_supported"])
        self.assertEqual("caller_owned_operator", protected["result"]["channel_state"])
        self.assertTrue(protected["result"]["caller_owned_operator_eligible"])
        self.assertFalse(protected["result"]["bundled_interface_can_interact"])

    def test_sensitive_channel_query_is_rejected_without_echo(self):
        secret_like = "password=do-not-log-this"
        result = run_cli("channels", secret_like)
        self.assertEqual(2, result.returncode)
        self.assertNotIn(secret_like, result.stderr)
        payload = json.loads(result.stderr)
        self.assertEqual("channels", payload["command"])
        self.assertEqual("SENSITIVE_INPUT_REJECTED", payload["error"]["code"])

    def test_case_and_profile_file_surfaces_do_not_exist(self):
        for arguments in (("case", "init", "case.json"), ("route", "health access", "--profile", "case.json")):
            result = run_cli(*arguments)
            self.assertEqual(2, result.returncode)
            payload = json.loads(result.stderr)
            self.assertEqual("INVALID_ARGUMENTS", payload["error"]["code"])
            self.assertNotIn("case.json", result.stderr)

    def test_unknown_source_returns_non_echoing_structured_error(self):
        unknown = "missing-source"
        result = run_cli("source", unknown)
        self.assertEqual(2, result.returncode)
        self.assertNotIn(unknown, result.stderr)
        payload = json.loads(result.stderr)
        self.assertFalse(payload["ok"])
        self.assertIsInstance(payload["error"]["code"], str)

    def test_doctor_returns_path_free_telemetry_free_receipt(self):
        payload = self.assert_success_envelope(
            run_cli("doctor", "--host", "package", "--as-of", "2026-08-21"),
            "doctor",
        )
        receipt = payload["result"]
        self.assertEqual("poland.doctor_receipt.v1", receipt["schema"])
        self.assertRegex(receipt["checked_at_utc"], r"^\d{4}-\d{2}-\d{2}T.*Z$")
        self.assertTrue(receipt["valid"])
        self.assertEqual(33, receipt["package"]["skills"])
        self.assertEqual(33, receipt["package"]["declared_skills"])
        self.assertTrue(receipt["package"]["skill_inventory_aligned"])
        self.assertTrue(receipt["package"]["versions_aligned"])
        self.assertTrue(receipt["checks"]["bundle_validation"]["valid"])
        self.assertEqual(0, receipt["checks"]["bundle_validation"]["error_count"])
        self.assertEqual("passed", receipt["checks"]["bundled_mcp_round_trip"]["status"])
        self.assertEqual(11, receipt["checks"]["bundled_mcp_round_trip"]["tool_count"])
        self.assertEqual(
            "poland_overview",
            receipt["checks"]["bundled_mcp_round_trip"]["read_only_tool_call"],
        )
        self.assertEqual("not_checked", receipt["checks"]["host_plugin_discovery"])
        self.assertFalse(receipt["privacy"]["poland_telemetry_emitted"])
        self.assertFalse(receipt["privacy"]["network_requests_made"])
        self.assertFalse(receipt["runtime"]["python"]["executable_path_disclosed"])
        self.assertEqual("not_checked", receipt["capability"]["host_version"])
        self.assertEqual("not_checked", receipt["capability"]["installation_scope"])
        self.assertIsNone(receipt["capability"]["skills"]["host_loaded_count"])
        strings: list[str] = []

        def collect(value):
            if isinstance(value, str):
                strings.append(value)
            elif isinstance(value, dict):
                for item in value.values():
                    collect(item)
            elif isinstance(value, list):
                for item in value:
                    collect(item)

        collect(receipt)
        for value in strings:
            self.assertNotIn(str(ROOT), value)
            self.assertNotIn(str(Path(sys.executable).parent), value)

    def test_doctor_proves_each_declared_host_component_on_this_runner(self):
        clean_env = os.environ.copy()
        clean_env.pop("POLAND_PYTHON", None)
        for host in ("codex", "claude", "cursor"):
            payload = self.assert_success_envelope(
                run_cli("doctor", "--host", host, "--as-of", "2026-08-21", env=clean_env),
                "doctor",
            )
            receipt = payload["result"]
            self.assertTrue(receipt["valid"], host)
            configured = receipt["checks"]["configured_mcp_round_trip"]
            self.assertEqual("passed", configured["status"], host)
            self.assertEqual(11, configured["tool_count"], host)
            self.assertEqual("passed", configured["launcher"]["status"], host)

        pi = self.assert_success_envelope(
            run_cli("doctor", "--host", "pi", "--as-of", "2026-08-21", env=clean_env),
            "doctor",
        )["result"]
        self.assertEqual(
            "not_declared_by_pi_package",
            pi["capability"]["mcp"]["registration"],
        )
        self.assertEqual("not_applicable", pi["checks"]["configured_mcp_round_trip"]["status"])

    def test_doctor_fails_closed_when_configured_launcher_is_missing(self):
        environment = os.environ.copy()
        environment["POLAND_PYTHON"] = "poland-python-command-that-does-not-exist"
        result = run_cli("doctor", "--host", "claude", "--as-of", "2026-08-21", env=environment)
        self.assertEqual(1, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        receipt = payload["result"]
        self.assertFalse(receipt["valid"])
        self.assertEqual(
            "launcher_not_found",
            receipt["checks"]["configured_mcp_round_trip"]["reason"],
        )
        self.assertNotIn(environment["POLAND_PYTHON"], result.stdout)

    def test_doctor_can_repair_missing_launcher_with_reviewable_local_config(self):
        environment = os.environ.copy()
        environment["POLAND_PYTHON"] = "poland-python-command-that-does-not-exist"
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / ".mcp.json"
            result = run_cli(
                "doctor",
                "--host",
                "claude",
                "--as-of",
                "2026-08-21",
                "--write-mcp-config",
                str(target),
                env=environment,
            )
            receipt = self.assert_success_envelope(result, "doctor")["result"]
            self.assertTrue(receipt["valid"])
            self.assertEqual(
                "launcher_not_found",
                receipt["checks"]["configured_mcp_round_trip"]["reason"],
            )
            self.assertEqual("passed", receipt["checks"]["generated_mcp_round_trip"]["status"])
            self.assertNotIn(environment["POLAND_PYTHON"], result.stdout)
            self.assertNotIn(directory, result.stdout)

    def test_doctor_writes_reviewable_host_local_config_without_path_in_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / ".codex-mcp.json"
            result = run_cli(
                "doctor",
                "--host",
                "cursor",
                "--as-of",
                "2026-08-21",
                "--write-mcp-config",
                str(target),
            )
            payload = self.assert_success_envelope(result, "doctor")
            generated = payload["result"]["generated_mcp_config"]
            self.assertTrue(generated["written"])
            self.assertFalse(generated["commit_safe"])
            self.assertEqual(".codex-mcp.json", generated["filename"])
            self.assertNotIn(directory, result.stdout)
            config = json.loads(target.read_text(encoding="utf-8"))
            server = config["mcpServers"]["poland"]
            self.assertEqual(str(Path(sys.executable).resolve()), server["command"])
            self.assertEqual(["-I", "-B", "./mcp/server.py"], server["args"])

            duplicate = run_cli(
                "doctor",
                "--host",
                "cursor",
                "--write-mcp-config",
                str(target),
            )
            self.assertEqual(2, duplicate.returncode)
            self.assertEqual("OUTPUT_EXISTS", json.loads(duplicate.stderr)["error"]["code"])
            self.assertNotIn(directory, duplicate.stderr)

    def test_doctor_generates_claude_root_aware_companion(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / ".mcp.json"
            result = run_cli(
                "doctor",
                "--host",
                "claude",
                "--write-mcp-config",
                str(target),
            )
            self.assert_success_envelope(result, "doctor")
            server = json.loads(target.read_text(encoding="utf-8"))["mcpServers"]["poland"]
            self.assertEqual(str(Path(sys.executable).resolve()), server["command"])
            self.assertEqual(
                ["-I", "-B", "${CLAUDE_PLUGIN_ROOT}/mcp/server.py"],
                server["args"],
            )
            self.assertEqual("${CLAUDE_PLUGIN_ROOT}", server["cwd"])

    def test_doctor_never_writes_generated_config_into_source(self):
        result = run_cli(
            "doctor",
            "--host",
            "codex",
            "--write-mcp-config",
            str(ROOT / ".codex-mcp.json"),
            "--force",
        )
        self.assertEqual(2, result.returncode)
        self.assertEqual("INVALID_OUTPUT_TARGET", json.loads(result.stderr)["error"]["code"])
        self.assertNotIn(str(ROOT), result.stderr)


if __name__ == "__main__":
    unittest.main()
