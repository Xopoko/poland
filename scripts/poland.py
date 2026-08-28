#!/usr/bin/env python3
"""Read-only CLI for Poland source discovery and evidence-gated planning."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT / "lib"))

from poland_core import (  # noqa: E402
    FRESHNESS_STATUSES,
    ONTOLOGY_LAYERS,
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
    ontology_map,
    overview,
    response_envelope,
    route_scenario,
    search_digital_channels,
    search_sources,
    validate_bundle,
    validate_public_literal,
)


STABLE_ID_PATTERN = re.compile(r"[a-z0-9][a-z0-9.-]{1,79}\Z")
CHANNEL_ID_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
COMMANDS = {
    "overview",
    "validate",
    "sources",
    "source",
    "channels",
    "channel",
    "route",
    "checklist",
    "terms",
    "regions",
    "freshness",
    "ontology",
    "boundary",
    "doctor",
}
BOOLEAN_FACT_FIELDS = {"safe_to_speak", "urgent"}
DATE_FACT_FIELDS = {"intended_arrival_date", "target_date"}
MINIMUM_PYTHON = (3, 11)
DOCTOR_SCHEMA = "poland.doctor_receipt.v1"
DOCTOR_HOSTS = ("package", "codex", "claude", "cursor", "pi")
MCP_CONFIG_PATHS = {
    "codex": ".codex-mcp.json",
    "claude": ".mcp.json",
    "cursor": ".codex-mcp.json",
}
MCP_CONFIG_FILENAMES = {
    "codex": ".codex-mcp.json",
    "claude": ".mcp.json",
    "cursor": ".codex-mcp.json",
}
MCP_PROBE_TIMEOUT_SECONDS = 8
MAX_MCP_PROBE_OUTPUT_BYTES = 1_000_000


class ContractArgumentParser(argparse.ArgumentParser):
    """Argparse variant that never copies caller text into an error response."""

    def error(self, message: str) -> None:  # noqa: ARG002 - argparse contract
        raise PolandDataError(
            "invalid command arguments",
            code="INVALID_ARGUMENTS",
            details={"field": "arguments"},
        )


def _safe_optional_literal(value: Any, *, field: str) -> str | None:
    if value is None:
        return None
    return validate_public_literal(value, field)


def _stable_id(value: Any, *, field: str) -> str:
    if not isinstance(value, str) or not STABLE_ID_PATTERN.fullmatch(value):
        raise PolandDataError(
            "identifier must use the public stable-ID format",
            code="INVALID_IDENTIFIER",
            details={"field": field},
        )
    return value


def _channel_id(value: Any) -> str:
    safe_value = validate_public_literal(value, "channel_id", allow_empty=False, max_length=80)
    if not CHANNEL_ID_PATTERN.fullmatch(safe_value):
        raise PolandDataError(
            "identifier must use the digital-channel ID format",
            code="INVALID_CHANNEL_ID",
            details={"field": "channel_id"},
        )
    return safe_value


def profile_from_args(args: argparse.Namespace) -> dict[str, Any]:
    facts = {
        field: value
        for field in sorted(ROUTE_FACT_FIELDS)
        if (value := getattr(args, field, None)) is not None
    }
    return {"facts": facts}


def add_profile_arguments(parser: argparse.ArgumentParser) -> None:
    for field in sorted(ROUTE_FACT_FIELDS):
        flag = "--" + field.replace("_", "-")
        if field == "citizenship_group":
            parser.add_argument(
                flag,
                choices=["polish", "eu_eea_swiss", "third_country", "stateless_or_unknown"],
                help="Abstract nationality category; never enter a document number.",
            )
        elif field in {"eu_efta_family_member_status", "pesel_status"}:
            parser.add_argument(
                flag,
                choices=["present", "absent", "unknown"],
                help="Abstract presence category only; never enter an identifier.",
            )
        elif field in BOOLEAN_FACT_FIELDS:
            parser.add_argument(flag, action=argparse.BooleanOptionalAction, default=None)
        else:
            parser.add_argument(
                flag,
                metavar="CATEGORY" if field not in DATE_FACT_FIELDS else "YYYY-MM-DD",
                help="Non-sensitive categorical fact only.",
            )


def _read_json_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("JSON root must be an object")
    return value


def _manifest_versions() -> dict[str, str | None]:
    locations = {
        "codex": PLUGIN_ROOT / ".codex-plugin" / "plugin.json",
        "claude": PLUGIN_ROOT / ".claude-plugin" / "plugin.json",
        "cursor": PLUGIN_ROOT / ".cursor-plugin" / "plugin.json",
        "package": PLUGIN_ROOT / "package.json",
    }
    versions: dict[str, str | None] = {}
    for name, path in locations.items():
        try:
            version = _read_json_object(path).get("version")
        except (OSError, ValueError, json.JSONDecodeError):
            version = None
        versions[name] = version if isinstance(version, str) else None
    return versions


def _pi_skill_inventory() -> set[str] | None:
    try:
        package = _read_json_object(PLUGIN_ROOT / "package.json")
    except (OSError, ValueError, json.JSONDecodeError):
        return None
    pi = package.get("pi")
    entries = pi.get("skills") if isinstance(pi, dict) else None
    if not isinstance(entries, list) or any(not isinstance(item, str) for item in entries):
        return None
    prefix = "./skills/"
    names = [item[len(prefix) :] for item in entries if item.startswith(prefix)]
    if len(names) != len(entries) or any(not name or "/" in name or "\\" in name for name in names):
        return None
    if len(set(names)) != len(names):
        return None
    return set(names)


def _git_revision() -> tuple[str | None, str]:
    try:
        revision = subprocess.run(
            ["git", "-C", str(PLUGIN_ROOT), "rev-parse", "HEAD"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=3,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None, "unavailable"
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        return None, "unavailable"
    try:
        worktree = subprocess.run(
            ["git", "-C", str(PLUGIN_ROOT), "status", "--porcelain"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=3,
        )
    except (OSError, subprocess.SubprocessError):
        return revision, "unknown"
    return revision, "clean" if worktree.returncode == 0 and not worktree.stdout else "modified"


def _expand_mcp_value(value: str) -> str:
    python_command = os.environ.get("POLAND_PYTHON") or "python3"
    replacements = {
        "${CLAUDE_PLUGIN_ROOT}": str(PLUGIN_ROOT),
        "${PLUGIN_ROOT}": str(PLUGIN_ROOT),
        "${POLAND_PYTHON:-python3}": python_command,
    }
    for placeholder, replacement in replacements.items():
        value = value.replace(placeholder, replacement)
    return value


def _mcp_command_from_config(config: dict[str, Any]) -> tuple[str, list[str], Path]:
    servers = config.get("mcpServers")
    if not isinstance(servers, dict) or not isinstance(servers.get("poland"), dict):
        raise ValueError("missing Poland MCP server")
    server = servers["poland"]
    command = server.get("command")
    args = server.get("args", [])
    cwd = server.get("cwd", ".")
    if not isinstance(command, str) or not isinstance(cwd, str):
        raise ValueError("invalid MCP command")
    if not isinstance(args, list) or any(not isinstance(item, str) for item in args):
        raise ValueError("invalid MCP arguments")
    command = _expand_mcp_value(command)
    args = [_expand_mcp_value(item) for item in args]
    expanded_cwd = Path(_expand_mcp_value(cwd))
    if not expanded_cwd.is_absolute():
        expanded_cwd = PLUGIN_ROOT / expanded_cwd
    return command, args, expanded_cwd


def _configured_mcp_command(host: str) -> tuple[str, list[str], Path]:
    return _mcp_command_from_config(_read_json_object(PLUGIN_ROOT / MCP_CONFIG_PATHS[host]))


def _subprocess_options() -> dict[str, Any]:
    if os.name == "nt" and hasattr(subprocess, "CREATE_NO_WINDOW"):
        return {"creationflags": subprocess.CREATE_NO_WINDOW}
    return {}


def _python_launcher_probe(command: str, environment: dict[str, str]) -> dict[str, Any]:
    probe = (
        "import json,platform,sys;"
        "print(json.dumps({'implementation':platform.python_implementation(),"
        "'version':platform.python_version(),'supported':sys.version_info>=(3,11)},"
        "separators=(',',':')))"
    )
    try:
        process = subprocess.run(
            [command, "-I", "-c", probe],
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=3,
            **_subprocess_options(),
        )
    except FileNotFoundError:
        return {"status": "failed", "reason": "launcher_not_found"}
    except PermissionError:
        return {"status": "failed", "reason": "launcher_not_executable"}
    except subprocess.TimeoutExpired:
        return {"status": "failed", "reason": "launcher_timeout"}
    except (OSError, UnicodeError):
        return {"status": "failed", "reason": "launcher_error"}
    if process.returncode != 0:
        return {"status": "failed", "reason": "launcher_not_python"}
    try:
        result = json.loads(process.stdout)
    except (json.JSONDecodeError, UnicodeError):
        return {"status": "failed", "reason": "launcher_invalid_version_output"}
    if not isinstance(result, dict) or not isinstance(result.get("supported"), bool):
        return {"status": "failed", "reason": "launcher_invalid_version_output"}
    if not result["supported"]:
        return {
            "status": "failed",
            "reason": "python_too_old",
            "implementation": result.get("implementation"),
            "version": result.get("version"),
        }
    return {
        "status": "passed",
        "reason": None,
        "implementation": result.get("implementation"),
        "version": result.get("version"),
    }


def _mcp_smoke(command: str, args: list[str], cwd: Path) -> dict[str, Any]:
    requests = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "poland-doctor", "version": "1"},
            },
        },
        {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        {"jsonrpc": "2.0", "id": 3, "method": "ping", "params": {}},
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "poland_overview", "arguments": {}},
        },
    ]
    payload = "".join(json.dumps(item, separators=(",", ":")) + "\n" for item in requests)
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONUTF8"] = "1"
    launcher = _python_launcher_probe(command, environment)
    if launcher["status"] != "passed":
        return {
            "status": "failed",
            "reason": launcher["reason"],
            "launcher": launcher,
            "tool_count": None,
        }
    try:
        process = subprocess.run(
            [command, *args],
            cwd=cwd,
            env=environment,
            input=payload,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=MCP_PROBE_TIMEOUT_SECONDS,
            **_subprocess_options(),
        )
    except FileNotFoundError:
        return {"status": "failed", "reason": "launcher_not_found", "tool_count": None}
    except PermissionError:
        return {"status": "failed", "reason": "launcher_not_executable", "tool_count": None}
    except subprocess.TimeoutExpired:
        return {"status": "failed", "reason": "startup_timeout", "tool_count": None}
    except (OSError, UnicodeError):
        return {"status": "failed", "reason": "launcher_error", "tool_count": None}
    if len(process.stdout.encode("utf-8", errors="replace")) > MAX_MCP_PROBE_OUTPUT_BYTES:
        return {"status": "failed", "reason": "output_limit", "tool_count": None}
    if process.returncode != 0:
        return {"status": "failed", "reason": "server_exit", "tool_count": None}
    try:
        messages = [json.loads(line) for line in process.stdout.splitlines() if line.strip()]
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {"status": "failed", "reason": "invalid_json", "tool_count": None}
    by_id = {item.get("id"): item for item in messages if isinstance(item, dict)}
    response_ids = (1, 2, 3, 4)
    if set(by_id) != set(response_ids) or any("error" in by_id[item] for item in response_ids):
        return {"status": "failed", "reason": "invalid_protocol_response", "tool_count": None}
    initialize = by_id[1].get("result")
    tools_result = by_id[2].get("result")
    overview_result = by_id[4].get("result")
    tools = tools_result.get("tools") if isinstance(tools_result, dict) else None
    server_info = initialize.get("serverInfo") if isinstance(initialize, dict) else None
    if (
        not isinstance(tools, list)
        or not tools
        or not isinstance(server_info, dict)
        or not isinstance(server_info.get("name"), str)
        or not isinstance(server_info.get("version"), str)
    ):
        return {"status": "failed", "reason": "invalid_capabilities", "tool_count": None}
    if not isinstance(overview_result, dict) or not isinstance(
        overview_result.get("structuredContent"), dict
    ):
        return {"status": "failed", "reason": "read_only_tool_call_failed", "tool_count": len(tools)}
    return {
        "status": "passed",
        "reason": None,
        "launcher": launcher,
        "server_name": server_info.get("name"),
        "server_version": server_info.get("version"),
        "tool_count": len(tools),
        "read_only_tool_call": "poland_overview",
    }


def _host_capability(host: str, skill_count: int) -> dict[str, Any]:
    common = {
        "host_version": "not_checked",
        "installation_scope": "not_checked",
        "skills": {
            "packaged": True,
            "count": skill_count,
            "host_loaded_count": None,
        },
        "cli": {"bundled": True, "automatic_registration": False},
        "native_host_discovery": "not_checked",
    }
    if host == "package":
        return {**common, "mcp": {"bundled": True, "registration": "host_specific"}}
    if host in MCP_CONFIG_PATHS:
        return {
            **common,
            "mcp": {
                "bundled": True,
                "config": MCP_CONFIG_PATHS[host],
                "registration": "companion_config_declared",
                "requires_current_host_preflight": True,
            },
        }
    return {
        **common,
        "mcp": {
            "bundled": True,
            "registration": "not_declared_by_pi_package",
            "requires_separate_host_setup": True,
        },
    }


def _generated_mcp_config(host: str) -> dict[str, Any]:
    if host not in MCP_CONFIG_PATHS:
        raise PolandDataError(
            "the selected host has no plugin MCP companion configuration",
            code="UNSUPPORTED_HOST_COMPONENT",
            details={"host": host},
        )
    python_executable = str(Path(sys.executable).resolve())
    if host == "claude":
        args = ["-I", "-B", "${CLAUDE_PLUGIN_ROOT}/mcp/server.py"]
        cwd = "${CLAUDE_PLUGIN_ROOT}"
    else:
        args = ["-I", "-B", "./mcp/server.py"]
        cwd = "."
    return {
        "mcpServers": {
            "poland": {
                "command": python_executable,
                "args": args,
                "cwd": cwd,
            }
        }
    }


def _write_generated_mcp_config(host: str, raw_target: str, *, force: bool) -> dict[str, Any]:
    target = Path(raw_target).expanduser()
    expected_name = MCP_CONFIG_FILENAMES.get(host)
    if expected_name is None:
        raise PolandDataError(
            "the selected host has no plugin MCP companion configuration",
            code="UNSUPPORTED_HOST_COMPONENT",
            details={"host": host},
        )
    if target.name != expected_name:
        raise PolandDataError(
            "generated MCP configuration must use the host companion filename",
            code="INVALID_OUTPUT_TARGET",
            details={"expected_filename": expected_name},
        )
    try:
        parent = target.parent.resolve(strict=True)
    except OSError as exc:
        raise PolandDataError(
            "generated MCP configuration parent directory does not exist",
            code="INVALID_OUTPUT_TARGET",
        ) from exc
    resolved_target = parent / target.name
    try:
        inside_source = resolved_target.is_relative_to(PLUGIN_ROOT.resolve())
    except OSError:
        inside_source = False
    if inside_source:
        raise PolandDataError(
            "refusing to write generated host configuration inside plugin source",
            code="INVALID_OUTPUT_TARGET",
        )
    if resolved_target.is_symlink():
        raise PolandDataError(
            "refusing to replace a symbolic-link output target",
            code="INVALID_OUTPUT_TARGET",
        )
    if resolved_target.exists() and not force:
        raise PolandDataError(
            "output target already exists; use --force only after reviewing it",
            code="OUTPUT_EXISTS",
        )
    encoded = (json.dumps(_generated_mcp_config(host), ensure_ascii=True, indent=2) + "\n").encode("utf-8")
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f".{target.name}.",
            suffix=".tmp",
            dir=parent,
            delete=False,
        ) as temporary:
            temporary.write(encoded)
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_name = temporary.name
        os.chmod(temporary_name, 0o600)
        os.replace(temporary_name, resolved_target)
    except OSError as exc:
        if temporary_name:
            try:
                Path(temporary_name).unlink(missing_ok=True)
            except OSError:
                pass
        raise PolandDataError(
            "unable to write generated MCP configuration",
            code="OUTPUT_WRITE_FAILED",
        ) from exc
    return {
        "written": True,
        "filename": target.name,
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "contains_local_interpreter_path": True,
        "commit_safe": False,
    }


def doctor(
    host: str,
    *,
    as_of: str | None = None,
    write_mcp_config: str | None = None,
    force: bool = False,
) -> dict[str, Any]:
    versions = _manifest_versions()
    non_null_versions = {item for item in versions.values() if item is not None}
    skill_names = {path.parent.name for path in (PLUGIN_ROOT / "skills").glob("*/SKILL.md")}
    declared_skill_names = _pi_skill_inventory()
    skill_count = len(skill_names)
    skill_inventory_aligned = declared_skill_names == skill_names
    revision, source_tree = _git_revision()
    python_supported = sys.version_info >= MINIMUM_PYTHON
    core_smoke = _mcp_smoke(
        sys.executable,
        ["-I", "-B", str(PLUGIN_ROOT / "mcp" / "server.py")],
        PLUGIN_ROOT,
    )
    if host in MCP_CONFIG_PATHS:
        try:
            command, args, cwd = _configured_mcp_command(host)
        except (OSError, ValueError, KeyError, json.JSONDecodeError):
            configured_smoke = {"status": "failed", "reason": "invalid_config", "tool_count": None}
        else:
            configured_smoke = _mcp_smoke(command, args, cwd)
    else:
        configured_smoke = {"status": "not_applicable", "reason": None, "tool_count": None}
    freshness = freshness_report(as_of)
    bundle_validation = validate_bundle(as_of)
    versions_aligned = len(non_null_versions) == 1 and all(value is not None for value in versions.values())
    package_version = next(iter(non_null_versions)) if versions_aligned else None

    def expected_mcp(smoke: dict[str, Any]) -> bool:
        return (
            smoke.get("status") == "passed"
            and smoke.get("server_name") == "Poland"
            and smoke.get("server_version") == package_version
            and isinstance(smoke.get("tool_count"), int)
            and smoke["tool_count"] > 0
            and smoke.get("read_only_tool_call") == "poland_overview"
        )

    package_ok = (
        python_supported
        and skill_count > 0
        and "poland" in skill_names
        and skill_inventory_aligned
        and versions_aligned
        and bundle_validation.get("valid") is True
        and expected_mcp(core_smoke)
    )
    generated = None
    generated_smoke = {"status": "not_applicable", "reason": None, "tool_count": None}
    if write_mcp_config is not None:
        if not package_ok:
            raise PolandDataError(
                "package preflight must pass before generating host configuration",
                code="PACKAGE_PREFLIGHT_FAILED",
            )
        command, args, cwd = _mcp_command_from_config(_generated_mcp_config(host))
        generated_smoke = _mcp_smoke(command, args, cwd)
        if not expected_mcp(generated_smoke):
            raise PolandDataError(
                "generated host configuration did not pass the MCP preflight",
                code="GENERATED_CONFIG_PREFLIGHT_FAILED",
            )
        generated = _write_generated_mcp_config(host, write_mcp_config, force=force)
    effective_smoke = generated_smoke if write_mcp_config is not None else configured_smoke
    host_ok = effective_smoke["status"] == "not_applicable" or expected_mcp(effective_smoke)
    return {
        "schema": DOCTOR_SCHEMA,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
            "+00:00", "Z"
        ),
        "valid": package_ok and host_ok,
        "selected_host": host,
        "package": {
            "name": "poland",
            "version": package_version,
            "manifest_versions": versions,
            "versions_aligned": versions_aligned,
            "git_commit": revision,
            "source_tree": source_tree,
            "skills": skill_count,
            "declared_skills": len(declared_skill_names) if declared_skill_names is not None else None,
            "skill_inventory_aligned": skill_inventory_aligned,
        },
        "runtime": {
            "operating_system": platform.system().casefold() or "unknown",
            "architecture": platform.machine() or "unknown",
            "python": {
                "implementation": platform.python_implementation(),
                "version": platform.python_version(),
                "minimum": ".".join(map(str, MINIMUM_PYTHON)),
                "supported": python_supported,
                "executable_path_disclosed": False,
            },
        },
        "capability": _host_capability(host, skill_count),
        "checks": {
            "bundle_validation": {
                "valid": bundle_validation.get("valid") is True,
                "bundle_sha256": bundle_validation.get("bundle_sha256"),
                "error_count": len(bundle_validation.get("errors", [])),
                "warning_count": len(bundle_validation.get("warnings", [])),
            },
            "bundled_mcp_round_trip": core_smoke,
            "configured_mcp_round_trip": configured_smoke,
            "generated_mcp_round_trip": generated_smoke,
            "host_plugin_discovery": "not_checked",
        },
        "freshness": {
            "as_of": freshness["as_of"],
            "summary": freshness["summary"],
        },
        "generated_mcp_config": generated,
        "privacy": {
            "poland_telemetry_emitted": False,
            "network_requests_made": False,
            "personal_paths_in_receipt": False,
            "agent_host_cli_invoked": False,
            "local_subprocesses": "git metadata and bundled MCP startup probes only",
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = ContractArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("overview", help="Show plugin scope and interface counts")
    validate = sub.add_parser("validate", help="Validate bundled offline data and schemas")
    validate.add_argument("--as-of")

    sources = sub.add_parser("sources", help="Search bundled official source records")
    sources.add_argument("--query", default="")
    sources.add_argument("--topic")
    sources.add_argument("--access", choices=["public", "authenticated", "credentialed_api"])
    sources.add_argument(
        "--jurisdiction",
        choices=["national", "eu", "voivodeship", "powiat", "gmina"],
    )
    sources.add_argument("--locality")
    sources.add_argument("--limit", type=int, choices=range(1, 101), default=20)

    source = sub.add_parser("source", help="Get one source by stable ID")
    source.add_argument("source_id")

    channels = sub.add_parser("channels", help="Search packaged digital-channel descriptors")
    channels.add_argument("query", nargs="?", default="")
    channels.add_argument(
        "--channel-kind",
        choices=[
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
    )
    channels.add_argument(
        "--access-scope",
        choices=["authenticated", "credentialed_api", "mixed", "public"],
    )
    channels.add_argument("--limit", type=int, choices=range(1, 101), default=20)
    channels.add_argument("--as-of")

    channel = sub.add_parser("channel", help="Get one packaged digital-channel descriptor")
    channel.add_argument("channel_id")
    channel.add_argument("--as-of")

    route = sub.add_parser("route", help="Route an abstract intent without deciding eligibility")
    route.add_argument("query")
    route.add_argument("--as-of")
    add_profile_arguments(route)

    checklist = sub.add_parser("checklist", help="Build an evidence-gated scenario checklist")
    checklist.add_argument("scenario_id")
    checklist.add_argument("--as-of")
    add_profile_arguments(checklist)

    terms = sub.add_parser("terms", help="Look up Polish administrative terms")
    terms.add_argument("query", nargs="?", default="")
    terms.add_argument("--limit", type=int, choices=range(1, 101), default=20)

    regions = sub.add_parser("regions", help="List or search voivodeships")
    regions.add_argument("query", nargs="?", default="")

    freshness = sub.add_parser("freshness", help="Report bundled source freshness")
    freshness.add_argument("--as-of")
    freshness.add_argument(
        "--status",
        dest="statuses",
        action="append",
        choices=FRESHNESS_STATUSES,
        help="Filter returned records; repeat for more than one status.",
    )
    freshness.add_argument("--topic")
    freshness.add_argument("--limit", type=int, choices=range(1, 101), default=50)
    freshness.add_argument("--summary-only", action="store_true")

    ontology = sub.add_parser(
        "ontology",
        help="Map packaged layers, relationships, dimensions, and coverage",
    )
    ontology.add_argument("--layer", choices=ONTOLOGY_LAYERS)
    ontology.add_argument("--detail", choices=["summary", "full"], default="summary")
    ontology.add_argument("--as-of")

    boundary = sub.add_parser("boundary", help="Classify an intended action boundary")
    boundary.add_argument("action")

    doctor_parser = sub.add_parser(
        "doctor",
        help="Run a telemetry-free package and local MCP preflight receipt",
    )
    doctor_parser.add_argument("--host", choices=DOCTOR_HOSTS, default="package")
    doctor_parser.add_argument("--as-of")
    doctor_parser.add_argument(
        "--write-mcp-config",
        metavar="PATH",
        help="Write a reviewed host-local companion config outside plugin source.",
    )
    doctor_parser.add_argument(
        "--force",
        action="store_true",
        help="Replace the explicit config output after it has been reviewed.",
    )
    return parser


def execute(args: argparse.Namespace) -> Any:
    if args.command == "overview":
        return overview()
    if args.command == "validate":
        return validate_bundle(args.as_of)
    if args.command == "sources":
        return search_sources(
            _safe_optional_literal(args.query, field="query") or "",
            topic=_safe_optional_literal(args.topic, field="topic"),
            access=args.access,
            jurisdiction=args.jurisdiction,
            locality=_safe_optional_literal(args.locality, field="locality"),
            limit=args.limit,
        )
    if args.command == "source":
        return get_source(_stable_id(args.source_id, field="source_id"))
    if args.command == "channels":
        return search_digital_channels(
            _safe_optional_literal(args.query, field="query") or "",
            channel_kind=args.channel_kind,
            access_scope=args.access_scope,
            limit=args.limit,
            as_of=args.as_of,
        )
    if args.command == "channel":
        return get_digital_channel(_channel_id(args.channel_id), as_of=args.as_of)
    if args.command == "route":
        return route_scenario(args.query, profile_from_args(args), as_of=args.as_of)
    if args.command == "checklist":
        return build_checklist(
            _stable_id(args.scenario_id, field="scenario_id"),
            profile_from_args(args),
            as_of=args.as_of,
        )
    if args.command == "terms":
        return lookup_terms(_safe_optional_literal(args.query, field="query") or "", args.limit)
    if args.command == "regions":
        return list_regions(_safe_optional_literal(args.query, field="query") or "")
    if args.command == "freshness":
        return freshness_report(
            args.as_of,
            statuses=args.statuses,
            topic=_safe_optional_literal(args.topic, field="topic"),
            limit=args.limit,
            summary_only=args.summary_only,
        )
    if args.command == "ontology":
        return ontology_map(layer=args.layer, detail=args.detail, as_of=args.as_of)
    if args.command == "boundary":
        return action_boundary(validate_public_literal(args.action, "action", allow_empty=False))
    if args.command == "doctor":
        if args.force and args.write_mcp_config is None:
            raise PolandDataError(
                "--force requires --write-mcp-config",
                code="INVALID_ARGUMENTS",
                details={"field": "force"},
            )
        return doctor(
            args.host,
            as_of=args.as_of,
            write_mcp_config=args.write_mcp_config,
            force=args.force,
        )
    raise PolandDataError("unsupported command", code="INVALID_ARGUMENTS")


def _operation_from_argv(argv: list[str]) -> str:
    return argv[0] if argv and argv[0] in COMMANDS else "parse"


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    operation = _operation_from_argv(arguments)
    try:
        parsed = build_parser().parse_args(arguments)
        operation = parsed.command
        result = execute(parsed)
        envelope = response_envelope(operation, result, as_of=getattr(parsed, "as_of", None))
        print(json.dumps(envelope, ensure_ascii=False, indent=2, sort_keys=True))
        return 1 if isinstance(result, dict) and result.get("valid") is False else 0
    except PolandDataError as exc:
        print(json.dumps(error_envelope(operation, exc), ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 2
    except ValueError:
        error = PolandDataError("invalid input", code="INVALID_INPUT")
        print(json.dumps(error_envelope(operation, error), ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 2
    except Exception:
        error = PolandDataError("internal CLI error", code="INTERNAL_ERROR")
        print(json.dumps(error_envelope(operation, error), ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
