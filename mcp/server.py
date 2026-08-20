#!/usr/bin/env python3
"""Networkless, read-only stdio MCP server for the Poland plugin."""

from __future__ import annotations

import json
import math
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT / "lib"))

from poland_core import (  # noqa: E402
    ROUTE_FACT_FIELDS,
    PolandDataError,
    action_boundary,
    build_checklist,
    error_envelope,
    freshness_report,
    get_digital_channel,
    get_source,
    list_regions,
    lookup_terms,
    overview,
    response_envelope,
    route_scenario,
    search_digital_channels,
    search_sources,
    validate_public_literal,
)


SERVER_VERSION = json.loads(
    (PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
)["version"]
PROTOCOL_VERSION = "2025-06-18"
MAX_FRAME_BYTES = 262144
MAX_TOOL_RESULT_BYTES = 196608
STABLE_ID_REGEX = r"^[a-z0-9][a-z0-9.-]{1,79}$"
CHANNEL_ID_REGEX = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
BOOLEAN_FACT_FIELDS = {"safe_to_speak", "urgent"}
DATE_FACT_FIELDS = {"intended_arrival_date", "target_date"}


def object_schema(properties: dict[str, Any], required: list[str] | None = None) -> dict[str, Any]:
    schema: dict[str, Any] = {
        "type": "object",
        "properties": properties,
        "additionalProperties": False,
    }
    if required:
        schema["required"] = required
    return schema


def _fact_schema(field: str) -> dict[str, Any]:
    if field == "citizenship_group":
        return {
            "type": ["string", "null"],
            "enum": ["polish", "eu_eea_swiss", "third_country", "stateless_or_unknown", None],
        }
    if field in BOOLEAN_FACT_FIELDS:
        return {"type": ["boolean", "null"]}
    schema: dict[str, Any] = {"type": ["string", "null"], "maxLength": 120}
    if field in DATE_FACT_FIELDS:
        schema["format"] = "date"
    elif field == "tax_year":
        schema["pattern"] = r"^\d{4}$"
    else:
        schema["pattern"] = r"^[A-Za-z][A-Za-z0-9_-]{0,119}$"
    return schema


FACT_PROPERTIES = {field: _fact_schema(field) for field in sorted(ROUTE_FACT_FIELDS)}
PROFILE_SCHEMA = object_schema({"facts": object_schema(FACT_PROPERTIES)})


TOOLS: dict[str, dict[str, Any]] = {
    "poland_overview": {
        "title": "Poland Overview",
        "description": "Describe the packaged offline Poland capability and dataset counts.",
        "inputSchema": object_schema({}),
    },
    "poland_search_sources": {
        "title": "Search Poland Official Sources",
        "description": "Search packaged official source records without making a network request.",
        "inputSchema": object_schema(
            {
                "query": {"type": "string", "maxLength": 160, "default": ""},
                "topic": {"type": "string", "maxLength": 80},
                "access": {
                    "type": "string",
                    "enum": ["public", "authenticated", "credentialed_api"],
                },
                "jurisdiction": {
                    "type": "string",
                    "enum": ["national", "eu", "voivodeship", "gmina"],
                },
                "locality": {"type": "string", "maxLength": 80},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20},
            }
        ),
    },
    "poland_get_source": {
        "title": "Get Poland Source",
        "description": "Get one packaged official source record by stable public ID.",
        "inputSchema": object_schema(
            {"source_id": {"type": "string", "pattern": STABLE_ID_REGEX}},
            ["source_id"],
        ),
    },
    "poland_search_channels": {
        "title": "Search Poland Digital Channels",
        "description": (
            "Search packaged digital-channel descriptors without authentication, network access, "
            "or external action."
        ),
        "inputSchema": object_schema(
            {
                "query": {"type": "string", "maxLength": 160, "default": ""},
                "channel_kind": {
                    "type": "string",
                    "enum": [
                        "application_portal",
                        "appointment_portal",
                        "correspondence",
                        "identity_signature",
                        "information_portal",
                        "mobile_app",
                        "open_data_api",
                        "personal_account",
                        "public_registry",
                    ],
                },
                "access_scope": {
                    "type": "string",
                    "enum": ["authenticated", "credentialed_api", "mixed", "public"],
                },
                "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20},
                "as_of": {"type": "string", "format": "date"},
            }
        ),
    },
    "poland_get_channel": {
        "title": "Get Poland Digital Channel",
        "description": (
            "Get one packaged digital-channel descriptor; protected interactions remain unsupported."
        ),
        "inputSchema": object_schema(
            {
                "channel_id": {
                    "type": "string",
                    "maxLength": 80,
                    "pattern": CHANNEL_ID_REGEX,
                },
                "as_of": {"type": "string", "format": "date"},
            },
            ["channel_id"],
        ),
    },
    "poland_route_scenario": {
        "title": "Route Poland Scenario",
        "description": "Route abstract categorical facts without deciding legal eligibility.",
        "inputSchema": object_schema(
            {
                "query": {"type": "string", "minLength": 1, "maxLength": 160},
                "profile": PROFILE_SCHEMA,
                "as_of": {"type": "string", "format": "date"},
            },
            ["query"],
        ),
    },
    "poland_build_checklist": {
        "title": "Build Poland Checklist",
        "description": "Build a packaged, evidence-gated checklist without taking an external action.",
        "inputSchema": object_schema(
            {
                "scenario_id": {"type": "string", "pattern": STABLE_ID_REGEX},
                "profile": PROFILE_SCHEMA,
                "as_of": {"type": "string", "format": "date"},
            },
            ["scenario_id"],
        ),
    },
    "poland_lookup_term": {
        "title": "Look Up Polish Term",
        "description": "Look up concise packaged Polish administrative terminology.",
        "inputSchema": object_schema(
            {
                "query": {"type": "string", "maxLength": 160, "default": ""},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20},
            }
        ),
    },
    "poland_list_regions": {
        "title": "List Poland Regions",
        "description": "List or search the packaged voivodeship directory.",
        "inputSchema": object_schema(
            {"query": {"type": "string", "maxLength": 80, "default": ""}}
        ),
    },
    "poland_freshness_report": {
        "title": "Poland Source Freshness",
        "description": "Compare packaged source review dates with an as-of date.",
        "inputSchema": object_schema({"as_of": {"type": "string", "format": "date"}}),
    },
    "poland_action_boundary": {
        "title": "Classify Poland Action",
        "description": "Classify an abstract intended action; the server never performs it.",
        "inputSchema": object_schema(
            {"action": {"type": "string", "minLength": 1, "maxLength": 160}},
            ["action"],
        ),
    },
}
for definition in TOOLS.values():
    definition["annotations"] = {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }


