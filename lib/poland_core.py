#!/usr/bin/env python3
"""Validated offline knowledge and planning primitives for the Poland plugin."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

from contract_validation import validate_payloads


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PLUGIN_ROOT / "data"
SCHEMA_ROOT = PLUGIN_ROOT / "schemas"
DATA_FILES = {
    "sources": "sources.json",
    "scenarios": "scenarios.json",
    "terms": "terms.json",
    "regions": "regions.json",
    "actions": "action-boundaries.json",
    "channels": "digital-channels.json",
}
EXPECTED_VERSIONS = {
    "sources": "1.0.0",
    "scenarios": "1.0.0",
    "terms": "1.0.0",
    "regions": "1.0.0",
    "actions": "1.0.0",
    "channels": "1.0.0",
}
OFFICIAL_DOMAIN_SUFFIXES = {
    "biznes.gov.pl",
    "ceidg.gov.pl",
    "edu.gov.pl",
    "duw.pl",
    "eli.gov.pl",
    "europa.eu",
    "gdansk.pl",
    "gov.pl",
    "krakow.pl",
    "mos.cudzoziemcy.gov.pl",
    "nfz.gov.pl",
    "pfron.org.pl",
    "pip.gov.pl",
    "policja.pl",
    "podatki.gov.pl",
    "praca.gov.pl",
    "rf.gov.pl",
    "strazgraniczna.pl",
    "stat.gov.pl",
    "uke.gov.pl",
    "um.warszawa.pl",
    "uokik.gov.pl",
    "warszawa19115.pl",
    "wroclaw.pl",
    "zus.pl",
}
SOURCE_REQUIRED = {
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
ROUTE_FACT_FIELDS = {
    "age_band",
    "authority_category",
    "benefit_name",
    "citizenship_group",
    "complaint_stage",
    "contract_type",
    "counterparty_type",
    "current_country",
    "current_location_category",
    "current_status",
    "current_status_category",
    "delivery_channel",
    "destination_voivodeship_or_unknown",
    "document_type",
    "education_stage",
    "employer_location",
    "gmina",
    "household_context",
    "insurance_context",
    "intended_arrival_date",
    "issuing_country",
    "language",
    "matter",
    "move_basis",
    "need_type",
    "problem_type",
    "procedure",
    "purpose",
    "requested_effect",
    "receiving_authority_category",
    "residence_status",
    "safe_to_speak",
    "sector",
    "system",
    "tax_year",
    "target_date",
    "target_procedure",
    "urgent",
    "voivodeship",
}
ROUTE_PROFILE_KEYS = {"facts"}
MAX_LITERAL_QUERY_LENGTH = 160
ABSTRACT_QUERY_PATTERN = re.compile(r"^[A-Za-z][A-Za-z _-]{0,159}$")
RESPONSE_CONTRACT = "poland.response.v1"


class PolandDataError(ValueError):
    """Raised when bundled data or caller input violates the plugin contract."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "INVALID_INPUT",
        message_key: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message_key = message_key or f"error.{code.lower()}"
        self.details = details or {}

    def as_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message_key": self.message_key,
            "details": self.details,
        }


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PolandDataError(f"missing required file: {path.relative_to(PLUGIN_ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise PolandDataError(
            f"invalid JSON in {path.relative_to(PLUGIN_ROOT)} at line {exc.lineno}"
        ) from exc


def load_dataset(name: str) -> dict[str, Any]:
    if name not in DATA_FILES:
        raise PolandDataError(f"unknown dataset: {name}")
    payload = _read_json(DATA_ROOT / DATA_FILES[name])
    if not isinstance(payload, dict):
        raise PolandDataError(f"{DATA_FILES[name]} must contain an object")
    return payload


def normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def _sensitive_text_reason(value: str) -> str | None:
    if any(char in value for char in "\r\n\x00"):
        return "control_characters"
    if re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", value):
        return "email_like"
    if re.search(r"\b\d{9,}\b", value):
        return "long_identifier_like"
    if re.search(r"\b[A-Z]{2}\d{7}\b", value):
        return "document_identifier_like"
    if re.search(
        r"(?i)\b(?:password|passwd|otp|one[- ]time code|access[_ -]?token|iban)\b\s*[:=]\s*\S+",
        value,
    ):
        return "secret_like"
    return None


def validate_public_literal(
    value: Any,
    field: str,
    *,
    allow_empty: bool = True,
    max_length: int = MAX_LITERAL_QUERY_LENGTH,
) -> str:
    if not isinstance(value, str):
        raise PolandDataError(
            f"{field} must be a string",
            details={"field": field},
        )
    stripped = value.strip()
    if not stripped and not allow_empty:
        raise PolandDataError(
            f"{field} must not be empty",
            details={"field": field},
        )
    if len(value) > max_length:
        raise PolandDataError(
            f"{field} exceeds the literal-search limit",
            code="INPUT_TOO_LARGE",
            details={"field": field, "max_length": max_length},
        )
    reason = _sensitive_text_reason(value)
    if reason:
        raise PolandDataError(
            f"{field} appears to contain personal or secret data",
            code="SENSITIVE_INPUT_REJECTED",
            details={"field": field, "reason": reason},
        )
    return stripped


def validate_literal_query(query: Any) -> str:
    literal = validate_public_literal(query, "query", allow_empty=False)
    if not ABSTRACT_QUERY_PATTERN.fullmatch(literal):
        raise PolandDataError(
            "query must be an abstract intent using ASCII letters, spaces, hyphens, or underscores",
            code="NON_ABSTRACT_INPUT_REJECTED",
            details={"field": "query"},
        )
    return literal


