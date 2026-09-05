#!/usr/bin/env python3
"""Validate the standalone Poland package without network access."""

from __future__ import annotations

import json
import os
import re
import struct
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))

from contract_validation import validate_datasets  # noqa: E402


PLUGIN_ID = "poland"
VERSION = "0.3.0"
EXPECTED_SKILL_COUNT = 33
REPOSITORY = "https://github.com/Xopoko/poland"
SHARED_MANIFEST_FIELDS = (
    "name",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
)
SKILL_FRONTMATTER_KEYS = {"name", "description"}
TEXT_SUFFIXES = {".json", ".md", ".py", ".txt", ".yaml", ".yml"}
SKIP_PARTS = {
    ".git",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "tmp",
    "venv",
}
ABSOLUTE_PATH = re.compile(
    "(?:[a-z]" + ":" + r"[\\/]" + "(?:users|projects)" + r"[\\/]" + "|/users/|/home/[^/\\s]+/)",
    re.IGNORECASE,
)
SECRET_PATTERNS = (
    re.compile(r"(?i)-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bgh[opsu]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
)
REQUIRED_PATHS = {
    ".agents/plugins/marketplace.json",
    ".claude-plugin/marketplace.json",
    ".claude-plugin/plugin.json",
    ".codex-mcp.json",
    ".codex-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
    ".github/ISSUE_TEMPLATE/bug-report.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/ISSUE_TEMPLATE/source-update.yml",
    ".github/ISSUE_TEMPLATE/workflow-request.yml",
    ".github/workflows/ci.yml",
    ".mcp.json",
    "AGENTS.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "DISCLAIMER.md",
    "LICENSE",
    "PRIVACY.md",
    "README.md",
    "SECURITY.md",
    "SOURCES.md",
    "SUPPORT.md",
    "TERMS.md",
    "agents/openai.yaml",
    "assets/ASSET_PROVENANCE.md",
    "assets/icon-prompt.json",
    "assets/icon.png",
    "docs/GETTING_STARTED.md",
    "docs/INSTALL.md",
    "package.json",
}


def strict_json_loads(text: str) -> Any:
    def no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    return json.loads(text, object_pairs_hook=no_duplicates)


def read_json(path: Path) -> dict[str, Any]:
    value = strict_json_loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("root JSON value must be an object")
    return value


def frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("missing YAML frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("unterminated YAML frontmatter") from exc
    result: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        key, separator, value = line.partition(":")
        if not separator:
            raise ValueError(f"invalid frontmatter line: {line}")
        key = key.strip()
        if key in result:
            raise ValueError(f"duplicate frontmatter key: {key}")
        result[key] = value.strip().strip('"')
    return result


def tracked_files() -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "-z"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        files = [
            Path(item.decode("utf-8"))
            for item in result.stdout.split(b"\0")
            if item
        ]
        if files:
            return files
    except (OSError, subprocess.CalledProcessError, UnicodeDecodeError):
        pass
    return sorted(
        path.relative_to(ROOT)
        for path in ROOT.rglob("*")
        if path.is_file()
        and not (set(path.relative_to(ROOT).parts) & SKIP_PARTS)
    )


def validate_png(path: Path) -> list[str]:
    errors: list[str] = []
    data = path.read_bytes()
    if len(data) < 33 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return ["assets/icon.png: not a PNG"]
    if data[12:16] != b"IHDR":
        return ["assets/icon.png: missing first IHDR chunk"]
    width, height, bit_depth, color_type = struct.unpack(">IIBB", data[16:26])
    if (width, height) != (1024, 1024):
        errors.append("assets/icon.png: must be exactly 1024x1024")
    if bit_depth != 8 or color_type != 2:
        errors.append("assets/icon.png: must be opaque 8-bit RGB")
    return errors


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    for relative in sorted(REQUIRED_PATHS):
        if not (ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")

    manifests: list[dict[str, Any]] = []
    for relative in (".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
        try:
            manifests.append(read_json(ROOT / relative))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{relative}: {exc}")
    if len(manifests) == 2:
        codex, claude = manifests
        for key in SHARED_MANIFEST_FIELDS:
            if codex.get(key) != claude.get(key):
                errors.append(f"manifest parity: {key} differs")
        if codex.get("name") != PLUGIN_ID:
            errors.append("manifest name must remain 'poland'")
        if codex.get("version") != VERSION:
            errors.append(f"manifest version must be {VERSION}")
        if codex.get("homepage") != REPOSITORY or codex.get("repository") != REPOSITORY:
            errors.append("manifest homepage and repository must point to standalone source")
        description = codex.get("description")
        if not isinstance(description, str) or not 1 <= len(description) <= 240:
            errors.append("manifest description must contain 1-240 characters")
        if codex.get("mcpServers") != "./.codex-mcp.json":
            errors.append("Codex manifest must bind .codex-mcp.json")
        interface = codex.get("interface")
        if not isinstance(interface, dict):
            errors.append("Codex interface is missing")
        else:
            if interface.get("websiteURL") != REPOSITORY:
                errors.append("Codex Website must point to the standalone source")
            if interface.get("privacyPolicyURL") != f"{REPOSITORY}/blob/main/PRIVACY.md":
                errors.append("privacyPolicyURL must point to standalone PRIVACY.md")
            if interface.get("termsOfServiceURL") != f"{REPOSITORY}/blob/main/TERMS.md":
                errors.append("termsOfServiceURL must point to standalone TERMS.md")
            if interface.get("composerIcon") != "./assets/icon.png" or interface.get("logo") != "./assets/icon.png":
                errors.append("Codex composerIcon and logo must share assets/icon.png")
            prompts = interface.get("defaultPrompt")
            if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3:
                errors.append("Codex defaultPrompt must contain 1-3 items")
            elif any(not isinstance(item, str) or len(item) > 128 for item in prompts):
                errors.append("Codex defaultPrompt items must be strings of at most 128 characters")

    try:
        marketplace = read_json(ROOT / ".claude-plugin" / "marketplace.json")
        entries = marketplace.get("plugins")
        entry = entries[0] if isinstance(entries, list) and len(entries) == 1 else None
        if marketplace.get("name") != "poland" or marketplace.get("version") != VERSION:
            errors.append("Claude marketplace name/version must match the standalone release")
        if not isinstance(entry, dict):
            errors.append("Claude marketplace must declare exactly one plugin")
        elif manifests:
            if entry.get("name") != PLUGIN_ID or entry.get("source") != "./":
                errors.append("Claude marketplace must bind poland to repository root")
            for key in ("version", "description", "repository", "author", "license"):
                if entry.get(key) != manifests[0].get(key):
                    errors.append(f"Claude marketplace plugin {key} differs from manifest")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f".claude-plugin/marketplace.json: {exc}")

    try:
        marketplace = read_json(ROOT / ".agents" / "plugins" / "marketplace.json")
        entries = marketplace.get("plugins")
        entry = entries[0] if isinstance(entries, list) and len(entries) == 1 else None
        if marketplace.get("name") != "poland":
            errors.append("Codex marketplace name must match the standalone repository")
        if marketplace.get("interface") != {"displayName": "Poland"}:
            errors.append("Codex marketplace display name must remain Poland")
        if not isinstance(entry, dict):
            errors.append("Codex marketplace must declare exactly one plugin")
        else:
            if entry.get("name") != PLUGIN_ID:
                errors.append("Codex marketplace plugin name must remain poland")
            if entry.get("source") != {"source": "local", "path": "."}:
                errors.append("Codex marketplace must bind poland to repository root")
            if entry.get("policy") != {
                "installation": "AVAILABLE",
                "authentication": "ON_INSTALL",
            }:
                errors.append("Codex marketplace must keep Poland opt-in and authenticate on install")
            if entry.get("category") != "Productivity":
                errors.append("Codex marketplace category must remain Productivity")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f".agents/plugins/marketplace.json: {exc}")

    skill_paths = sorted((ROOT / "skills").glob("*/SKILL.md"))
    skill_names: set[str] = set()
    for path in skill_paths:
        relative = path.relative_to(ROOT).as_posix()
        try:
            metadata = frontmatter(path)
        except (OSError, ValueError) as exc:
            errors.append(f"{relative}: {exc}")
            continue
        if set(metadata) != SKILL_FRONTMATTER_KEYS:
            errors.append(f"{relative}: frontmatter must contain only name and description")
        name = metadata.get("name")
        description = metadata.get("description")
        if name != path.parent.name:
            errors.append(f"{relative}: name must match directory")
        if name in skill_names:
            errors.append(f"duplicate skill name: {name}")
        if isinstance(name, str):
            skill_names.add(name)
        if not isinstance(description, str) or not 1 <= len(description) <= 240:
            errors.append(f"{relative}: description must contain 1-240 characters")

        agent_manifest = path.parent / "agents" / "openai.yaml"
        expected_policy = (
            "  allow_implicit_invocation: true"
            if path.parent.name == "poland"
            else "  allow_implicit_invocation: false"
        )
        try:
            agent_lines = agent_manifest.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            errors.append(f"{agent_manifest.relative_to(ROOT).as_posix()}: {exc}")
        else:
            policy_lines = [
                line
                for line in agent_lines
                if "allow_implicit_invocation:" in line
            ]
            if "policy:" not in agent_lines or policy_lines != [expected_policy]:
                errors.append(
                    f"{agent_manifest.relative_to(ROOT).as_posix()}: "
                    "only the Poland router may be implicitly invoked in Codex"
                )
    if len(skill_names) != EXPECTED_SKILL_COUNT:
        errors.append(f"expected {EXPECTED_SKILL_COUNT} skills, found {len(skill_names)}")

    try:
        cursor = read_json(ROOT / ".cursor-plugin" / "plugin.json")
        if cursor.get("name") != PLUGIN_ID or cursor.get("version") != VERSION:
            errors.append("Cursor manifest name/version differs")
        if cursor.get("repository") != REPOSITORY:
            errors.append("Cursor repository must point to standalone source")
        if cursor.get("homepage") != REPOSITORY:
            errors.append("Cursor homepage must point to standalone source")
        if cursor.get("skills") != "./skills/":
            errors.append("Cursor manifest must explicitly bind repository-root skills")
        if cursor.get("mcpServers") != "./.codex-mcp.json":
            errors.append("Cursor manifest must explicitly bind the bundled MCP config")
        logo = cursor.get("logo")
        if not isinstance(logo, str) or not (ROOT / logo).is_file():
            errors.append("Cursor logo must resolve to a repository file")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f".cursor-plugin/plugin.json: {exc}")

    try:
        package = read_json(ROOT / "package.json")
        if package.get("name") != "poland-agent-skills" or package.get("version") != VERSION:
            errors.append("package.json name/version differs")
        pi = package.get("pi")
        pi_skills = pi.get("skills") if isinstance(pi, dict) else None
        expected_pi = {f"./skills/{name}" for name in skill_names}
        if (
            not isinstance(pi_skills, list)
            or any(not isinstance(item, str) for item in pi_skills)
            or set(pi_skills) != expected_pi
            or len(pi_skills) != len(expected_pi)
        ):
            errors.append(
                "package.json pi.skills must exactly match "
                f"the {EXPECTED_SKILL_COUNT} skill directories"
            )
        packaged_files = package.get("files")
        required_package_entries = {
            ".agents",
            ".claude-plugin",
            ".codex-mcp.json",
            ".codex-plugin",
            ".cursor-plugin",
            ".mcp.json",
            "CHANGELOG.md",
            "CONTRIBUTING.md",
            "DISCLAIMER.md",
            "LICENSE",
            "PRIVACY.md",
            "README.md",
            "SECURITY.md",
            "SOURCES.md",
            "SUPPORT.md",
            "TERMS.md",
            "agents",
            "assets",
            "data",
            "docs",
            "lib/*.py",
            "mcp/*.py",
            "references",
            "schemas",
            "scripts/*.py",
            "skills",
        }
        packaged_file_set = (
            set(packaged_files)
            if isinstance(packaged_files, list)
            and all(isinstance(item, str) for item in packaged_files)
            else None
        )
        if packaged_file_set is None or not required_package_entries.issubset(packaged_file_set):
            errors.append("package.json files must preserve the complete runtime and host companions")
        elif {"lib", "mcp", "scripts"} & packaged_file_set:
            errors.append("package.json must not package Python cache directories")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"package.json: {exc}")

    try:
        codex_mcp = read_json(ROOT / ".codex-mcp.json")["mcpServers"]["poland"]
        claude_mcp = read_json(ROOT / ".mcp.json")["mcpServers"]["poland"]
        if (
            codex_mcp.get("command") != "python3"
            or codex_mcp.get("args") != ["-I", "-B", "./mcp/server.py"]
            or codex_mcp.get("cwd") != "."
        ):
            errors.append(".codex-mcp.json does not match the public companion contract")
        if (
            claude_mcp.get("command") != "${POLAND_PYTHON:-python3}"
            or claude_mcp.get("args")
            != ["-I", "-B", "${CLAUDE_PLUGIN_ROOT}/mcp/server.py"]
            or claude_mcp.get("cwd") != "${CLAUDE_PLUGIN_ROOT}"
        ):
            errors.append(".mcp.json does not match the Claude plugin-root contract")
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        errors.append(f"MCP configuration: {exc}")

    icon_path = ROOT / "assets" / "icon.png"
    if icon_path.is_file():
        errors.extend(validate_png(icon_path))
    try:
        prompt = read_json(ROOT / "assets" / "icon-prompt.json")
        if prompt.get("schema") != "capability_workbench.plugin_icon_prompt.v2":
            errors.append("icon prompt must use schema v2")
        hero = prompt.get("semantic_hero")
        if (
            not isinstance(hero, dict)
            or not hero
            or any(not isinstance(value, str) or not value.strip() for value in hero.values())
        ):
            errors.append("icon prompt must declare exactly one non-empty semantic hero")
        support_cue = prompt.get("support_cue")
        if support_cue is not None and (
            not isinstance(support_cue, dict)
            or not support_cue
            or any(not isinstance(value, str) or not value.strip() for value in support_cue.values())
        ):
            errors.append("icon prompt support cue must be null or one non-empty object")
        if not isinstance(prompt.get("brand_source"), dict):
            errors.append("icon prompt must declare brand provenance")
        if prompt.get("plugin_name") != PLUGIN_ID:
            errors.append("icon prompt plugin_name must match the package")
        if prompt.get("recommended_asset_path") != "assets/icon.png":
            errors.append("icon prompt must point to assets/icon.png")
        avoid = prompt.get("avoid")
        avoid_text = " ".join(avoid).casefold() if isinstance(avoid, list) and all(
            isinstance(item, str) for item in avoid
        ) else ""
        if "map" not in avoid_text or (
            "geographic" not in avoid_text and "country outline" not in avoid_text
        ):
            errors.append("icon prompt must explicitly prohibit maps and geographic outlines")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"assets/icon-prompt.json: {exc}")

    try:
        provenance = (ROOT / "assets" / "ASSET_PROVENANCE.md").read_text(encoding="utf-8").casefold()
        for phrase in ("open folded ribbon", "support cue: none", "no map or geographic border"):
            if phrase not in provenance:
                errors.append(f"asset provenance must preserve icon contract: {phrase}")
    except OSError as exc:
        errors.append(f"assets/ASSET_PROVENANCE.md: {exc}")

    for schema_path in sorted((ROOT / "schemas").glob("*.schema.json")):
        try:
            schema = read_json(schema_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{schema_path.relative_to(ROOT).as_posix()}: {exc}")
            continue
        expected_id = f"{REPOSITORY}/blob/main/schemas/{schema_path.name}"
        if schema.get("$id") != expected_id:
            errors.append(f"{schema_path.relative_to(ROOT).as_posix()}: stale $id")

    errors.extend(f"data contract: {item}" for item in validate_datasets(ROOT / "data"))

    cli = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "poland.py"), "validate"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if cli.returncode != 0:
        errors.append(f"CLI bundle validation failed: {cli.stderr or cli.stdout}")

    doctor_environment = os.environ.copy()
    doctor_environment.pop("POLAND_PYTHON", None)

    def invoke_doctor(host: str, *extra: str) -> tuple[dict[str, Any] | None, str | None]:
        try:
            preflight = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(ROOT / "scripts" / "poland.py"),
                    "doctor",
                    "--host",
                    host,
                    *extra,
                ],
                cwd=ROOT,
                env=doctor_environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=45,
            )
        except subprocess.TimeoutExpired:
            return None, "timeout"
        try:
            preflight_payload = strict_json_loads(preflight.stdout)
            receipt = preflight_payload["result"]
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            return None, "invalid_receipt"
        return receipt if isinstance(receipt, dict) else None, (
            None if isinstance(receipt, dict) else "invalid_receipt"
        )

    for host in ("codex", "claude", "cursor", "pi"):
        receipt, failure = invoke_doctor(host)
        receipt_valid = (
            receipt is not None
            and receipt.get("schema") == "poland.doctor_receipt.v1"
            and receipt.get("valid") is True
        )
        if not receipt_valid and host != "pi":
            filename = ".mcp.json" if host == "claude" else ".codex-mcp.json"
            with tempfile.TemporaryDirectory(prefix="poland-doctor-") as directory:
                target = str(Path(directory) / filename)
                receipt, fallback_failure = invoke_doctor(
                    host,
                    "--write-mcp-config",
                    target,
                )
            receipt_valid = (
                receipt is not None
                and receipt.get("schema") == "poland.doctor_receipt.v1"
                and receipt.get("valid") is True
                and receipt.get("checks", {}).get("generated_mcp_round_trip", {}).get("status")
                == "passed"
            )
            if receipt_valid:
                warnings.append(
                    f"{host} public launcher unavailable on this runner; "
                    "generated host-local companion preflight passed"
                )
            else:
                failure = fallback_failure or failure
        if not receipt_valid:
            suffix = f" ({failure})" if failure else ""
            errors.append(f"{host} package/MCP preflight failed on this runner{suffix}")
            continue
        if receipt.get("checks", {}).get("host_plugin_discovery") != "not_checked":
            errors.append(f"{host} preflight must not claim native host discovery")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    onboarding_phrases = (
        "Ask Your Agent",
        "codex plugin marketplace add Xopoko/poland",
        "/plugin install poland@poland",
        "not installed by default",
    )
    for phrase in onboarding_phrases:
        if phrase not in readme:
            errors.append(f"README missing public onboarding phrase: {phrase}")

    files = tracked_files()
    for relative in files:
        if "__pycache__" in relative.parts or relative.suffix == ".pyc":
            errors.append(f"generated Python artifact is tracked: {relative.as_posix()}")
        if relative.suffix.lower() not in TEXT_SUFFIXES:
            continue
        path = ROOT / relative
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if relative.as_posix() != "scripts/validate_package.py" and ABSOLUTE_PATH.search(text):
            errors.append(f"machine-specific absolute path in {relative.as_posix()}")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"possible secret material in {relative.as_posix()}")

    result = {
        "schema": "poland.package_validation.v1",
        "valid": not errors,
        "counts": {
            "skills": len(skill_names),
            "sources": len(read_json(ROOT / "data" / "sources.json").get("sources", [])),
            "errors": len(errors),
            "warnings": len(warnings),
        },
        "errors": sorted(errors),
        "warnings": sorted(warnings),
    }
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