TOOL_OPERATIONS = {
    "poland_overview": "overview",
    "poland_search_sources": "sources",
    "poland_get_source": "source",
    "poland_search_channels": "channels",
    "poland_get_channel": "channel",
    "poland_route_scenario": "route",
    "poland_build_checklist": "checklist",
    "poland_lookup_term": "terms",
    "poland_list_regions": "regions",
    "poland_freshness_report": "freshness",
    "poland_action_boundary": "boundary",
}


def _schema_error(path: str, _constraint: str, *, code: str = "INVALID_ARGUMENTS") -> None:
    field = re.sub(r"[^a-z0-9_]+", "_", path.casefold()).strip("_")[:80] or "arguments"
    raise PolandDataError(
        "tool arguments violate the declared input schema",
        code=code,
        details={"field": field},
    )


def _matches_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return False


def validate_schema_value(value: Any, schema: dict[str, Any], *, path: str = "arguments") -> None:
    expected = schema.get("type")
    expected_types = expected if isinstance(expected, list) else [expected]
    if not any(_matches_type(value, item) for item in expected_types if isinstance(item, str)):
        _schema_error(path, "type")
    if value is None:
        if "enum" in schema and value not in schema["enum"]:
            _schema_error(path, "enum")
        return
    if "enum" in schema and value not in schema["enum"]:
        _schema_error(path, "enum")
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        missing = [item for item in schema.get("required", []) if item not in value]
        if missing:
            _schema_error(path, "required")
        if schema.get("additionalProperties") is False and any(key not in properties for key in value):
            _schema_error(path, "additionalProperties", code="UNSUPPORTED_FIELD")
        for key, child in value.items():
            if key in properties:
                validate_schema_value(child, properties[key], path=f"{path}.{key}")
        return
    if isinstance(value, str):
        safe_field = re.sub(r"[^a-z0-9_]+", "_", path.casefold()).strip("_")[:80] or "arguments"
        try:
            validate_public_literal(
                value,
                safe_field,
                allow_empty=schema.get("minLength", 0) == 0,
                max_length=schema.get("maxLength", 160),
            )
        except PolandDataError as exc:
            if exc.code == "SENSITIVE_INPUT_REJECTED":
                raise
        if len(value) < schema.get("minLength", 0):
            _schema_error(path, "minLength")
        if len(value) > schema.get("maxLength", len(value)):
            _schema_error(path, "maxLength", code="INPUT_TOO_LARGE")
        if "pattern" in schema and re.fullmatch(schema["pattern"], value) is None:
            _schema_error(path, "pattern", code="INVALID_IDENTIFIER")
        if schema.get("format") == "date":
            try:
                date.fromisoformat(value)
            except ValueError:
                _schema_error(path, "format")
        return
    if isinstance(value, int) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            _schema_error(path, "minimum")
        if "maximum" in schema and value > schema["maximum"]:
            _schema_error(path, "maximum")