def validate_route_profile(profile: Any) -> dict[str, Any]:
    if profile in (None, {}):
        return {"facts": {}}
    if not isinstance(profile, dict):
        raise PolandDataError("route profile must be an object")
    unknown_top = set(profile) - ROUTE_PROFILE_KEYS
    if unknown_top:
        raise PolandDataError(
            "route profile contains unsupported fields",
            code="UNSUPPORTED_FIELD",
            details={"fields": sorted(unknown_top)},
        )
    facts = profile.get("facts", {})
    if not isinstance(facts, dict):
        raise PolandDataError("route profile facts must be an object")
    unknown_facts = set(facts) - ROUTE_FACT_FIELDS
    if unknown_facts:
        raise PolandDataError(
            "route profile contains unsupported fact fields",
            code="UNSUPPORTED_FIELD",
            details={"fields": sorted(unknown_facts)},
        )
    validated: dict[str, Any] = {}
    for key, value in facts.items():
        if value is None or isinstance(value, bool):
            validated[key] = value
            continue
        if not isinstance(value, str):
            raise PolandDataError(
                "route fact values must be strings, booleans, or null",
                details={"field": key},
            )
        if len(value) > 120:
            raise PolandDataError(
                "route fact value exceeds the categorical limit",
                code="INPUT_TOO_LARGE",
                details={"field": key, "max_length": 120},
            )
        reason = _sensitive_text_reason(value)
        if reason:
            raise PolandDataError(
                "route fact appears to contain personal or secret data",
                code="SENSITIVE_INPUT_REJECTED",
                details={"field": key, "reason": reason},
            )
        if key == "tax_year":
            if not re.fullmatch(r"\d{4}", value):
                raise PolandDataError(
                    "tax_year must be a four-digit year category",
                    code="NON_ABSTRACT_INPUT_REJECTED",
                    details={"field": key},
                )
        elif key not in {"target_date", "intended_arrival_date"} and not re.fullmatch(
            r"[A-Za-z][A-Za-z0-9_-]{0,119}", value
        ):
            raise PolandDataError(
                "route facts must use abstract category identifiers",
                code="NON_ABSTRACT_INPUT_REJECTED",
                details={"field": key},
            )
        validated[key] = value
    nationality = validated.get("citizenship_group")
    if nationality not in (
        None,
        "polish",
        "eu_eea_swiss",
        "third_country",
        "stateless_or_unknown",
    ):
        raise PolandDataError(
            "citizenship_group must use a supported abstract category",
            details={"field": "citizenship_group"},
        )
    for field in ("urgent", "safe_to_speak"):
        if field in validated and validated[field] not in {True, False, None}:
            raise PolandDataError(
                f"{field} must be true, false, or null",
                details={"field": field},
            )
    voivodeship = validated.get("voivodeship")
    if voivodeship is not None:
        known_regions = {item["id"] for item in _records(load_dataset("regions"), "regions", "regions")}
        if voivodeship not in known_regions:
            raise PolandDataError(
                "voivodeship must be a bundled region identifier",
                details={"field": "voivodeship"},
            )
    for field in ("target_date", "intended_arrival_date"):
        if validated.get(field):
            _parse_iso_date(validated[field], field)
    return {"facts": validated}


def _parse_iso_date(value: Any, label: str) -> date:
    if not isinstance(value, str):
        raise PolandDataError(f"{label} must be an ISO date")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise PolandDataError(f"{label} must be an ISO date") from exc


def _is_official_host(host: str) -> bool:
    lowered = host.lower().rstrip(".")
    return any(lowered == suffix or lowered.endswith("." + suffix) for suffix in OFFICIAL_DOMAIN_SUFFIXES)


def _host_matches_declared(host: str, domains: Iterable[str]) -> bool:
    lowered = host.lower().rstrip(".")
    return any(
        lowered == domain.lower().rstrip(".")
        or lowered.endswith("." + domain.lower().rstrip("."))
        for domain in domains
    )


def _records(payload: dict[str, Any], key: str, dataset: str) -> list[dict[str, Any]]:
    values = payload.get(key)
    if not isinstance(values, list) or any(not isinstance(item, dict) for item in values):
        raise PolandDataError(f"{dataset}.{key} must be an array of objects")
    return values


def all_sources() -> list[dict[str, Any]]:
    return _records(load_dataset("sources"), "sources", "sources")


def source_index() -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in all_sources() if isinstance(item.get("id"), str)}


def all_digital_channels() -> list[dict[str, Any]]:
    return _records(load_dataset("channels"), "channels", "digital-channels")


def digital_channels_for_sources(source_ids: Iterable[str]) -> list[dict[str, Any]]:
    """Return deterministic channel profiles backed by any supplied source ID."""
    wanted = {str(source_id) for source_id in source_ids}
    if not wanted:
        return []
    profiles = [
        dict(channel)
        for channel in all_digital_channels()
        if wanted & {str(source_id) for source_id in channel.get("source_ids", [])}
    ]
    return sorted(profiles, key=lambda item: item["id"])


def _source_view(source: dict[str, Any]) -> dict[str, Any]:
    result = dict(source)
    channels = digital_channels_for_sources([str(source.get("id", ""))])
    if channels:
        result["digital_channels"] = channels
    return result


def get_source(source_id: str) -> dict[str, Any]:
    source = source_index().get(source_id)
    if source is None:
        raise PolandDataError(f"unknown source id: {source_id}")
    return _source_view(source)


