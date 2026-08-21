"""Strict, dependency-free validation for the Poland plugin data bundle.

The JSON Schema files are publication contracts. This module mirrors their
closed object shapes at runtime without requiring a third-party validator.
Errors contain only public dataset paths and stable reason text.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


DATASET_FILES = {
    "sources": "sources.json",
    "scenarios": "scenarios.json",
    "terms": "terms.json",
    "regions": "regions.json",
    "action-boundaries": "action-boundaries.json",
    "digital-channels": "digital-channels.json",
}

SCHEMA_VERSION = "1.0.0"
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TOKEN_PATTERN = re.compile(r"^[a-z0-9]+(?:[_-][a-z0-9]+)*$")
DOMAIN_PATTERN = re.compile(r"^[a-z0-9.-]+$")
LANGUAGE_PATTERN = re.compile(r"^[a-z]{2,3}(?:-[A-Z]{2})?$")

JURISDICTIONS = {"national", "eu", "voivodeship", "powiat", "gmina"}
ACCESS_MODES = {"public", "authenticated", "credentialed_api"}
EFFECTS = {"informational", "personal_record", "consequential"}
SOURCE_AUTOMATION_MODES = {
    "human_in_loop_operator",
    "public_read_only",
    "public_read_only_handoff",
    "prohibited_external_effect",
    "user_handoff_then_stop",
}
BOUNDARY_AUTOMATION_MODES = {
    "confirmation_gated_external_effect",
    "public_read_only",
    "task_scoped_assistance",
    "user_only_restricted",
}
CHANNEL_KINDS = {
    "application_portal",
    "appointment_portal",
    "correspondence",
    "identity_signature",
    "information_portal",
    "mobile_app",
    "open_data_api",
    "personal_account",
    "public_registry",
}
CHANNEL_ACCESS_SCOPES = {"authenticated", "credentialed_api", "mixed", "public"}

SOURCE_FIELDS = {
    "id",
    "title",
    "authority",
    "url",
    "domains",
    "jurisdiction",
    "localities",
    "languages",
    "topics",
    "access",
    "effect",
    "automation",
    "last_verified",
    "freshness_days",
    "notes",
    "publisher",
    "source_tier",
    "source_kind",
    "accessed_at",
    "publication_date",
    "modified_date",
    "effective_from",
    "effective_to",
    "status",
    "locator",
}
SCENARIO_FIELDS = {
    "id",
    "purpose",
    "keywords",
    "owner_skill_ids",
    "composition",
    "required_parameters",
    "optional_parameters",
    "source_ids",
    "local_source_topic",
    "stop_before",
    "escalate_when",
}
TERM_FIELDS = {"id", "polish_ascii", "english", "aliases", "source_ids"}
REGION_FIELDS = {"id", "name", "administrative_centres"}
BOUNDARY_FIELDS = {"id", "automation", "allowed", "requires_confirmation", "never"}
CHANNEL_FIELDS = {
    "id",
    "name",
    "channel_kind",
    "source_ids",
    "access_scope",
    "public_surface",
    "protected_surface",
    "authentication_categories",
    "agent_mode",
    "stop_before",
    "live_verify",
    "notes",
}


def _error(errors: list[str], path: str, reason: str) -> None:
    errors.append(f"{path}: {reason}")


def _object(
    value: Any,
    path: str,
    fields: set[str],
    errors: list[str],
) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        _error(errors, path, "expected object")
        return None
    for key in sorted(fields - set(value)):
        _error(errors, f"{path}.{key}", "required field missing")
    for key in sorted(set(value) - fields):
        _error(errors, f"{path}.{key}", "unsupported field")
    return value


def _string(
    value: Any,
    path: str,
    errors: list[str],
    *,
    minimum: int = 1,
    maximum: int,
    pattern: re.Pattern[str] | None = None,
    choices: set[str] | None = None,
) -> str | None:
    if not isinstance(value, str):
        _error(errors, path, "expected string")
        return None
    if not minimum <= len(value) <= maximum:
        _error(errors, path, f"length must be from {minimum} to {maximum}")
        return None
    if pattern is not None and pattern.fullmatch(value) is None:
        _error(errors, path, "invalid format")
        return None
    if choices is not None and value not in choices:
        _error(errors, path, "unsupported value")
        return None
    return value


def _integer(
    value: Any,
    path: str,
    errors: list[str],
    *,
    minimum: int,
    maximum: int,
) -> int | None:
    if not isinstance(value, int) or isinstance(value, bool):
        _error(errors, path, "expected integer")
        return None
    if not minimum <= value <= maximum:
        _error(errors, path, f"value must be from {minimum} to {maximum}")
        return None
    return value


def _date_string(value: Any, path: str, errors: list[str]) -> str | None:
    checked = _string(value, path, errors, maximum=10)
    if checked is None:
        return None
    try:
        parsed = date.fromisoformat(checked)
    except ValueError:
        _error(errors, path, "expected ISO date")
        return None
    if parsed.isoformat() != checked:
        _error(errors, path, "expected ISO date")
        return None
    return checked


def _nullable_date(value: Any, path: str, errors: list[str]) -> str | None:
    if value is None:
        return None
    return _date_string(value, path, errors)


def _https_url(value: Any, path: str, errors: list[str]) -> str | None:
    checked = _string(value, path, errors, maximum=2048)
    if checked is None:
        return None
    parsed = urlsplit(checked)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
    ):
        _error(errors, path, "expected credential-free HTTPS URL")
        return None
    return checked


def _string_array(
    value: Any,
    path: str,
    errors: list[str],
    *,
    minimum: int,
    maximum: int,
    item_maximum: int,
    pattern: re.Pattern[str] | None = None,
) -> list[str] | None:
    if not isinstance(value, list):
        _error(errors, path, "expected array")
        return None
    if not minimum <= len(value) <= maximum:
        _error(errors, path, f"item count must be from {minimum} to {maximum}")
    checked: list[str] = []
    for index, item in enumerate(value):
        result = _string(
            item,
            f"{path}[{index}]",
            errors,
            maximum=item_maximum,
            pattern=pattern,
        )
        if result is not None:
            checked.append(result)
    if len(checked) == len(value) and len(set(checked)) != len(checked):
        _error(errors, path, "duplicate values are not allowed")
    return checked


def _object_array(
    value: Any,
    path: str,
    errors: list[str],
    *,
    minimum: int,
    maximum: int,
) -> list[Any] | None:
    if not isinstance(value, list):
        _error(errors, path, "expected array")
        return None
    if not minimum <= len(value) <= maximum:
        _error(errors, path, f"item count must be from {minimum} to {maximum}")
    return value


def _schema_version(value: Any, path: str, errors: list[str]) -> None:
    checked = _string(value, path, errors, maximum=len(SCHEMA_VERSION))
    if checked is not None and checked != SCHEMA_VERSION:
        _error(errors, path, "unsupported schema version")


def _unique_record_ids(records: list[Any], path: str, errors: list[str]) -> None:
    seen: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict) or not isinstance(record.get("id"), str):
            continue
        record_id = record["id"]
        if record_id in seen:
            _error(errors, f"{path}[{index}].id", "duplicate record id")
        seen.add(record_id)


def _validate_sources(payload: Any, errors: list[str]) -> None:
    root = _object(
        payload,
        "sources.json",
        {"schema_version", "registry_version", "description", "sources"},
        errors,
    )
    if root is None:
        return
    _schema_version(root.get("schema_version"), "sources.json.schema_version", errors)
    _date_string(root.get("registry_version"), "sources.json.registry_version", errors)
    _string(root.get("description"), "sources.json.description", errors, maximum=1000)
    records = _object_array(root.get("sources"), "sources.json.sources", errors, minimum=1, maximum=512)
    if records is None:
        return
    for index, record in enumerate(records):
        path = f"sources.json.sources[{index}]"
        item = _object(record, path, SOURCE_FIELDS, errors)
        if item is None:
            continue
        _string(item.get("id"), f"{path}.id", errors, maximum=80, pattern=SLUG_PATTERN)
        _string(item.get("title"), f"{path}.title", errors, maximum=300)
        _string(item.get("authority"), f"{path}.authority", errors, maximum=240)
        url = _https_url(item.get("url"), f"{path}.url", errors)
        domains = _string_array(
            item.get("domains"),
            f"{path}.domains",
            errors,
            minimum=1,
            maximum=16,
            item_maximum=253,
            pattern=DOMAIN_PATTERN,
        )
        _string(
            item.get("jurisdiction"),
            f"{path}.jurisdiction",
            errors,
            maximum=20,
            choices=JURISDICTIONS,
        )
        _string_array(
            item.get("localities"),
            f"{path}.localities",
            errors,
            minimum=0,
            maximum=64,
            item_maximum=80,
            pattern=SLUG_PATTERN,
        )
        _string_array(
            item.get("languages"),
            f"{path}.languages",
            errors,
            minimum=1,
            maximum=32,
            item_maximum=6,
            pattern=LANGUAGE_PATTERN,
        )
        _string_array(
            item.get("topics"),
            f"{path}.topics",
            errors,
            minimum=1,
            maximum=64,
            item_maximum=80,
            pattern=SLUG_PATTERN,
        )
        _string(
            item.get("access"),
            f"{path}.access",
            errors,
            maximum=32,
            choices=ACCESS_MODES,
        )
        _string(
            item.get("effect"),
            f"{path}.effect",
            errors,
            maximum=32,
            choices=EFFECTS,
        )
        _string(
            item.get("automation"),
            f"{path}.automation",
            errors,
            maximum=32,
            choices=SOURCE_AUTOMATION_MODES,
        )
        _date_string(item.get("last_verified"), f"{path}.last_verified", errors)
        _integer(
            item.get("freshness_days"),
            f"{path}.freshness_days",
            errors,
            minimum=1,
            maximum=365,
        )
        _string(item.get("notes"), f"{path}.notes", errors, maximum=1000)
        _string(item.get("publisher"), f"{path}.publisher", errors, maximum=240)
        _string(
            item.get("source_tier"),
            f"{path}.source_tier",
            errors,
            maximum=2,
            choices={"T0", "T1", "T2"},
        )
        _string(
            item.get("source_kind"),
            f"{path}.source_kind",
            errors,
            maximum=32,
            choices={"legal_text", "official_guidance", "official_service", "official_registry"},
        )
        _date_string(item.get("accessed_at"), f"{path}.accessed_at", errors)
        _nullable_date(item.get("publication_date"), f"{path}.publication_date", errors)
        _nullable_date(item.get("modified_date"), f"{path}.modified_date", errors)
        effective_from = _nullable_date(item.get("effective_from"), f"{path}.effective_from", errors)
        effective_to = _nullable_date(item.get("effective_to"), f"{path}.effective_to", errors)
        if effective_from is not None and effective_to is not None and effective_from > effective_to:
            _error(errors, f"{path}.effective_to", "must not precede effective_from")
        _string(
            item.get("status"),
            f"{path}.status",
            errors,
            maximum=16,
            choices={"active", "superseded", "unavailable"},
        )
        locator = _object(item.get("locator"), f"{path}.locator", {"type", "value"}, errors)
        if locator is not None:
            _string(
                locator.get("type"),
                f"{path}.locator.type",
                errors,
                maximum=16,
                choices={"page", "heading", "article", "paragraph", "annex", "table_row", "form_field"},
            )
            _string(locator.get("value"), f"{path}.locator.value", errors, maximum=240)
        if url is not None and domains:
            host = (urlsplit(url).hostname or "").lower().rstrip(".")
            if not any(host == domain or host.endswith("." + domain) for domain in domains):
                _error(errors, f"{path}.url", "host is outside declared domains")
    _unique_record_ids(records, "sources.json.sources", errors)


def _validate_scenarios(payload: Any, errors: list[str]) -> None:
    root = _object(
        payload,
        "scenarios.json",
        {"schema_version", "description", "scenarios"},
        errors,
    )
    if root is None:
        return
    _schema_version(root.get("schema_version"), "scenarios.json.schema_version", errors)
    _string(root.get("description"), "scenarios.json.description", errors, maximum=1000)
    records = _object_array(root.get("scenarios"), "scenarios.json.scenarios", errors, minimum=1, maximum=256)
    if records is None:
        return
    for index, record in enumerate(records):
        path = f"scenarios.json.scenarios[{index}]"
        item = _object(record, path, SCENARIO_FIELDS, errors)
        if item is None:
            continue
        _string(item.get("id"), f"{path}.id", errors, maximum=80, pattern=SLUG_PATTERN)
        _string(item.get("purpose"), f"{path}.purpose", errors, maximum=500)
        _string_array(
            item.get("keywords"),
            f"{path}.keywords",
            errors,
            minimum=1,
            maximum=32,
            item_maximum=120,
        )
        owners = _string_array(
            item.get("owner_skill_ids"),
            f"{path}.owner_skill_ids",
            errors,
            minimum=1,
            maximum=8,
            item_maximum=80,
            pattern=SLUG_PATTERN,
        )
        composition = _string(
            item.get("composition"),
            f"{path}.composition",
            errors,
            maximum=8,
            choices={"single", "multi"},
        )
        required = _string_array(
            item.get("required_parameters"),
            f"{path}.required_parameters",
            errors,
            minimum=1,
            maximum=32,
            item_maximum=80,
            pattern=TOKEN_PATTERN,
        )
        optional = _string_array(
            item.get("optional_parameters"),
            f"{path}.optional_parameters",
            errors,
            minimum=0,
            maximum=32,
            item_maximum=80,
            pattern=TOKEN_PATTERN,
        )
        _string_array(
            item.get("source_ids"),
            f"{path}.source_ids",
            errors,
            minimum=1,
            maximum=32,
            item_maximum=80,
            pattern=SLUG_PATTERN,
        )
        _string(
            item.get("local_source_topic"),
            f"{path}.local_source_topic",
            errors,
            maximum=80,
            pattern=SLUG_PATTERN,
        )
        _string_array(
            item.get("stop_before"),
            f"{path}.stop_before",
            errors,
            minimum=1,
            maximum=32,
            item_maximum=120,
            pattern=TOKEN_PATTERN,
        )
        _string_array(
            item.get("escalate_when"),
            f"{path}.escalate_when",
            errors,
            minimum=1,
            maximum=32,
            item_maximum=120,
            pattern=TOKEN_PATTERN,
        )
        if required is not None and optional is not None and set(required) & set(optional):
            _error(errors, path, "required and optional parameters must be disjoint")
        if owners is not None and composition == "single" and len(owners) != 1:
            _error(errors, path, "single composition must have exactly one owner")
        if owners is not None and composition == "multi" and len(owners) < 2:
            _error(errors, path, "multi composition must have at least two owners")
    _unique_record_ids(records, "scenarios.json.scenarios", errors)


def _validate_terms(payload: Any, errors: list[str]) -> None:
    root = _object(payload, "terms.json", {"schema_version", "terms"}, errors)
    if root is None:
        return
    _schema_version(root.get("schema_version"), "terms.json.schema_version", errors)
    records = _object_array(root.get("terms"), "terms.json.terms", errors, minimum=1, maximum=512)
    if records is None:
        return
    for index, record in enumerate(records):
        path = f"terms.json.terms[{index}]"
        item = _object(record, path, TERM_FIELDS, errors)
        if item is None:
            continue
        _string(item.get("id"), f"{path}.id", errors, maximum=80, pattern=SLUG_PATTERN)
        _string(item.get("polish_ascii"), f"{path}.polish_ascii", errors, maximum=240)
        _string(item.get("english"), f"{path}.english", errors, maximum=300)
        _string_array(
            item.get("aliases"),
            f"{path}.aliases",
            errors,
            minimum=0,
            maximum=32,
            item_maximum=120,
        )
        _string_array(
            item.get("source_ids"),
            f"{path}.source_ids",
            errors,
            minimum=1,
            maximum=32,
            item_maximum=80,
            pattern=SLUG_PATTERN,
        )
    _unique_record_ids(records, "terms.json.terms", errors)


def _validate_regions(payload: Any, errors: list[str]) -> None:
    root = _object(
        payload,
        "regions.json",
        {"schema_version", "last_verified", "regions"},
        errors,
    )
    if root is None:
        return
    _schema_version(root.get("schema_version"), "regions.json.schema_version", errors)
    _date_string(root.get("last_verified"), "regions.json.last_verified", errors)
    records = _object_array(root.get("regions"), "regions.json.regions", errors, minimum=16, maximum=16)
    if records is None:
        return
    for index, record in enumerate(records):
        path = f"regions.json.regions[{index}]"
        item = _object(record, path, REGION_FIELDS, errors)
        if item is None:
            continue
        _string(item.get("id"), f"{path}.id", errors, maximum=80, pattern=SLUG_PATTERN)
        _string(item.get("name"), f"{path}.name", errors, maximum=120)
        _string_array(
            item.get("administrative_centres"),
            f"{path}.administrative_centres",
            errors,
            minimum=1,
            maximum=4,
            item_maximum=120,
        )
    _unique_record_ids(records, "regions.json.regions", errors)


def _validate_action_boundaries(payload: Any, errors: list[str]) -> None:
    root = _object(
        payload,
        "action-boundaries.json",
        {"schema_version", "default_boundary", "boundaries", "global_never"},
        errors,
    )
    if root is None:
        return
    _schema_version(root.get("schema_version"), "action-boundaries.json.schema_version", errors)
    default_boundary = _string(
        root.get("default_boundary"),
        "action-boundaries.json.default_boundary",
        errors,
        maximum=80,
        pattern=SLUG_PATTERN,
    )
    records = _object_array(
        root.get("boundaries"),
        "action-boundaries.json.boundaries",
        errors,
        minimum=1,
        maximum=16,
    )
    automations: list[str] = []
    if records is not None:
        for index, record in enumerate(records):
            path = f"action-boundaries.json.boundaries[{index}]"
            item = _object(record, path, BOUNDARY_FIELDS, errors)
            if item is None:
                continue
            _string(item.get("id"), f"{path}.id", errors, maximum=80, pattern=SLUG_PATTERN)
            automation = _string(
                item.get("automation"),
                f"{path}.automation",
                errors,
                maximum=48,
                choices=BOUNDARY_AUTOMATION_MODES,
            )
            if automation is not None:
                automations.append(automation)
            for field, minimum in (("allowed", 1), ("requires_confirmation", 0), ("never", 1)):
                _string_array(
                    item.get(field),
                    f"{path}.{field}",
                    errors,
                    minimum=minimum,
                    maximum=64,
                    item_maximum=120,
                    pattern=TOKEN_PATTERN,
                )
        _unique_record_ids(records, "action-boundaries.json.boundaries", errors)
    if len(set(automations)) != len(automations):
        _error(errors, "action-boundaries.json.boundaries", "duplicate automation values are not allowed")
    boundary_ids = {
        record["id"]
        for record in records or []
        if isinstance(record, dict) and isinstance(record.get("id"), str)
    }
    if default_boundary is not None and boundary_ids and default_boundary not in boundary_ids:
        _error(errors, "action-boundaries.json.default_boundary", "does not reference a boundary id")
    _string_array(
        root.get("global_never"),
        "action-boundaries.json.global_never",
        errors,
        minimum=1,
        maximum=128,
        item_maximum=160,
        pattern=TOKEN_PATTERN,
    )


def _validate_digital_channels(payload: Any, errors: list[str]) -> None:
    root = _object(
        payload,
        "digital-channels.json",
        {"schema_version", "description", "channels"},
        errors,
    )
    if root is None:
        return
    _schema_version(root.get("schema_version"), "digital-channels.json.schema_version", errors)
    _string(root.get("description"), "digital-channels.json.description", errors, maximum=1000)
    records = _object_array(
        root.get("channels"),
        "digital-channels.json.channels",
        errors,
        minimum=1,
        maximum=128,
    )
    if records is None:
        return
    for index, record in enumerate(records):
        path = f"digital-channels.json.channels[{index}]"
        item = _object(record, path, CHANNEL_FIELDS, errors)
        if item is None:
            continue
        _string(item.get("id"), f"{path}.id", errors, maximum=80, pattern=SLUG_PATTERN)
        _string(item.get("name"), f"{path}.name", errors, maximum=200)
        _string(
            item.get("channel_kind"),
            f"{path}.channel_kind",
            errors,
            maximum=32,
            choices=CHANNEL_KINDS,
        )
        _string_array(
            item.get("source_ids"),
            f"{path}.source_ids",
            errors,
            minimum=1,
            maximum=16,
            item_maximum=80,
            pattern=SLUG_PATTERN,
        )
        access_scope = _string(
            item.get("access_scope"),
            f"{path}.access_scope",
            errors,
            maximum=32,
            choices=CHANNEL_ACCESS_SCOPES,
        )
        public_surface = _string_array(
            item.get("public_surface"),
            f"{path}.public_surface",
            errors,
            minimum=1,
            maximum=64,
            item_maximum=120,
            pattern=TOKEN_PATTERN,
        )
        protected_surface = _string_array(
            item.get("protected_surface"),
            f"{path}.protected_surface",
            errors,
            minimum=0,
            maximum=64,
            item_maximum=120,
            pattern=TOKEN_PATTERN,
        )
        authentication_categories = _string_array(
            item.get("authentication_categories"),
            f"{path}.authentication_categories",
            errors,
            minimum=0,
            maximum=32,
            item_maximum=120,
            pattern=TOKEN_PATTERN,
        )
        agent_mode = _string(
            item.get("agent_mode"),
            f"{path}.agent_mode",
            errors,
            maximum=32,
            choices=SOURCE_AUTOMATION_MODES,
        )
        _string_array(
            item.get("stop_before"),
            f"{path}.stop_before",
            errors,
            minimum=1,
            maximum=64,
            item_maximum=120,
            pattern=TOKEN_PATTERN,
        )
        _string_array(
            item.get("live_verify"),
            f"{path}.live_verify",
            errors,
            minimum=1,
            maximum=64,
            item_maximum=120,
            pattern=TOKEN_PATTERN,
        )
        _string(item.get("notes"), f"{path}.notes", errors, maximum=800)
        if access_scope == "public" and authentication_categories:
            _error(errors, f"{path}.authentication_categories", "public channel must not require authentication")
        if protected_surface and agent_mode == "public_read_only":
            _error(errors, f"{path}.agent_mode", "protected surface requires a fail-closed agent mode")
        if access_scope in {"authenticated", "credentialed_api"} and not protected_surface:
            _error(errors, f"{path}.protected_surface", "protected channel must name its user-only surface")
        if public_surface is not None and not public_surface:
            _error(errors, f"{path}.public_surface", "at least one public capability is required")
    _unique_record_ids(records, "digital-channels.json.channels", errors)


VALIDATORS = {
    "sources": _validate_sources,
    "scenarios": _validate_scenarios,
    "terms": _validate_terms,
    "regions": _validate_regions,
    "action-boundaries": _validate_action_boundaries,
    "digital-channels": _validate_digital_channels,
}


def _source_ids(payload: Any) -> set[str]:
    if not isinstance(payload, dict) or not isinstance(payload.get("sources"), list):
        return set()
    return {
        item["id"]
        for item in payload["sources"]
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def _validate_source_references(
    payload: Any,
    *,
    dataset_file: str,
    record_key: str,
    known_sources: set[str],
    errors: list[str],
) -> None:
    if not isinstance(payload, dict) or not isinstance(payload.get(record_key), list):
        return
    for record_index, record in enumerate(payload[record_key]):
        if not isinstance(record, dict) or not isinstance(record.get("source_ids"), list):
            continue
        for source_index, source_id in enumerate(record["source_ids"]):
            if isinstance(source_id, str) and source_id not in known_sources:
                _error(
                    errors,
                    f"{dataset_file}.{record_key}[{record_index}].source_ids[{source_index}]",
                    "unknown source reference",
                )


def validate_dataset_payload(name: str, payload: Any) -> list[str]:
    """Validate one parsed dataset payload and return deterministic errors."""

    validator = VALIDATORS.get(name)
    if validator is None:
        return ["dataset: unsupported dataset name"]
    errors: list[str] = []
    validator(payload, errors)
    return sorted(set(errors))


def validate_payloads(payloads: Mapping[str, Any]) -> list[str]:
    """Validate all parsed datasets, including cross-dataset references."""

    errors: list[str] = []
    for name in sorted(set(DATASET_FILES) - set(payloads)):
        _error(errors, DATASET_FILES[name], "dataset missing")
    for name in sorted(set(payloads) - set(DATASET_FILES)):
        _error(errors, str(name), "unsupported dataset")
    for name in DATASET_FILES:
        if name in payloads:
            VALIDATORS[name](payloads[name], errors)

    known_sources = _source_ids(payloads.get("sources"))
    _validate_source_references(
        payloads.get("scenarios"),
        dataset_file="scenarios.json",
        record_key="scenarios",
        known_sources=known_sources,
        errors=errors,
    )
    _validate_source_references(
        payloads.get("terms"),
        dataset_file="terms.json",
        record_key="terms",
        known_sources=known_sources,
        errors=errors,
    )
    _validate_source_references(
        payloads.get("digital-channels"),
        dataset_file="digital-channels.json",
        record_key="channels",
        known_sources=known_sources,
        errors=errors,
    )
    return sorted(set(errors))


def validate_datasets(data_root: str | Path) -> list[str]:
    """Read and validate every canonical Poland dataset under ``data_root``."""

    root = Path(data_root)
    payloads: dict[str, Any] = {}
    errors: list[str] = []
    for name, filename in DATASET_FILES.items():
        path = root / filename
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            _error(errors, filename, "file missing")
            continue
        except UnicodeDecodeError:
            _error(errors, filename, "expected UTF-8 JSON")
            continue
        try:
            payloads[name] = json.loads(text)
        except json.JSONDecodeError as exc:
            _error(errors, filename, f"invalid JSON at line {exc.lineno} column {exc.colno}")
    errors.extend(validate_payloads(payloads))
    return sorted(set(errors))


__all__ = [
    "DATASET_FILES",
    "validate_dataset_payload",
    "validate_datasets",
    "validate_payloads",
]