def _safe_optional_literal(value: Any, *, field: str) -> str | None:
    if value is None:
        return None
    return validate_public_literal(value, field)


def _execute_tool(name: str, arguments: dict[str, Any]) -> Any:
    if name == "poland_overview":
        return overview()
    if name == "poland_search_sources":
        return search_sources(
            _safe_optional_literal(arguments.get("query", ""), field="query") or "",
            topic=_safe_optional_literal(arguments.get("topic"), field="topic"),
            access=arguments.get("access"),
            jurisdiction=arguments.get("jurisdiction"),
            locality=_safe_optional_literal(arguments.get("locality"), field="locality"),
            limit=arguments.get("limit", 20),
        )
    if name == "poland_get_source":
        return get_source(arguments["source_id"])
    if name == "poland_search_channels":
        return search_digital_channels(
            _safe_optional_literal(arguments.get("query", ""), field="query") or "",
            channel_kind=arguments.get("channel_kind"),
            access_scope=arguments.get("access_scope"),
            limit=arguments.get("limit", 20),
            as_of=arguments.get("as_of"),
        )
    if name == "poland_get_channel":
        return get_digital_channel(
            arguments["channel_id"],
            as_of=arguments.get("as_of"),
        )
    if name == "poland_route_scenario":
        return route_scenario(
            arguments["query"],
            arguments.get("profile"),
            as_of=arguments.get("as_of"),
        )
    if name == "poland_build_checklist":
        return build_checklist(
            arguments["scenario_id"],
            arguments.get("profile"),
            as_of=arguments.get("as_of"),
        )
    if name == "poland_lookup_term":
        return lookup_terms(
            _safe_optional_literal(arguments.get("query", ""), field="query") or "",
            arguments.get("limit", 20),
        )
    if name == "poland_list_regions":
        return list_regions(_safe_optional_literal(arguments.get("query", ""), field="query") or "")
    if name == "poland_freshness_report":
        return freshness_report(arguments.get("as_of"))
    if name == "poland_action_boundary":
        action = validate_public_literal(arguments["action"], "action", allow_empty=False)
        return action_boundary(action)
    raise PolandDataError("unknown Poland tool", code="UNKNOWN_TOOL")


