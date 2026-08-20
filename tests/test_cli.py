from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "poland.py"


def run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", str(CLI), *arguments],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
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
        self.assertTrue(payload["citations"])

        protected = self.assert_success_envelope(
            run_cli("channel", "e-tax-office", "--as-of", "2026-08-20"),
            "channel",
        )
        self.assertEqual("authenticated", protected["result"]["access_scope"])
        self.assertFalse(protected["result"]["protected_interaction_supported"])

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


if __name__ == "__main__":
    unittest.main()
