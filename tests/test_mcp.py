from __future__ import annotations

import importlib.util
import ast
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVER_PATH = ROOT / "mcp" / "server.py"
SPEC = importlib.util.spec_from_file_location("poland_mcp_server", SERVER_PATH)
SERVER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(SERVER)


class McpTests(unittest.TestCase):
    def request(self, method, params=None, request_id=1):
        payload = {"jsonrpc": "2.0", "id": request_id, "method": method}
        if params is not None:
            payload["params"] = params
        return SERVER.response_for(payload)

    def call(self, name, arguments=None):
        return self.request(
            "tools/call",
            {"name": name, "arguments": arguments or {}},
        )

    def test_initialize_and_read_only_tool_inventory(self):
        initialized = self.request("initialize")
        self.assertEqual("2025-06-18", initialized["result"]["protocolVersion"])
        self.assertIn("Never authenticate", initialized["result"]["instructions"])
        listed = self.request("tools/list")
        tools = listed["result"]["tools"]
        names = {item["name"] for item in tools}
        self.assertEqual(
            {
                "poland_action_boundary",
                "poland_build_checklist",
                "poland_freshness_report",
                "poland_get_channel",
                "poland_get_source",
                "poland_list_regions",
                "poland_lookup_term",
                "poland_overview",
                "poland_route_scenario",
                "poland_search_channels",
                "poland_search_sources",
            },
            names,
        )
        self.assertNotIn("poland_validate_case", names)
        self.assertTrue(all(item["annotations"]["readOnlyHint"] for item in tools))
        self.assertTrue(all(not item["annotations"]["openWorldHint"] for item in tools))
        self.assertTrue(all(item["inputSchema"]["additionalProperties"] is False for item in tools))

    def test_profile_schema_is_closed_at_both_levels(self):
        tool = SERVER.TOOLS["poland_route_scenario"]
        profile = tool["inputSchema"]["properties"]["profile"]
        facts = profile["properties"]["facts"]
        self.assertFalse(profile["additionalProperties"])
        self.assertFalse(facts["additionalProperties"])
        self.assertIn("citizenship_group", facts["properties"])
        self.assertNotIn("passport_number", facts["properties"])

    def test_tool_result_uses_contract_envelope_and_citations(self):
        result = self.call("poland_get_source", {"source_id": "udsc-home"})["result"]
        envelope = result["structuredContent"]
        self.assertEqual("poland.response.v1", envelope["contract"])
        self.assertTrue(envelope["ok"])
        self.assertEqual("source", envelope["command"])
        self.assertEqual("udsc-home", envelope["result"]["id"])
        self.assertEqual("udsc-home", envelope["citations"][0]["source_id"])
        self.assertEqual("text", result["content"][0]["type"])
        self.assertEqual(envelope, json.loads(result["content"][0]["text"]))

    def test_channel_tools_are_closed_bounded_and_source_backed(self):
        search_schema = SERVER.TOOLS["poland_search_channels"]["inputSchema"]
        self.assertFalse(search_schema["additionalProperties"])
        self.assertEqual(100, search_schema["properties"]["limit"]["maximum"])
        self.assertEqual(
            ["authenticated", "credentialed_api", "mixed", "public"],
            search_schema["properties"]["access_scope"]["enum"],
        )

        search = self.call(
            "poland_search_channels",
            {
                "query": "portal",
                "channel_kind": "information_portal",
                "access_scope": "public",
                "limit": 1,
                "as_of": "2026-08-20",
            },
        )["result"]["structuredContent"]
        self.assertEqual("channels", search["command"])
        self.assertEqual(1, len(search["result"]))
        self.assertFalse(search["result"][0]["protected_interaction_supported"])
        self.assertEqual("public_read_only_handoff", search["result"][0]["channel_state"])
        self.assertFalse(search["result"][0]["caller_owned_operator_eligible"])
        self.assertFalse(search["result"][0]["bundled_interface_can_interact"])
        self.assertTrue(search["citations"])

        channel = self.call(
            "poland_get_channel",
            {"channel_id": "e-tax-office", "as_of": "2026-08-20"},
        )["result"]["structuredContent"]
        self.assertEqual("channel", channel["command"])
        self.assertEqual("e-tax-office", channel["result"]["id"])
        self.assertEqual("authenticated", channel["result"]["access_scope"])
        self.assertFalse(channel["result"]["protected_interaction_supported"])
        self.assertEqual("caller_owned_operator", channel["result"]["channel_state"])
        self.assertTrue(channel["result"]["caller_owned_operator_eligible"])
        self.assertFalse(channel["result"]["bundled_interface_can_interact"])

    def test_sensitive_channel_query_fails_without_echo(self):
        secret_like = "password=do-not-log-this"
        response = self.call("poland_search_channels", {"query": secret_like})
        self.assertEqual(-32602, response["error"]["code"])
        self.assertEqual("channels", response["error"]["data"]["command"])
        self.assertEqual(
            "SENSITIVE_INPUT_REJECTED",
            response["error"]["data"]["error"]["code"],
        )
        self.assertNotIn(secret_like, json.dumps(response))

    def test_sensitive_and_unknown_profile_inputs_fail_without_echo(self):
        secret_like = "password=do-not-log-this"
        sensitive = self.call(
            "poland_route_scenario",
            {"query": "health-access", "profile": {"facts": {"matter": secret_like}}},
        )
        self.assertEqual(-32602, sensitive["error"]["code"])
        self.assertEqual(
            "SENSITIVE_INPUT_REJECTED",
            sensitive["error"]["data"]["error"]["code"],
        )
        self.assertNotIn(secret_like, json.dumps(sensitive))

        unsupported = self.call(
            "poland_route_scenario",
            {"query": "health access", "profile": {"facts": {"passport_number": "redacted"}}},
        )
        self.assertEqual(-32602, unsupported["error"]["code"])
        self.assertEqual("UNSUPPORTED_FIELD", unsupported["error"]["data"]["error"]["code"])
        self.assertNotIn("passport_number", json.dumps(unsupported))

    def test_wrong_types_and_unknown_fields_are_invalid_params(self):
        wrong_type = self.call("poland_route_scenario", {"query": 123})
        self.assertEqual(-32602, wrong_type["error"]["code"])
        self.assertEqual("INVALID_ARGUMENTS", wrong_type["error"]["data"]["error"]["code"])

        unknown = self.call("poland_overview", {"extra": True})
        self.assertEqual(-32602, unknown["error"]["code"])
        self.assertEqual("UNSUPPORTED_FIELD", unknown["error"]["data"]["error"]["code"])
        self.assertEqual(-32600, SERVER.response_for([])["error"]["code"])

    def test_notifications_errors_and_output_limit(self):
        self.assertIsNone(SERVER.response_for({"jsonrpc": "2.0", "method": "notifications/initialized"}))
        self.assertEqual(-32601, self.request("unknown")["error"]["code"])
        self.assertLess(SERVER.MAX_TOOL_RESULT_BYTES, SERVER.MAX_FRAME_BYTES)
        with self.assertRaises(__import__("poland_core").PolandDataError) as caught:
            SERVER.tool_result(
                SERVER.response_envelope(
                    "overview",
                    {"payload": "x" * SERVER.MAX_TOOL_RESULT_BYTES},
                    as_of="2026-08-20",
                )
            )
        self.assertEqual("OUTPUT_TOO_LARGE", caught.exception.code)

    def test_stdio_server_handles_multiple_frames(self):
        messages = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "poland_list_regions", "arguments": {"query": "Warsaw"}},
            },
        ]
        completed = subprocess.run(
            [sys.executable, "-B", str(SERVER_PATH)],
            input="".join(json.dumps(item) + "\n" for item in messages),
            text=True,
            capture_output=True,
            cwd=ROOT,
            timeout=10,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        responses = [json.loads(line) for line in completed.stdout.splitlines()]
        self.assertEqual([1, 2, 3], [item["id"] for item in responses])
        self.assertEqual(
            "poland.response.v1",
            responses[-1]["result"]["structuredContent"]["contract"],
        )

    def test_server_imports_no_network_process_or_write_runtime(self):
        source = SERVER_PATH.read_text(encoding="utf-8")
        for forbidden in ("urllib", "subprocess", "requests", "socket", "open(", "write_text", "write_bytes"):
            self.assertNotIn(forbidden, source)

    def test_transitive_core_has_no_network_process_or_write_capability(self):
        for path in (ROOT / "lib" / "poland_core.py", ROOT / "lib" / "contract_validation.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            imports = {
                alias.name
                for node in ast.walk(tree)
                if isinstance(node, (ast.Import, ast.ImportFrom))
                for alias in (
                    node.names
                    if isinstance(node, ast.Import)
                    else [ast.alias(name=node.module or "")]
                )
            }
            self.assertFalse(
                imports & {"http.client", "requests", "socket", "subprocess", "urllib.request"},
                path,
            )
            called_attributes = {
                node.func.attr
                for node in ast.walk(tree)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            }
            self.assertFalse(called_attributes & {"write_text", "write_bytes", "unlink", "mkdir"}, path)


if __name__ == "__main__":
    unittest.main()