def call_tool(name: Any, arguments: Any) -> dict[str, Any]:
    if not isinstance(name, str) or name not in TOOLS:
        raise PolandDataError("unknown Poland tool", code="UNKNOWN_TOOL")
    if not isinstance(arguments, dict):
        _schema_error("arguments", "type")
    validate_schema_value(arguments, TOOLS[name]["inputSchema"])
    operation = TOOL_OPERATIONS[name]
    result = _execute_tool(name, arguments)
    return response_envelope(operation, result, as_of=arguments.get("as_of"))


def tool_result(envelope: dict[str, Any]) -> dict[str, Any]:
    encoded = json.dumps(envelope, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if len(encoded.encode("utf-8")) > MAX_TOOL_RESULT_BYTES:
        raise PolandDataError(
            "tool result exceeds the MCP output limit",
            code="OUTPUT_TOO_LARGE",
            details={"max_bytes": MAX_TOOL_RESULT_BYTES},
        )
    return {
        "content": [{"type": "text", "text": encoded}],
        "structuredContent": envelope,
    }


def valid_id(value: Any) -> bool:
    return value is None or (
        not isinstance(value, bool)
        and isinstance(value, (str, int, float))
        and (not isinstance(value, float) or math.isfinite(value))
    )


def response_for(message: Any) -> dict[str, Any] | None:
    if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
        return {
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32600, "message": "invalid JSON-RPC request"},
        }
    has_id = "id" in message
    request_id = message.get("id")
    if has_id and not valid_id(request_id):
        return {
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32600, "message": "invalid request id"},
        }
    if not has_id:
        return None
    method = message.get("method")
    operation = "rpc"
    try:
        if method == "initialize":
            result = {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "Poland", "version": SERVER_VERSION},
                "instructions": (
                    "Networkless, read-only Poland source and planning tools. "
                    "Use abstract categorical facts only. Never authenticate, read personal records, "
                    "upload, download, send, sign, book, pay, submit, or change external state."
                ),
            }
        elif method == "ping":
            result = {}
        elif method == "tools/list":
            result = {"tools": [{"name": name, **definition} for name, definition in TOOLS.items()]}
        elif method == "tools/call":
            params = message.get("params")
            if not isinstance(params, dict) or any(key not in {"name", "arguments", "_meta"} for key in params):
                raise PolandDataError("invalid tools/call parameters", code="INVALID_ARGUMENTS")
            requested_name = params.get("name")
            if isinstance(requested_name, str) and requested_name in TOOL_OPERATIONS:
                operation = TOOL_OPERATIONS[requested_name]
            result = tool_result(call_tool(requested_name, params.get("arguments", {})))
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": "method not found"},
            }
        return {"jsonrpc": "2.0", "id": request_id, "result": result}
    except PolandDataError as exc:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32602,
                "message": "invalid Poland tool request",
                "data": error_envelope(operation, exc),
            },
        }
    except Exception:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32603, "message": "internal Poland server error"},
        }


def main() -> int:
    while True:
        raw = sys.stdin.buffer.readline(MAX_FRAME_BYTES + 1)
        if not raw:
            return 0
        if len(raw) > MAX_FRAME_BYTES:
            while raw and not raw.endswith(b"\n"):
                raw = sys.stdin.buffer.readline(MAX_FRAME_BYTES + 1)
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "JSON-RPC frame exceeds size limit"},
            }
        else:
            try:
                message = json.loads(raw)
            except (json.JSONDecodeError, UnicodeDecodeError, RecursionError):
                response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": "invalid JSON-RPC JSON frame"},
                }
            else:
                response = response_for(message)
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    raise SystemExit(main())
