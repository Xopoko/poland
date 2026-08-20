from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "poland.py"
SERVER_PATH = ROOT / "mcp" / "server.py"
sys.path.insert(0, str(ROOT / "lib"))

from poland_core import citations_for  # noqa: E402


SPEC = importlib.util.spec_from_file_location("poland_mcp_parity_server", SERVER_PATH)
SERVER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(SERVER)


def cli_envelope(*arguments: str):
    completed = subprocess.run(
        [sys.executable, "-B", str(CLI), *arguments],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=10,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return json.loads(completed.stdout)


def mcp_envelope(name: str, arguments: dict):
    response = SERVER.response_for(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        }
    )
    if "error" in response:
        raise AssertionError(response["error"])
    return response["result"]["structuredContent"]


class InterfaceParityTests(unittest.TestCase):
    def test_overview_envelope_parity(self):
        self.assertEqual(cli_envelope("overview"), mcp_envelope("poland_overview", {}))

    def test_route_result_and_citation_parity(self):
        cli = cli_envelope("route", "health access", "--as-of", "2026-08-20")
        mcp = mcp_envelope(
            "poland_route_scenario",
            {"query": "health access", "as_of": "2026-08-20"},
        )
        self.assertEqual(cli, mcp)
        self.assertEqual(cli["result"], mcp["result"])
        self.assertEqual(cli["citations"], mcp["citations"])
        self.assertEqual(citations_for(cli["result"]), cli["citations"])

    def test_channel_search_result_and_citation_parity(self):
        cli = cli_envelope(
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
        )
        mcp = mcp_envelope(
            "poland_search_channels",
            {
                "query": "portal",
                "channel_kind": "information_portal",
                "access_scope": "public",
                "limit": 2,
                "as_of": "2026-08-20",
            },
        )
        self.assertEqual(cli, mcp)
        self.assertEqual(citations_for(cli["result"]), cli["citations"])

    def test_get_channel_result_and_citation_parity(self):
        cli = cli_envelope("channel", "e-tax-office", "--as-of", "2026-08-20")
        mcp = mcp_envelope(
            "poland_get_channel",
            {"channel_id": "e-tax-office", "as_of": "2026-08-20"},
        )
        self.assertEqual(cli, mcp)
        self.assertEqual(citations_for(cli["result"]), cli["citations"])


if __name__ == "__main__":
    unittest.main()