def search_sources(
    query: str = "",
    *,
    topic: str | None = None,
    access: str | None = None,
    jurisdiction: str | None = None,
    locality: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 100:
        raise PolandDataError("limit must be an integer from 1 to 100")
    query = validate_public_literal(query, "query")
    topic = validate_public_literal(topic or "", "topic", max_length=80)
    locality = validate_public_literal(locality or "", "locality", max_length=80)
    needle = normalize_text(query)
    topic_n = normalize_text(topic)
    locality_n = normalize_text(locality)
    matches: list[tuple[int, dict[str, Any]]] = []
    for source in all_sources():
        if access and source.get("access") != access:
            continue
        if jurisdiction and source.get("jurisdiction") != jurisdiction:
            continue
        topics = [str(item) for item in source.get("topics", [])]
        if topic_n and topic_n not in {normalize_text(item) for item in topics}:
            continue
        localities = [str(item) for item in source.get("localities", [])]
        if locality_n and locality_n not in {normalize_text(item) for item in localities}:
            continue
        channel_profiles = digital_channels_for_sources([str(source.get("id", ""))])
        haystack = normalize_text(
            " ".join(
                [
                    str(source.get("id", "")),
                    str(source.get("title", "")),
                    str(source.get("authority", "")),
                    str(source.get("notes", "")),
                    json.dumps(channel_profiles, ensure_ascii=True, sort_keys=True),
                    *topics,
                    *localities,
                ]
            )
        )
        if needle and needle not in haystack:
            continue
        score = 0
        if needle:
            if needle in normalize_text(str(source.get("title", ""))):
                score += 4
            if needle in normalize_text(str(source.get("id", ""))):
                score += 3
            score += sum(1 for token in needle.split() if token in haystack)
        matches.append((score, _source_view(source)))
    matches.sort(key=lambda item: (-item[0], item[1]["id"]))
    return [item for _, item in matches[:limit]]


def _scenario_records() -> list[dict[str, Any]]:
    return _records(load_dataset("scenarios"), "scenarios", "scenarios")


def _scenario_view(scenario: dict[str, Any]) -> dict[str, Any]:
    """Project evidence-first scenario data into the planning interface."""
    purpose = str(scenario.get("purpose", scenario.get("title", scenario.get("id", ""))))
    required = [str(item) for item in scenario.get("required_parameters", scenario.get("intake", []))]
    stop_before = [str(item) for item in scenario.get("stop_before", [])]
    source_ids = [str(item) for item in scenario.get("source_ids", [])]
    return {
        **scenario,
        "title": str(scenario.get("title", purpose)),
        "keywords": list(
            dict.fromkeys(
                [
                    str(scenario.get("id", "")).replace("-", " "),
                    purpose,
                    str(scenario.get("local_source_topic", "")),
                    *map(str, scenario.get("keywords", [])),
                ]
            )
        ),
        "intake": required,
        "source_ids": source_ids,
        "digital_channels": digital_channels_for_sources(source_ids),
        "phases": scenario.get("phases") or [
            {
                "id": "intake",
                "title": "Resolve material facts",
                "actions": [f"Confirm {field.replace('_', ' ')}" for field in required],
            },
            {
                "id": "verify",
                "title": "Verify authority and current instructions",
                "actions": [
                    "Open the listed official sources",
                    "Confirm locality, channel, form, and deadline at action time",
                ],
            },
            {
                "id": "prepare",
                "title": "Prepare a reviewable draft or document checklist",
                "actions": [
                    "Separate verified facts, assumptions, and missing evidence",
                    "Keep identifiers and document scans outside every plugin input and output",
                ],
            },
            {
                "id": "human-action",
                "title": "Complete human-controlled steps",
                "actions": [f"Stop before {item.replace('_', ' ')}" for item in stop_before]
                or ["Review any consequential action before it occurs"],
            },
        ],
    }


def _profile_value(profile: dict[str, Any], field: str) -> Any:
    if isinstance(profile.get("facts"), dict):
        profile = profile["facts"]
    aliases = {
        "citizenship_group": (
            ("citizenship_group",),
            ("nationality_group",),
        ),
        "nationality_group": (
            ("nationality_group",),
            ("citizenship_group",),
        ),
        "current_status": (("current_status",), ("current_status_category",)),
        "current_status_category": (("current_status_category",), ("current_status",)),
        "current_location": (("current_location_category",),),
        "country_of_residence": (("current_country",),),
        "voivodeship_if_in_poland": (("voivodeship",),),
        "deadline": (("target_date",),),
    }
    for path in aliases.get(field, ((field,),)):
        current: Any = profile
        for part in path:
            if not isinstance(current, dict) or part not in current:
                current = None
                break
            current = current[part]
        if current not in (None, "", [], {}):
            return current
    return None


def _as_of_date(as_of: str | date | None) -> date:
    if as_of is None:
        return datetime.now(timezone.utc).date()
    if isinstance(as_of, date):
        return as_of
    return _parse_iso_date(as_of, "as_of")


def _source_freshness_record(source: dict[str, Any], target: date) -> dict[str, Any]:
    verified = _parse_iso_date(source.get("last_verified"), f"{source.get('id')}.last_verified")
    window = source.get("freshness_days")
    if not isinstance(window, int) or isinstance(window, bool) or window < 1:
        raise PolandDataError(f"{source.get('id')}.freshness_days must be positive")
    age = (target - verified).days
    effective_from = (
        _parse_iso_date(source["effective_from"], f"{source.get('id')}.effective_from")
        if source.get("effective_from")
        else None
    )
    effective_to = (
        _parse_iso_date(source["effective_to"], f"{source.get('id')}.effective_to")
        if source.get("effective_to")
        else None
    )
    if source.get("status") != "active":
        status = "inactive"
    elif (effective_from and target < effective_from) or (effective_to and target > effective_to):
        status = "out_of_effective_period"
    elif age < 0:
        status = "future"
    elif age <= window:
        status = "fresh"
    elif age <= window * 2:
        status = "review_due"
    else:
        status = "stale"
    return {
        "source_id": source["id"],
        "last_verified": verified.isoformat(),
        "age_days": age,
        "freshness_days": window,
        "status": status,
        "record_status": source.get("status"),
        "effective_from": source.get("effective_from"),
        "effective_to": source.get("effective_to"),
        "effect": source["effect"],
    }


def evidence_gate(
    source_ids: Iterable[str],
    *,
    as_of: str | date | None = None,
    conflicts: Iterable[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    target = _as_of_date(as_of)
    sources = source_index()
    records = []
    for source_id in source_ids:
        source = sources.get(str(source_id))
        if source is None:
            raise PolandDataError(
                "unknown source id in evidence gate",
                code="UNKNOWN_SOURCE",
            )
        records.append(_source_freshness_record(source, target))
    conflict_records = list(conflicts or [])
    statuses = {item["status"] for item in records}
    if conflict_records:
        state = "conflict"
        warning_codes = ["OFFICIAL_SOURCE_CONFLICT"]
    elif "inactive" in statuses:
        state = "unsupported_as_of"
        warning_codes = ["SOURCE_NOT_ACTIVE"]
    elif "out_of_effective_period" in statuses:
        state = "unsupported_as_of"
        warning_codes = ["SOURCE_OUTSIDE_EFFECTIVE_PERIOD"]
    elif "future" in statuses:
        state = "unsupported_as_of"
        warning_codes = ["UNSUPPORTED_AS_OF_DATE"]
    elif "stale" in statuses:
        state = "stale"
        warning_codes = ["STALE_PACKAGED_DATA"]
    elif "review_due" in statuses:
        state = "review_due"
        warning_codes = ["LIVE_VERIFICATION_RECOMMENDED"]
    else:
        state = "verified"
        warning_codes = []
    actionable = state == "verified"
    if actionable:
        usable_for = ["intent_routing", "checklist_composition", "source_discovery"]
        not_usable_for = ["eligibility_decision", "external_action"]
    else:
        usable_for = ["background", "intent_routing", "source_discovery"]
        not_usable_for = [
            "current_fee",
            "current_deadline",
            "submission_channel",
            "eligibility_decision",
            "external_action",
        ]
    return {
        "data_mode": "OFFLINE_PACKAGED_DATA",
        "as_of": target.isoformat(),
        "state": state,
        "actionable": actionable,
        "live_verification_required": state != "verified",
        "usable_for": usable_for,
        "not_usable_for": not_usable_for,
        "warnings": warning_codes,
        "sources": records,
        "conflicts": conflict_records,
    }


def _digital_channel_view(
    channel: dict[str, Any],
    *,
    as_of: str | date | None = None,
) -> dict[str, Any]:
    """Return a source-backed channel profile with an explicit safety state."""
    source_ids = [str(item) for item in channel.get("source_ids", [])]
    gate = evidence_gate(source_ids, as_of=as_of)
    if not gate["actionable"]:
        channel_state = "verification_required"
    elif channel.get("agent_mode") == "public_read_only":
        channel_state = "public_read_only"
    elif channel.get("agent_mode") == "public_read_only_handoff":
        channel_state = "public_read_only_handoff"
    else:
        channel_state = "public_metadata_only"
    sources = source_index()
    return {
        **channel,
        "channel_state": channel_state,
        "protected_interaction_supported": False,
        "evidence_gate": gate,
        "sources": [dict(sources[source_id]) for source_id in source_ids],
    }


def get_digital_channel(
    channel_id: str,
    *,
    as_of: str | date | None = None,
) -> dict[str, Any]:
    """Resolve one public channel descriptor without entering its protected UI."""
    safe_id = validate_public_literal(channel_id, "channel_id", allow_empty=False, max_length=80)
    if re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", safe_id) is None:
        raise PolandDataError(
            "channel_id must be a bundled channel identifier",
            code="INVALID_CHANNEL_ID",
            details={"field": "channel_id"},
        )
    channel = next((item for item in all_digital_channels() if item.get("id") == safe_id), None)
    if channel is None:
        raise PolandDataError(
            "unknown digital channel",
            code="UNKNOWN_DIGITAL_CHANNEL",
            details={"field": "channel_id"},
        )
    return _digital_channel_view(dict(channel), as_of=as_of)


def search_digital_channels(
    query: str = "",
    *,
    channel_kind: str | None = None,
    access_scope: str | None = None,
    limit: int = 20,
    as_of: str | date | None = None,
) -> list[dict[str, Any]]:
    """Search the bounded channel catalog; results never access personal accounts."""
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 100:
        raise PolandDataError(
            "limit must be an integer from 1 to 100",
            details={"field": "limit"},
        )
    safe_query = validate_public_literal(query, "query")
    safe_kind = validate_public_literal(channel_kind or "", "channel_kind", max_length=40)
    safe_access = validate_public_literal(access_scope or "", "access_scope", max_length=40)
    known_kinds = {
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
    known_access = {"authenticated", "credentialed_api", "mixed", "public"}
    if safe_kind and safe_kind not in known_kinds:
        raise PolandDataError(
            "unsupported channel_kind",
            code="INVALID_CHANNEL_FILTER",
            details={"field": "channel_kind"},
        )
    if safe_access and safe_access not in known_access:
        raise PolandDataError(
            "unsupported access_scope",
            code="INVALID_CHANNEL_FILTER",
            details={"field": "access_scope"},
        )
    needle = normalize_text(safe_query)
    matches: list[tuple[int, dict[str, Any]]] = []
    for channel in all_digital_channels():
        if safe_kind and channel.get("channel_kind") != safe_kind:
            continue
        if safe_access and channel.get("access_scope") != safe_access:
            continue
        haystack = normalize_text(
            " ".join(
                [
                    str(channel.get("id", "")),
                    str(channel.get("name", "")),
                    str(channel.get("channel_kind", "")),
                    str(channel.get("access_scope", "")),
                    str(channel.get("notes", "")),
                    *map(str, channel.get("public_surface", [])),
                    *map(str, channel.get("live_verify", [])),
                ]
            )
        )
        if needle and needle not in haystack:
            continue
        score = 0
        if needle:
            if needle in normalize_text(str(channel.get("name", ""))):
                score += 4
            if needle in normalize_text(str(channel.get("id", ""))):
                score += 3
            score += sum(1 for token in needle.split() if token in haystack)
        matches.append((score, _digital_channel_view(dict(channel), as_of=as_of)))
    matches.sort(key=lambda item: (-item[0], item[1]["id"]))
    return [item for _, item in matches[:limit]]


def route_scenario(
    query: str,
    profile: dict[str, Any] | None = None,
    *,
    as_of: str | date | None = None,
) -> dict[str, Any]:
    literal_query = validate_literal_query(query)
    safe_profile = validate_route_profile(profile)
    normalized = normalize_text(literal_query)
    scored: list[tuple[int, dict[str, Any]]] = []
    for raw_scenario in _scenario_records():
        scenario = _scenario_view(raw_scenario)
        if scenario.get("id") == literal_query:
            score = 1000
        else:
            terms = [str(scenario.get("title", "")), *map(str, scenario.get("keywords", []))]
            score = sum(3 if normalize_text(term) in normalized else 0 for term in terms if term)
            term_tokens = set(normalize_text(" ".join(terms)).split())
            score += sum(
                1
                for token in normalized.split()
                if token in term_tokens
            )
        if score:
            scored.append((score, scenario))
    if not scored:
        return {
            "schema_version": "poland.route.v1",
            "id": None,
            "route_state": "not_applicable",
            "match_truth": "false",
            "intent_candidates": [],
            "alternatives": [],
            "missing_intake": [],
            "parameter_states": {},
            "source_ids": [],
            "sources": [],
            "eligibility_assessed": False,
            "evidence_gate": evidence_gate([], as_of=as_of),
        }
    scored.sort(key=lambda item: (-item[0], item[1]["id"]))
    best = dict(scored[0][1])
    intake = [str(item) for item in best.get("intake", [])]
    missing_intake = [field for field in intake if _profile_value(safe_profile, field) is None]
    tied = [item[1]["id"] for item in scored if item[0] == scored[0][0]]
    gate = evidence_gate(
        best.get("source_ids", []),
        as_of=as_of,
        conflicts=best.get("conflicts", []),
    )
    best["missing_intake"] = missing_intake
    best["schema_version"] = "poland.route.v1"
    best["alternatives"] = [item[1]["id"] for item in scored[1:4]]
    sources = source_index()
    best["sources"] = [dict(sources[source_id]) for source_id in best.get("source_ids", [])]
    best["route_state"] = (
        "undetermined" if missing_intake or len(tied) > 1 or not gate["actionable"] else "candidate"
    )
    best["match_truth"] = "true" if best["route_state"] == "candidate" else "unknown"
    best["parameter_states"] = {
        field: "known" if _profile_value(safe_profile, field) is not None else "unknown"
        for field in intake
    }
    best["intent_candidates"] = tied
    best["eligibility_assessed"] = False
    best["evidence_gate"] = gate
    return best


def build_checklist(
    scenario_id: str,
    profile: dict[str, Any] | None = None,
    *,
    as_of: str | date | None = None,
) -> dict[str, Any]:
    if not isinstance(scenario_id, str) or not any(
        item.get("id") == scenario_id for item in _scenario_records()
    ):
        raise PolandDataError(
            "unknown scenario id",
            code="UNKNOWN_SCENARIO",
        )
    routed = route_scenario(scenario_id, profile, as_of=as_of)
    phases = routed.get("phases", [])
    if not isinstance(phases, list):
        raise PolandDataError(f"scenario {scenario_id} has invalid phases")
    allowed_phase_ids = {"intake", "verify", "prepare"}
    if routed["route_state"] == "candidate" and routed["evidence_gate"]["actionable"]:
        allowed_phase_ids.add("human-action")
    visible_phases = [phase for phase in phases if phase.get("id") in allowed_phase_ids]
    suppressed_phase_ids = [
        str(phase.get("id")) for phase in phases if phase.get("id") not in allowed_phase_ids
    ]
    return {
        "schema_version": "poland.checklist.v1",
        "scenario_id": routed["id"],
        "title": routed["title"],
        "owner_skill_ids": routed.get("owner_skill_ids", []),
        "route_state": routed["route_state"],
        "missing_intake": routed["missing_intake"],
        "phases": visible_phases,
        "suppressed_phase_ids": suppressed_phase_ids,
        "source_ids": routed.get("source_ids", []),
        "digital_channels": routed.get("digital_channels", []),
        "sources": routed["sources"],
        "evidence_gate": routed["evidence_gate"],
        "escalate_when": routed.get("escalate_when", []),
        "notice": (
            "Verify changing facts and the competent office at action time. "
            "This checklist is navigation support, not a decision or guarantee."
        ),
    }


def lookup_terms(query: str = "", limit: int = 20) -> list[dict[str, Any]]:
    if not 1 <= limit <= 100:
        raise PolandDataError("limit must be from 1 to 100")
    needle = normalize_text(validate_public_literal(query, "query"))
    terms = _records(load_dataset("terms"), "terms", "terms")
    results = []
    for item in terms:
        haystack = normalize_text(" ".join([
            *(str(item.get(key, "")) for key in ("id", "polish", "polish_ascii", "english", "meaning", "notes")),
            *map(str, item.get("aliases", [])),
        ]))
        if not needle or needle in haystack:
            results.append(dict(item))
    return results[:limit]


def list_regions(query: str = "") -> list[dict[str, Any]]:
    needle = normalize_text(validate_public_literal(query, "query", max_length=80))
    regions = _records(load_dataset("regions"), "regions", "regions")
    return [
        dict(item)
        for item in regions
        if not needle or needle in normalize_text(json.dumps(item, ensure_ascii=False))
    ]


def action_boundary(action: str) -> dict[str, Any]:
    if not isinstance(action, str) or not action.strip():
        raise PolandDataError("action must be a non-empty string")
    if len(action) > MAX_LITERAL_QUERY_LENGTH:
        raise PolandDataError(
            "action exceeds the literal-classification limit",
            code="INPUT_TOO_LARGE",
            details={"max_length": MAX_LITERAL_QUERY_LENGTH},
        )
    reason = _sensitive_text_reason(action)
    if reason:
        raise PolandDataError(
            "action appears to contain personal or secret data",
            code="SENSITIVE_INPUT_REJECTED",
            details={"reason": reason},
        )
    needle = normalize_text(action)
    actions = _records(load_dataset("actions"), "boundaries", "actions")
    by_id = {item["id"]: item for item in actions}
    prohibited = by_id["human-submit"]
    exact = next((item for item in actions if item.get("id") == action), None)
    if exact:
        return dict(exact)
    action_token = re.sub(r"[^a-z0-9]+", "_", needle).strip("_")
    prohibited_patterns = (
        r"\b(?:log\s*in|login|authenticat\w*|credential\w*|trusted\s+profile)\b",
        r"\b(?:otp|verification\s+code|session\s+cookie|api\s+key)\b",
        r"\b(?:book|reschedule|cancel)\b.*\bappointment\b",
        r"\b(?:upload|submit|send|pay|payment|sign|withdraw|amend)\b",
        r"\b(?:save|start|edit)\b.*\b(?:draft|application)\b",
        r"\bdownload\b.*\b(?:personal|document|record)\b",
        r"\b(?:read|copy)\b.*\b(?:email|record|document|code)\b",
        r"\bclick\s+through\b",
        r"\b(?:contact|message)\b.*\b(?:authority|employer|landlord)\b",
        r"\bcredentialed\s+api\b",
    )
    if action_token in set(prohibited.get("never", [])) or any(
        re.search(pattern, needle) for pattern in prohibited_patterns
    ):
        return {**prohibited, "matched_by": "hard_prohibition"}
    exact_allowed: list[dict[str, Any]] = []
    for item in actions:
        if action_token in set(item.get("allowed", [])) | set(item.get("requires_confirmation", [])):
            exact_allowed.append(item)
    if len(exact_allowed) == 1:
        return {**exact_allowed[0], "matched_by": "exact_policy_action"}
    return {**prohibited, "matched_by": "fail_closed_default"}


def freshness_report(as_of: str | date | None = None) -> dict[str, Any]:
    target = _as_of_date(as_of)
    records = []
    summary = {
        "fresh": 0,
        "review_due": 0,
        "stale": 0,
        "future": 0,
        "inactive": 0,
        "out_of_effective_period": 0,
    }
    for source in all_sources():
        record = _source_freshness_record(source, target)
        status = record["status"]
        summary[status] += 1
        records.append(record)
    return {
        "data_mode": "OFFLINE_PACKAGED_DATA",
        "as_of": target.isoformat(),
        "summary": summary,
        "sources": records,
    }


def evidence_receipt(
    source_id: str,
    result: str,
    *,
    content_sha256: str | None = None,
    locator_type: str = "page",
    locator_value: str | None = None,
    supports: Iterable[str] | None = None,
    effective_from: str | None = None,
    effective_to: str | None = None,
    conflicts: Iterable[dict[str, str]] | None = None,
    checked_at: datetime | None = None,
) -> dict[str, Any]:
    if result not in {"verified", "changed", "unavailable", "needs_review"}:
        raise PolandDataError("unsupported evidence result")
    source = get_source(source_id)
    if content_sha256 is not None and not re.fullmatch(r"[0-9a-f]{64}", content_sha256):
        raise PolandDataError("content_sha256 must be a lowercase SHA-256 hex digest")
    if locator_type not in {"page", "heading", "article", "paragraph", "annex", "table_row", "form_field"}:
        raise PolandDataError("unsupported evidence locator type")
    if locator_value is not None:
        if not isinstance(locator_value, str) or len(locator_value) > 240:
            raise PolandDataError("locator_value must be a string up to 240 characters")
        if _sensitive_text_reason(locator_value):
            raise PolandDataError(
                "locator_value appears to contain personal or secret data",
                code="SENSITIVE_INPUT_REJECTED",
            )
    supported_fields = sorted(set(supports or []))
    if not supported_fields:
        raise PolandDataError("supports must name at least one material claim field")
    if any(not re.fullmatch(r"[a-z0-9]+(?:[._-][a-z0-9]+)*", item) for item in supported_fields):
        raise PolandDataError("supports must contain stable field identifiers")
    effective_from = effective_from if effective_from is not None else source["effective_from"]
    effective_to = effective_to if effective_to is not None else source["effective_to"]
    if effective_from:
        _parse_iso_date(effective_from, "effective_from")
    if effective_to:
        _parse_iso_date(effective_to, "effective_to")
    if effective_from and effective_to and effective_from > effective_to:
        raise PolandDataError("effective_from must not be after effective_to")
    conflict_records = list(conflicts or [])
    for conflict in conflict_records:
        if not isinstance(conflict, dict) or set(conflict) != {"source_id", "conflict_type"}:
            raise PolandDataError("conflicts must contain source_id and conflict_type")
        get_source(conflict["source_id"])
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", conflict["conflict_type"]):
            raise PolandDataError("conflict_type must be a stable identifier")
    observed_at = checked_at or datetime.now(timezone.utc)
    receipt_seed = f"{source_id}|{observed_at.isoformat()}|{result}|{content_sha256 or ''}"
    gate = evidence_gate(
        [source_id],
        as_of=observed_at.date(),
        conflicts=conflict_records,
    )
    receipt = {
        "schema_version": "poland.evidence-receipt.v2",
        "receipt_id": "receipt-" + hashlib.sha256(receipt_seed.encode("utf-8")).hexdigest()[:20],
        "result": result,
        "source_id": source_id,
        "observed_at": observed_at.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "url": source["url"],
        "authority": source["authority"],
        "publisher": source.get("publisher", source["authority"]),
        "source_tier": source.get("source_tier", "T1"),
        "source_accessed_at": source.get("accessed_at", source["last_verified"]),
        "page_title": source["title"],
        "page_modified_at": None,
        "content_hash_sha256": content_sha256,
        "locator": {
            "type": locator_type if locator_value is not None else source["locator"]["type"],
            "value": locator_value if locator_value is not None else source["locator"]["value"],
        },
        "supports": supported_fields,
        "effective_period": {
            "from": effective_from,
            "to": effective_to,
        },
        "evidence_gate": gate,
        "effect_boundary": source["effect"],
        "conflicts": conflict_records,
    }
    return receipt


def citations_for(result: Any) -> list[dict[str, Any]]:
    """Return complete, deterministic citation objects for referenced sources."""
    source_ids: set[str] = set()

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            if isinstance(value.get("source_id"), str):
                source_ids.add(value["source_id"])
            if (
                isinstance(value.get("id"), str)
                and isinstance(value.get("url"), str)
                and isinstance(value.get("authority"), str)
            ):
                source_ids.add(value["id"])
            if isinstance(value.get("source_ids"), list):
                source_ids.update(
                    item for item in value["source_ids"] if isinstance(item, str)
                )
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(result)
    citations: list[dict[str, Any]] = []
    known = source_index()
    for source_id in sorted(source_ids):
        source = known.get(source_id)
        if source is None:
            continue
        citations.append(
            {
                "source_id": source_id,
                "title": source["title"],
                "url": source["url"],
                "authority": source["authority"],
                "publisher": source["publisher"],
                "source_tier": source["source_tier"],
                "accessed_at": source["accessed_at"],
                "effective_period": {
                    "from": source["effective_from"],
                    "to": source["effective_to"],
                },
                "locator": dict(source["locator"]),
            }
        )
    return citations


def _warning_codes(result: Any) -> list[str]:
    warnings: set[str] = set()

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            candidate = value.get("warnings")
            if isinstance(candidate, list):
                warnings.update(
                    item
                    for item in candidate
                    if isinstance(item, str) and re.fullmatch(r"[A-Z0-9_]+", item)
                )
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(result)
    return sorted(warnings)


def response_envelope(
    command: str,
    result: dict[str, Any] | list[dict[str, Any]],
    *,
    as_of: str | date | None = None,
) -> dict[str, Any]:
    if not isinstance(command, str) or not re.fullmatch(r"[a-z][a-z0-9._-]{0,79}", command):
        raise PolandDataError("invalid response command", code="INTERNAL_CONTRACT_ERROR")
    if not isinstance(result, (dict, list)):
        raise PolandDataError("response result must be an object or array", code="INTERNAL_CONTRACT_ERROR")
    result_as_of = result.get("as_of") if isinstance(result, dict) else None
    return {
        "contract": RESPONSE_CONTRACT,
        "ok": True,
        "command": command,
        "data_version": load_dataset("sources")["registry_version"],
        "data_mode": "OFFLINE_PACKAGED_DATA",
        "as_of": _as_of_date(result_as_of or as_of).isoformat(),
        "result": result,
        "warnings": _warning_codes(result),
        "citations": citations_for(result),
    }


def error_envelope(command: str, error: PolandDataError) -> dict[str, Any]:
    safe_command = command if re.fullmatch(r"[a-z][a-z0-9._-]{0,79}", command or "") else "invalid"
    return {
        "contract": RESPONSE_CONTRACT,
        "ok": False,
        "command": safe_command,
        "data_version": load_dataset("sources")["registry_version"],
        "data_mode": "OFFLINE_PACKAGED_DATA",
        "error": error.as_dict(),
    }


def validate_bundle(as_of: str | date | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    datasets: dict[str, dict[str, Any]] = {}
    for name, expected in EXPECTED_VERSIONS.items():
        try:
            payload = load_dataset(name)
            datasets[name] = payload
            if payload.get("schema_version") != expected:
                errors.append(f"{DATA_FILES[name]} schema_version must be {expected}")
        except PolandDataError as exc:
            errors.append(str(exc))
    contract_names = {
        "actions": "action-boundaries",
        "channels": "digital-channels",
    }
    contract_payloads = {
        contract_names.get(name, name): payload
        for name, payload in datasets.items()
    }
    errors.extend(validate_payloads(contract_payloads))
    schema_names = (
        "source-registry.schema.json",
        "scenario.schema.json",
        "term.schema.json",
        "region.schema.json",
        "action-boundary.schema.json",
        "digital-channel.schema.json",
        "evidence-receipt.schema.json",
        "response.schema.json",
    )
    for schema_name in schema_names:
        path = SCHEMA_ROOT / schema_name
        try:
            schema = _read_json(path)
            if not isinstance(schema, dict) or schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
                errors.append(f"{schema_name} must use JSON Schema draft 2020-12")
        except PolandDataError as exc:
            errors.append(str(exc))
    source_ids: set[str] = set()
    if "sources" in datasets:
        try:
            sources = _records(datasets["sources"], "sources", "sources")
        except PolandDataError as exc:
            errors.append(str(exc))
            sources = []
        for index, source in enumerate(sources):
            label = str(source.get("id", f"index-{index}"))
            missing = SOURCE_REQUIRED - set(source)
            if missing:
                errors.append(f"source {label} missing fields: {', '.join(sorted(missing))}")
                continue
            if not re.fullmatch(r"[a-z0-9][a-z0-9.-]{1,79}", str(source["id"])):
                errors.append(f"invalid source id: {source['id']}")
            if source["id"] in source_ids:
                errors.append(f"duplicate source id: {source['id']}")
            source_ids.add(source["id"])
            parsed = urlparse(str(source["url"]))
            domains = source["domains"]
            if parsed.scheme != "https" or not parsed.hostname:
                errors.append(f"source {label} must use an HTTPS URL")
            elif not isinstance(domains, list) or not domains:
                errors.append(f"source {label} domains must be a non-empty array")
            elif not _host_matches_declared(parsed.hostname, domains):
                errors.append(f"source {label} URL host is outside declared domains")
            elif not _is_official_host(parsed.hostname):
                errors.append(f"source {label} URL host is outside the official allowlist")
            for list_field in ("domains", "localities", "languages", "topics"):
                value = source[list_field]
                if not isinstance(value, list) or any(
                    not isinstance(item, str) for item in value
                ):
                    errors.append(f"source {label}.{list_field} must be an array of strings")
            if source["jurisdiction"] not in {"national", "eu", "voivodeship", "gmina"}:
                errors.append(f"source {label} has invalid jurisdiction")
            if source["access"] not in {"public", "authenticated", "credentialed_api"}:
                errors.append(f"source {label} has invalid access")
            if source["effect"] not in {"informational", "personal_record", "consequential"}:
                errors.append(f"source {label} has invalid effect")
            allowed_automation = {
                "public_read_only",
                "public_read_only_handoff",
                "prohibited_external_effect",
            }
            if source["automation"] not in allowed_automation:
                errors.append(f"source {label} has invalid automation")
            try:
                _parse_iso_date(source["last_verified"], f"{label}.last_verified")
            except PolandDataError as exc:
                errors.append(str(exc))
            freshness_days = source["freshness_days"]
            if (
                not isinstance(freshness_days, int)
                or isinstance(freshness_days, bool)
                or freshness_days < 1
            ):
                errors.append(f"source {label}.freshness_days must be positive")
    record_sets = (
        ("scenarios", "scenarios"),
        ("terms", "terms"),
        ("regions", "regions"),
        ("actions", "boundaries"),
        ("channels", "channels"),
    )
    for dataset_name, record_key in record_sets:
        if dataset_name not in datasets:
            continue
        try:
            records = _records(datasets[dataset_name], record_key, dataset_name)
        except PolandDataError as exc:
            errors.append(str(exc))
            continue
        seen: set[str] = set()
        for item in records:
            item_id = item.get("id")
            if not isinstance(item_id, str) or not item_id:
                errors.append(f"{dataset_name} record requires a string id")
                continue
            if item_id in seen:
                errors.append(f"duplicate {dataset_name} id: {item_id}")
            seen.add(item_id)
            for source_id in item.get("source_ids", []):
                if source_id not in source_ids:
                    errors.append(f"{dataset_name} {item_id} references unknown source: {source_id}")
            if dataset_name == "scenarios":
                unknown_parameters = (
                    set(item.get("required_parameters", []))
                    | set(item.get("optional_parameters", []))
                ) - ROUTE_FACT_FIELDS
                if unknown_parameters:
                    errors.append(
                        f"scenario {item_id} uses unsupported route parameters: "
                        + ", ".join(sorted(unknown_parameters))
                    )
                for owner in item.get("owner_skill_ids", []):
                    if not (PLUGIN_ROOT / "skills" / owner / "SKILL.md").is_file():
                        errors.append(f"scenario {item_id} references unknown owner skill: {owner}")
    if "regions" in datasets:
        try:
            region_count = len(_records(datasets["regions"], "regions", "regions"))
            if region_count != 16:
                errors.append(f"regions.json must contain 16 voivodeships, found {region_count}")
        except PolandDataError:
            pass
    if not errors:
        try:
            freshness = freshness_report(as_of)
            if freshness["summary"]["future"]:
                errors.append("source verification dates cannot be in the future")
            if freshness["summary"]["stale"]:
                warnings.append(f"{freshness['summary']['stale']} sources are stale")
        except PolandDataError as exc:
            errors.append(str(exc))
    counts = {
        "sources": len(datasets.get("sources", {}).get("sources", [])),
        "scenarios": len(datasets.get("scenarios", {}).get("scenarios", [])),
        "terms": len(datasets.get("terms", {}).get("terms", [])),
        "regions": len(datasets.get("regions", {}).get("regions", [])),
        "actions": len(datasets.get("actions", {}).get("boundaries", [])),
        "digital_channels": len(datasets.get("channels", {}).get("channels", [])),
    }
    digest = hashlib.sha256(
        json.dumps(datasets, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "data_mode": "OFFLINE_PACKAGED_DATA",
        "as_of": _as_of_date(as_of).isoformat(),
        "valid": not errors,
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
        "counts": counts,
        "bundle_sha256": digest,
    }


def overview() -> dict[str, Any]:
    validation = validate_bundle()
    return {
        "plugin": "poland",
        "version": "0.1.0",
        "model": "official-source-first",
        "data_mode": "OFFLINE_PACKAGED_DATA",
        "counts": validation["counts"],
        "interfaces": {
            "cli": "scripts/poland.py",
            "source_probe": "scripts/source_probe.py",
            "mcp": "mcp/server.py",
        },
        "policy_modes": [
            "public_read_only",
            "local_placeholder_only",
            "user_handoff_then_stop",
            "prohibited_external_effect",
        ],
        "notice": (
            "Navigation support only. Verify changing facts and competent locality at action time. "
            "The plugin never authenticates or performs external actions."
        ),
    }
