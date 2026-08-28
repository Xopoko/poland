#!/usr/bin/env python3
"""Validated offline knowledge and planning primitives for the Poland plugin."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
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
    "bfg.pl",
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
    "eu_efta_family_member_status",
    "gmina",
    "household_context",
    "insurance_context",
    "intended_arrival_date",
    "issuing_country",
    "language",
    "matter",
    "move_basis",
    "need_type",
    "pesel_status",
    "problem_type",
    "procedure",
    "powiat",
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
POLISH_LATIN_LETTERS = "A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż"
ABSTRACT_QUERY_PATTERN = re.compile(
    rf"^[{POLISH_LATIN_LETTERS}][{POLISH_LATIN_LETTERS} _-]{{0,159}}$"
)
ABSTRACT_CATEGORY_PATTERN = re.compile(
    rf"^[{POLISH_LATIN_LETTERS}][{POLISH_LATIN_LETTERS}0-9_-]{{0,119}}$"
)
ROUTER_CONTEXT_TOKENS = {"poland", "polish"}
RESPONSE_CONTRACT = "poland.response.v1"
FRESHNESS_STATUSES = (
    "fresh",
    "review_due",
    "stale",
    "future",
    "inactive",
    "out_of_effective_period",
)
MAX_REPAIR_QUEUE_PROJECTION = 64
ONTOLOGY_LAYERS = (
    "services",
    "evidence",
    "channels",
    "vocabulary",
    "geography",
    "safety",
    "ownership",
    "authorities",
)


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
    without_combining_marks = "".join(
        char for char in decomposed if not unicodedata.combining(char)
    )
    # LATIN SMALL LETTER L WITH STROKE does not decompose under NFKD.
    return without_combining_marks.replace("ł", "l")


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
            "query must be an abstract intent using Latin letters, including Polish diacritics, spaces, hyphens, or underscores",
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
        elif key not in {"target_date", "intended_arrival_date"} and not (
            ABSTRACT_CATEGORY_PATTERN.fullmatch(value)
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
    for field in ("eu_efta_family_member_status", "pesel_status"):
        if validated.get(field) not in (None, "present", "absent", "unknown"):
            raise PolandDataError(
                f"{field} must use present, absent, or unknown",
                details={"field": field},
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
                "title": "Complete checkpointed steps",
                "actions": [
                    (
                        f"Pause before {item.replace('_', ' ')}; classify the concrete "
                        "action against the action boundary, then complete its task-scope, "
                        "action-time-confirmation, or user-only handoff requirement"
                    )
                    for item in stop_before
                ]
                or ["Review any consequential action before it occurs"],
            },
        ],
        "stop_before_semantics": "pause_and_classify_checkpoint",
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


def _scenario_channel_selection(
    scenario: dict[str, Any],
    profile: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]] | None:
    """Resolve explicit source-bound channel rules without deciding eligibility."""
    rules = scenario.get("channel_rules")
    if not isinstance(rules, list) or not rules:
        return None
    compatible: list[tuple[dict[str, Any], list[str]]] = []
    matches: list[dict[str, Any]] = []
    for rule in rules:
        when = rule.get("when", {})
        if not isinstance(when, dict):
            raise PolandDataError("scenario channel rule has invalid conditions")
        missing: list[str] = []
        contradicted = False
        for field, allowed_values in when.items():
            if field not in ROUTE_FACT_FIELDS or not isinstance(allowed_values, list):
                raise PolandDataError("scenario channel rule uses an unsupported fact")
            value = _profile_value(profile, str(field))
            if value is None:
                missing.append(str(field))
            elif value not in allowed_values:
                contradicted = True
                break
        if contradicted:
            continue
        compatible.append((rule, missing))
        if not missing:
            matches.append(rule)

    if matches:
        specificity = max(len(rule.get("when", {})) for rule in matches)
        most_specific = sorted(
            (rule for rule in matches if len(rule.get("when", {})) == specificity),
            key=lambda item: str(item.get("id", "")),
        )
        if len(most_specific) > 1:
            return (
                {
                    "state": "unresolved",
                    "matched_rule_id": None,
                    "missing_facts": [],
                    "requirements": [],
                    "channel_ids": [],
                    "warnings": ["CHANNEL_RULES_AMBIGUOUS"],
                },
                [],
            )
        selected = most_specific[0]
        state = str(selected["state"])
        warning_by_state = {
            "verification_required": "CHANNEL_LIVE_VERIFICATION_REQUIRED",
            "unavailable": "REQUESTED_CHANNEL_UNAVAILABLE_FOR_PROFILE",
        }
        channel_ids = [str(item) for item in selected.get("channel_ids", [])]
        channel_by_id = {
            str(channel["id"]): channel for channel in all_digital_channels()
        }
        unknown_channels = sorted(set(channel_ids) - set(channel_by_id))
        if unknown_channels:
            raise PolandDataError("scenario channel rule references an unknown channel")
        selection = {
            "state": state,
            "matched_rule_id": str(selected["id"]),
            "missing_facts": [],
            "requirements": [str(item) for item in selected.get("requirements", [])],
            "channel_ids": channel_ids,
            "warnings": [warning_by_state[state]] if state in warning_by_state else [],
        }
        return selection, [dict(channel_by_id[channel_id]) for channel_id in channel_ids]

    if compatible:
        smallest_gap = min(len(missing) for _, missing in compatible)
        missing_facts = sorted(
            {
                field
                for _, missing in compatible
                if len(missing) == smallest_gap
                for field in missing
            }
        )
        state = "unresolved"
        warning = "CHANNEL_APPLICABILITY_UNRESOLVED"
    else:
        missing_facts = []
        state = "unavailable"
        warning = "REQUESTED_CHANNEL_UNAVAILABLE_FOR_PROFILE"
    return (
        {
            "state": state,
            "matched_rule_id": None,
            "missing_facts": missing_facts,
            "requirements": [],
            "channel_ids": [],
            "warnings": [warning],
        },
        [],
    )


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
    if effective_from and target < effective_from:
        effective_state = "not_yet_effective"
    elif effective_to and target > effective_to:
        effective_state = "expired"
    else:
        effective_state = "in_effect"
    if source.get("status") != "active":
        status = "inactive"
    elif effective_state != "in_effect":
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
        "effective_state": effective_state,
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
    elif not records:
        state = "insufficient_evidence"
        warning_codes = ["NO_SOURCE_EVIDENCE"]
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
        not_usable_for = [
            "eligibility_decision",
            "external_action_without_task_authorization_and_confirmation",
        ]
    elif records:
        usable_for = ["background", "intent_routing", "source_discovery"]
        not_usable_for = [
            "current_fee",
            "current_deadline",
            "submission_channel",
            "eligibility_decision",
            "external_action_until_live_verification",
        ]
    else:
        usable_for = []
        not_usable_for = [
            "background",
            "intent_routing",
            "checklist_composition",
            "source_discovery",
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
    elif channel.get("agent_mode") == "human_in_loop_operator":
        channel_state = "caller_owned_operator"
    elif channel.get("agent_mode") == "user_handoff_then_stop":
        channel_state = "user_handoff_then_stop"
    else:
        channel_state = "user_only_or_unsupported"
    sources = source_index()
    return {
        **channel,
        "channel_state": channel_state,
        "caller_owned_operator_eligible": channel.get("agent_mode") == "human_in_loop_operator",
        "bundled_interface_can_interact": False,
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


def _route_tokens(value: str) -> tuple[str, ...]:
    """Return deterministic ASCII-comparable tokens after Polish normalization."""
    return tuple(re.findall(r"[a-z0-9]+", normalize_text(value)))


def _contains_token_phrase(tokens: tuple[str, ...], phrase: tuple[str, ...]) -> bool:
    if not phrase or len(phrase) > len(tokens):
        return False
    width = len(phrase)
    return any(
        tokens[index : index + width] == phrase
        for index in range(len(tokens) - width + 1)
    )


def _is_acronym_variant(value: str, tokens: tuple[str, ...]) -> bool:
    compact = "".join(char for char in value if char.isalnum())
    return (
        len(tokens) == 1
        and len(compact) >= 3
        and compact.upper() == compact
        and any(char.isalpha() for char in compact)
    )


def _term_route_matches(query_tokens: tuple[str, ...]) -> list[dict[str, Any]]:
    """Resolve glossary concepts present in a query without a language dictionary."""
    matches: list[dict[str, Any]] = []
    for term in _records(load_dataset("terms"), "terms", "terms"):
        variants = [
            str(term.get("id", "")).replace("-", " "),
            str(term.get("polish_ascii", "")),
            str(term.get("english", "")),
            *map(str, term.get("aliases", [])),
        ]
        variant_matches: list[tuple[int, bool]] = []
        for variant in variants:
            phrase = _route_tokens(variant)
            if not _contains_token_phrase(query_tokens, phrase):
                continue
            acronym = _is_acronym_variant(variant, phrase)
            if len(phrase) >= 2 or acronym:
                variant_matches.append((len(phrase), acronym))
        if not variant_matches:
            continue
        best_width, acronym = max(variant_matches)
        matches.append(
            {
                "id": str(term.get("id", "")),
                "source_ids": {str(item) for item in term.get("source_ids", [])},
                "phrase_width": best_width,
                "acronym": acronym,
            }
        )
    return matches


def _scenario_applies_to_profile(
    scenario: dict[str, Any], profile: dict[str, Any]
) -> bool:
    """Reject only a scenario contradicted by a known abstract profile fact."""
    applicability = scenario.get("applicability", {})
    if not isinstance(applicability, dict):
        return False
    for field, allowed_values in applicability.items():
        if not isinstance(allowed_values, list):
            return False
        profile_value = _profile_value(profile, str(field))
        if profile_value is not None and profile_value not in allowed_values:
            return False
    return True


def _route_match_rows(
    raw_scenarios: list[dict[str, Any]],
    query_tokens: tuple[str, ...],
    normalized_query: str,
    profile: dict[str, Any],
) -> list[dict[str, Any]]:
    """Build confidence-qualified rows; weak one-token overlap is excluded."""
    candidate_scenarios = [
        scenario
        for scenario in raw_scenarios
        if _scenario_applies_to_profile(scenario, profile)
    ]
    scenario_tokens: dict[str, set[str]] = {}
    scenario_salient_tokens: dict[str, set[str]] = {}
    token_frequency: dict[str, int] = {}
    for scenario in candidate_scenarios:
        scenario_id = str(scenario.get("id", ""))
        corpus = " ".join(
            [
                scenario_id.replace("-", " "),
                str(scenario.get("purpose", "")),
                str(scenario.get("local_source_topic", "")).replace("-", " "),
                *map(str, scenario.get("keywords", [])),
            ]
        )
        tokens = set(_route_tokens(corpus))
        scenario_tokens[scenario_id] = tokens
        salient_corpus = " ".join(
            [
                scenario_id.replace("-", " "),
                str(scenario.get("local_source_topic", "")).replace("-", " "),
                *map(str, scenario.get("keywords", [])),
            ]
        )
        scenario_salient_tokens[scenario_id] = set(_route_tokens(salient_corpus))
        for token in tokens:
            token_frequency[token] = token_frequency.get(token, 0) + 1

    glossary_matches = _term_route_matches(query_tokens)
    rows: list[dict[str, Any]] = []
    query_token_set = set(query_tokens)
    broad_token_limit = max(3, len(candidate_scenarios) // 4)
    for raw_scenario in candidate_scenarios:
        scenario_id = str(raw_scenario.get("id", ""))
        id_phrase = normalize_text(scenario_id.replace("-", " "))
        exact_id = normalized_query in {normalize_text(scenario_id), id_phrase}
        direct_hits: list[tuple[int, bool]] = []
        for phrase_value in [
            scenario_id.replace("-", " "),
            *map(str, raw_scenario.get("keywords", [])),
        ]:
            phrase = _route_tokens(phrase_value)
            if not _contains_token_phrase(query_tokens, phrase):
                continue
            acronym = _is_acronym_variant(phrase_value, phrase)
            if len(phrase) >= 2 or acronym:
                direct_hits.append((len(phrase), acronym))

        source_ids = {str(item) for item in raw_scenario.get("source_ids", [])}
        glossary_hits: list[tuple[int, int, bool]] = []
        for term_match in glossary_matches:
            shared_sources = source_ids & term_match["source_ids"]
            if shared_sources:
                glossary_hits.append(
                    (
                        int(term_match["phrase_width"]),
                        len(shared_sources),
                        bool(term_match["acronym"]),
                    )
                )

        informative_overlap = {
            token
            for token in query_token_set & scenario_tokens[scenario_id]
            if len(token) >= 3
            and token not in ROUTER_CONTEXT_TOKENS
            and token_frequency.get(token, 0) <= broad_token_limit
        }
        salient_overlap = informative_overlap & scenario_salient_tokens[scenario_id]
        qualifies = bool(
            exact_id
            or direct_hits
            or glossary_hits
            or len(informative_overlap) >= 2
        )
        if not qualifies:
            continue
        overlap_weight = sum(
            max(1, broad_token_limit + 1 - token_frequency[token])
            for token in informative_overlap
        )
        score = (
            (10000 if exact_id else 0)
            + sum(
                40 + width * 4 + (6 if acronym else 0)
                for width, acronym in direct_hits
            )
            + sum(
                50 + width * 4 + shared_count * 8 + (6 if acronym else 0)
                for width, shared_count, acronym in glossary_hits
            )
            + len(informative_overlap) * 4
            + len(salient_overlap) * 12
            + overlap_weight
        )
        rows.append(
            {
                "score": score,
                "scenario": _scenario_view(raw_scenario),
                "exact_id": exact_id,
                "direct_hits": direct_hits,
                "glossary_hits": glossary_hits,
                "informative_overlap": informative_overlap,
                "salient_overlap": salient_overlap,
            }
        )
    rows.sort(key=lambda item: (-int(item["score"]), item["scenario"]["id"]))
    return rows


def _unresolved_route(
    *,
    as_of: str | date | None,
    route_state: str,
    match_truth: str,
    intent_candidates: list[str] | None = None,
    alternatives: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": "poland.route.v1",
        "id": None,
        "route_state": route_state,
        "match_truth": match_truth,
        "intent_candidates": intent_candidates or [],
        "alternatives": alternatives or [],
        "missing_intake": [],
        "parameter_states": {},
        "source_ids": [],
        "sources": [],
        "eligibility_assessed": False,
        "evidence_gate": evidence_gate([], as_of=as_of),
    }


def route_scenario(
    query: str,
    profile: dict[str, Any] | None = None,
    *,
    as_of: str | date | None = None,
) -> dict[str, Any]:
    literal_query = validate_literal_query(query)
    safe_profile = validate_route_profile(profile)
    normalized = normalize_text(literal_query)
    query_tokens = _route_tokens(literal_query)
    raw_scenarios = _scenario_records()
    exact_scenario = next(
        (
            scenario
            for scenario in raw_scenarios
            if normalized
            in {
                normalize_text(str(scenario.get("id", ""))),
                normalize_text(str(scenario.get("id", "")).replace("-", " ")),
            }
        ),
        None,
    )
    if exact_scenario is not None and not _scenario_applies_to_profile(
        exact_scenario, safe_profile
    ):
        return _unresolved_route(
            as_of=as_of,
            route_state="not_applicable",
            match_truth="false",
        )
    match_rows = _route_match_rows(
        raw_scenarios, query_tokens, normalized, safe_profile
    )
    if not match_rows:
        return _unresolved_route(
            as_of=as_of,
            route_state="not_applicable",
            match_truth="false",
        )

    top_score = int(match_rows[0]["score"])
    tied_rows = [row for row in match_rows if int(row["score"]) == top_score]
    single_token_ambiguity = len(query_tokens) == 1 and len(match_rows) > 1
    if len(tied_rows) > 1 or single_token_ambiguity:
        candidates = [
            str(row["scenario"]["id"])
            for row in (match_rows if single_token_ambiguity else tied_rows)
        ]
        return _unresolved_route(
            as_of=as_of,
            route_state="undetermined",
            match_truth="unknown",
            intent_candidates=candidates,
            alternatives=[str(row["scenario"]["id"]) for row in match_rows[:4]],
        )

    best = dict(match_rows[0]["scenario"])
    intake = [str(item) for item in best.get("intake", [])]
    missing_intake = [field for field in intake if _profile_value(safe_profile, field) is None]
    channel_selection_result = _scenario_channel_selection(best, safe_profile)
    if channel_selection_result is not None:
        channel_selection, selected_channels = channel_selection_result
        best["channel_selection"] = channel_selection
        best["digital_channels"] = selected_channels
        missing_intake = list(
            dict.fromkeys([*missing_intake, *channel_selection["missing_facts"]])
        )
    gate = evidence_gate(
        best.get("source_ids", []),
        as_of=as_of,
        conflicts=best.get("conflicts", []),
    )
    best["missing_intake"] = missing_intake
    best["schema_version"] = "poland.route.v1"
    best["alternatives"] = [str(row["scenario"]["id"]) for row in match_rows[1:4]]
    sources = source_index()
    best["sources"] = [dict(sources[source_id]) for source_id in best.get("source_ids", [])]
    channel_state = (
        best.get("channel_selection", {}).get("state")
        if isinstance(best.get("channel_selection"), dict)
        else None
    )
    channel_blocks = channel_state in {
        "unavailable",
        "unresolved",
        "verification_required",
    }
    best["route_state"] = (
        "undetermined"
        if missing_intake or not gate["actionable"] or channel_blocks
        else "candidate"
    )
    best["match_truth"] = "true" if best["route_state"] == "candidate" else "unknown"
    parameter_fields = list(dict.fromkeys([*intake, *missing_intake]))
    best["parameter_states"] = {
        field: "known" if _profile_value(safe_profile, field) is not None else "unknown"
        for field in parameter_fields
    }
    best["intent_candidates"] = [best["id"]]
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
    if routed.get("id") != scenario_id:
        raise PolandDataError(
            "scenario is not applicable to the supplied profile",
            code="SCENARIO_NOT_APPLICABLE",
            details={"scenario_id": scenario_id},
        )
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
    exact = next((item for item in actions if item.get("id") == action), None)
    if exact:
        return dict(exact)
    action_token = re.sub(r"[^a-z0-9]+", "_", needle).strip("_")
    exact_matches: list[tuple[dict[str, Any], str]] = []
    for item in actions:
        for disposition in ("allowed", "requires_confirmation", "never"):
            if action_token in set(item.get(disposition, [])):
                exact_matches.append((item, disposition))
    if len(exact_matches) == 1:
        item, disposition = exact_matches[0]
        return {
            **item,
            "matched_by": "exact_policy_action",
            "policy_action": action_token,
            "disposition": disposition,
        }

    # A user-completed authentication handoff followed by a named record task is
    # scoped assistance, not a request for the agent to authenticate.
    if re.search(r"\bafter\s+(?:i|the\s+user)\s+(?:log\s*in|authenticate)\b", needle):
        scoped = by_id["task-scoped-assistance"]
        if re.search(r"\b(?:read|inspect|review|open)\b.*\brecord\b", needle):
            policy_action = "read_task_relevant_personal_record"
        elif re.search(r"\b(?:enter|fill|type|correct)\b.*\b(?:form|field|application)\b", needle):
            policy_action = "enter_task_relevant_personal_data"
        else:
            policy_action = "resume_after_user_authentication"
        return {
            **scoped,
            "matched_by": "policy_pattern",
            "policy_action": policy_action,
            "disposition": "requires_confirmation",
        }
    if re.search(r"\bapproved\b.*\b(?:authenticated|credentialed)\b.*\bconnector\b", needle):
        scoped = by_id["task-scoped-assistance"]
        return {
            **scoped,
            "matched_by": "policy_pattern",
            "policy_action": "use_approved_authenticated_connector",
            "disposition": "requires_confirmation",
        }

    pattern_groups = (
        (
            "user-only-restricted",
            (
                ("login", r"\b(?:log\s+in(?:to)?|login|sign\s+in|authenticat\w*)\b"),
                ("read_credentials", r"\b(?:credential\w*|password|passkey|pin)\b"),
                ("read_verification_code", r"\b(?:otp|verification\s+code|recovery\s+code|session\s+cookie)\b"),
                ("pass_captcha", r"\bcaptcha\b"),
                ("bypass_2fa", r"\b(?:2fa|two[- ]factor)\b"),
                ("sign_as_user", r"\b(?:sign|signature)\b"),
                ("accept_declaration", r"\b(?:accept|attest|confirm)\b.*\b(?:declaration|truth|consent|terms|settlement)\b"),
                ("approve_final_payment_authorization", r"\b(?:approve|authorize)\b.*\b(?:bank|payment)\b"),
                ("withdraw_application", r"\bwithdraw\b"),
                ("perform_irreversible_destructive_action", r"\b(?:irreversible|permanent)\b.*\b(?:delete|close|destroy|erase)\b"),
                ("delete_external_account_or_record", r"\b(?:delete|erase)\b.*\b(?:account|record)\b"),
                ("place_emergency_call", r"\b(?:call|dial)\b.*\b(?:112|emergency)\b"),
                ("click_through_everything", r"\bclick\s+through\b"),
                ("use_unapproved_credentialed_api", r"\bcredentialed\s+api\b"),
                ("forge_document_signature_or_declaration", r"\b(?:forge|fake)\b"),
            ),
        ),
        (
            "task-scoped-assistance",
            (
                ("resume_after_user_authentication", r"\b(?:resume|continue)\b.*\b(?:after\s+login|authenticated|logged[- ]in)\b"),
                ("read_task_relevant_personal_record", r"\b(?:read|inspect|review|open)\b.*\b(?:personal\s+record|account\s+(?:record|balance)|case\s+(?:record|state)|medical\s+record|tax\s+(?:record|return)|contribution\s+record|insured[- ]person\s+record|certificate)\b"),
                ("inspect_task_relevant_correspondence", r"\b(?:read|inspect|review|open)\b.*\b(?:message|letter|correspondence|inbox)\b"),
                ("open_user_selected_personal_document", r"\b(?:read|inspect|review|open)\b.*\b(?:personal\s+document|identity\s+document|passport(?:\s+scan)?|residence\s+card|contract|statement)\b"),
                ("enter_task_relevant_personal_data", r"\b(?:enter|fill|type|correct)\b.*\b(?:personal\s+data|form|field|application)\b"),
            ),
        ),
        (
            "human-submit",
            (
                ("book_appointment", r"\bbook\b.*\bappointment\b"),
                ("reschedule_appointment", r"\breschedule\b.*\bappointment\b"),
                ("cancel_appointment", r"\bcancel\b.*\bappointment\b"),
                ("upload_document", r"\bupload\b"),
                ("download_personal_document", r"\bdownload\b"),
                ("submit_application", r"\bsubmit\b"),
                ("send_message", r"\bsend\b"),
                ("initiate_payment", r"\b(?:pay|payment)\b"),
                ("amend_application", r"\bamend\b"),
                ("save_server_side_draft", r"\bsave\b.*\bdraft\b"),
                ("start_application", r"\bstart\b.*\bapplication\b"),
                ("edit_application", r"\bedit\b.*\bapplication\b"),
                ("contact_authority", r"\b(?:contact|message)\b.*\b(?:authority|employer|landlord)\b"),
                ("create_external_account", r"\bcreate\b.*\baccount\b"),
                ("change_external_record", r"\b(?:change|update|correct)\b.*\b(?:external|official)\s+record\b"),
            ),
        ),
    )
    for boundary_id, patterns in pattern_groups:
        for policy_action, pattern in patterns:
            if re.search(pattern, needle):
                boundary = by_id[boundary_id]
                disposition = (
                    "requires_confirmation"
                    if policy_action in set(boundary.get("requires_confirmation", []))
                    else "never"
                    if policy_action in set(boundary.get("never", []))
                    else "allowed"
                )
                return {
                    **boundary,
                    "matched_by": "policy_pattern",
                    "policy_action": policy_action,
                    "disposition": disposition,
                }

    restricted = by_id["user-only-restricted"]
    return {
        **restricted,
        "matched_by": "fail_closed_default",
        "policy_action": None,
        "disposition": "never",
    }


def _verification_route(source: dict[str, Any]) -> str:
    automation = source.get("automation")
    if source.get("access") == "public" and automation == "public_read_only":
        return "source_probe"
    if source.get("access") == "public" and automation == "public_read_only_handoff":
        return "browser"
    return "manual_authority_review"


def _repair_next_step(issue_code: str) -> str:
    steps = {
        "SOURCE_VERIFICATION_DATE_IN_FUTURE": "correct_verification_metadata",
        "SOURCE_STALE": "reverify_material_claims",
        "SOURCE_REVIEW_DUE": "reverify_material_claims",
        "SOURCE_NOT_YET_EFFECTIVE": "defer_current_use_and_recheck_effective_date",
        "SOURCE_EXPIRED": "review_successor_or_mark_superseded",
        "SOURCE_INACTIVE": "review_active_references",
        "SCENARIO_SOURCE_CONFLICT": "compare_all_scenario_sources_and_preserve_unresolved_conflict",
        "SOURCE_ORPHANED": "review_discovery_link_or_remove_record",
    }
    return steps[issue_code]


def _source_discovery_paths(
    sources: list[dict[str, Any]],
    scenarios: list[dict[str, Any]],
    terms: list[dict[str, Any]],
    channels: list[dict[str, Any]],
) -> tuple[set[str], set[str]]:
    direct = {
        str(source_id)
        for records in (scenarios, terms, channels)
        for record in records
        for source_id in record.get("source_ids", [])
    }
    discovery_topics = {
        str(scenario.get("local_source_topic"))
        for scenario in scenarios
        if scenario.get("local_source_topic")
    }
    topic_discovered = {
        str(source["id"])
        for source in sources
        if discovery_topics & {str(topic) for topic in source.get("topics", [])}
    }
    return direct, topic_discovered


def source_reality_audit(as_of: str | date | None = None) -> dict[str, Any]:
    """Build the full deterministic maintenance state without making a network request."""
    target = _as_of_date(as_of)
    sources = all_sources()
    scenarios = _scenario_records()
    terms = _records(load_dataset("terms"), "terms", "terms")
    channels = all_digital_channels()
    source_by_id = {str(source["id"]): source for source in sources}
    records = [
        _source_freshness_record(source, target)
        for source in sorted(sources, key=lambda item: str(item["id"]))
    ]
    summary = {status: 0 for status in FRESHNESS_STATUSES}
    effective_summary = {
        "in_effect": 0,
        "not_yet_effective": 0,
        "expired": 0,
    }
    queue: list[dict[str, Any]] = []
    issue_specs = {
        "stale": ("SOURCE_STALE", 0),
        "review_due": ("SOURCE_REVIEW_DUE", 1),
        "inactive": ("SOURCE_INACTIVE", 0),
    }
    for record in records:
        summary[record["status"]] += 1
        effective_summary[record["effective_state"]] += 1
        record_issues: list[tuple[str, int]] = []
        if record["age_days"] < 0:
            record_issues.append(("SOURCE_VERIFICATION_DATE_IN_FUTURE", 0))
        if record["status"] == "out_of_effective_period":
            if record["effective_state"] == "not_yet_effective":
                record_issues.append(("SOURCE_NOT_YET_EFFECTIVE", 1))
            else:
                record_issues.append(("SOURCE_EXPIRED", 0))
        elif record["status"] in issue_specs:
            record_issues.append(issue_specs[record["status"]])
        source = source_by_id[record["source_id"]]
        for issue_code, priority in record_issues:
            queue.append(
                {
                    "issue_code": issue_code,
                    "priority": priority,
                    "status": record["status"],
                    "source_id": record["source_id"],
                    "scenario_id": None,
                    "conflict_type": None,
                    "related_source_ids": [],
                    "topics": sorted(str(topic) for topic in source.get("topics", [])),
                    "blocks_current_claim_use": True,
                    "verification_route": _verification_route(source),
                    "next_step": _repair_next_step(issue_code),
                    "automatic_update_allowed": False,
                }
            )
    for scenario in scenarios:
        for conflict in scenario.get("conflicts", []):
            source_id = str(conflict["source_id"])
            source = source_by_id[source_id]
            queue.append(
                {
                    "issue_code": "SCENARIO_SOURCE_CONFLICT",
                    "priority": 0,
                    "status": "conflict",
                    "source_id": source_id,
                    "scenario_id": str(scenario["id"]),
                    "conflict_type": str(conflict["conflict_type"]),
                    "related_source_ids": sorted(
                        str(item) for item in scenario.get("source_ids", [])
                    ),
                    "topics": sorted(str(topic) for topic in source.get("topics", [])),
                    "blocks_current_claim_use": True,
                    "verification_route": _verification_route(source),
                    "next_step": _repair_next_step("SCENARIO_SOURCE_CONFLICT"),
                    "automatic_update_allowed": False,
                }
            )
    direct_references, topic_discovered = _source_discovery_paths(
        sources,
        scenarios,
        terms,
        channels,
    )
    for source_id in sorted(set(source_by_id) - direct_references - topic_discovered):
        source = source_by_id[source_id]
        queue.append(
            {
                "issue_code": "SOURCE_ORPHANED",
                "priority": 2,
                "status": "orphaned",
                "source_id": source_id,
                "scenario_id": None,
                "conflict_type": None,
                "related_source_ids": [],
                "topics": sorted(str(topic) for topic in source.get("topics", [])),
                "blocks_current_claim_use": False,
                "verification_route": _verification_route(source),
                "next_step": _repair_next_step("SOURCE_ORPHANED"),
                "automatic_update_allowed": False,
            }
        )
    queue.sort(
        key=lambda item: (
            item["priority"],
            item["issue_code"],
            item["source_id"],
            item["scenario_id"] or "",
        )
    )
    repair_summary = dict(sorted(Counter(item["issue_code"] for item in queue).items()))
    problem_source_ids_by_issue = {
        issue_code: sorted(
            {item["source_id"] for item in queue if item["issue_code"] == issue_code}
        )
        for issue_code in repair_summary
    }
    return {
        "data_mode": "OFFLINE_PACKAGED_DATA",
        "as_of": target.isoformat(),
        "summary": summary,
        "effective_summary": effective_summary,
        "repair_summary": repair_summary,
        "problem_source_ids_by_issue": problem_source_ids_by_issue,
        "problem_source_ids": sorted({item["source_id"] for item in queue}),
        "problem_scenario_ids": sorted(
            {item["scenario_id"] for item in queue if item["scenario_id"] is not None}
        ),
        "sources": records,
        "repair_queue": queue,
        "discovery": {
            "directly_referenced_source_ids": sorted(direct_references & set(source_by_id)),
            "topic_discovered_source_ids": sorted(topic_discovered),
            "orphaned_source_ids": sorted(set(source_by_id) - direct_references - topic_discovered),
        },
    }


def freshness_report(
    as_of: str | date | None = None,
    *,
    statuses: Iterable[str] | str | None = None,
    topic: str | None = None,
    limit: int = 50,
    summary_only: bool = False,
) -> dict[str, Any]:
    if statuses is None:
        requested_statuses = []
    elif isinstance(statuses, str):
        requested_statuses = [statuses]
    else:
        if isinstance(statuses, (bytes, dict)):
            raise PolandDataError(
                "status must be a string or iterable of strings",
                details={"field": "status"},
            )
        try:
            requested_statuses = list(statuses)
        except TypeError as exc:
            raise PolandDataError(
                "status must be a string or iterable of strings",
                details={"field": "status"},
            ) from exc
        if any(not isinstance(item, str) for item in requested_statuses):
            raise PolandDataError(
                "status values must be strings",
                details={"field": "status"},
            )
    invalid_statuses = sorted(set(requested_statuses) - set(FRESHNESS_STATUSES))
    if invalid_statuses:
        raise PolandDataError(
            "status must be a supported freshness state",
            details={"field": "status"},
        )
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 100:
        raise PolandDataError("limit must be an integer from 1 to 100", details={"field": "limit"})
    if not isinstance(summary_only, bool):
        raise PolandDataError("summary_only must be a boolean", details={"field": "summary_only"})
    safe_topic = validate_public_literal(topic or "", "topic", max_length=80)
    normalized_topic = normalize_text(safe_topic)
    audit = source_reality_audit(as_of)
    sources = source_index()
    selected = []
    for record in audit["sources"]:
        source = sources[record["source_id"]]
        if requested_statuses and record["status"] not in requested_statuses:
            continue
        if normalized_topic and normalized_topic not in {
            normalize_text(str(item)) for item in source.get("topics", [])
        }:
            continue
        selected.append(record)
    total_matched = len(selected)
    matched_source_ids = {record["source_id"] for record in selected}
    matched_queue = [
        item
        for item in audit["repair_queue"]
        if item["source_id"] in matched_source_ids
    ]
    priority_source_ids = list(
        dict.fromkeys(item["source_id"] for item in matched_queue)
    )
    priority_source_id_set = set(priority_source_ids)
    selected_by_id = {record["source_id"]: record for record in selected}
    ordered_selected = [selected_by_id[source_id] for source_id in priority_source_ids]
    ordered_selected.extend(
        record for record in selected if record["source_id"] not in priority_source_id_set
    )
    returned_records = [] if summary_only else ordered_selected[:limit]
    returned_ids = {record["source_id"] for record in returned_records}
    projected_queue = (
        []
        if summary_only
        else [
            item
            for item in matched_queue
            if item["source_id"] in returned_ids
        ][:MAX_REPAIR_QUEUE_PROJECTION]
    )
    warnings = sorted({item["issue_code"] for item in audit["repair_queue"]})
    return {
        "schema": "poland.source-reality-report.v1",
        "data_mode": "OFFLINE_PACKAGED_DATA",
        "as_of": audit["as_of"],
        "summary": audit["summary"],
        "effective_summary": audit["effective_summary"],
        "repair_summary": audit["repair_summary"],
        "problem_source_ids_by_issue": audit["problem_source_ids_by_issue"],
        "problem_source_ids": audit["problem_source_ids"],
        "problem_scenario_ids": audit["problem_scenario_ids"],
        "projection": {
            "statuses": sorted(set(requested_statuses)),
            "topic": safe_topic or None,
            "limit": limit,
            "summary_only": summary_only,
            "total_matched": total_matched,
            "returned": len(returned_records),
            "truncated": total_matched > len(returned_records),
            "queue_total_matched": len(matched_queue),
            "queue_returned": len(projected_queue),
            "queue_truncated": len(matched_queue) > len(projected_queue),
        },
        "warnings": warnings,
        "sources": returned_records,
        "repair_queue": projected_queue,
    }


def _dimension_counts(
    records: Iterable[dict[str, Any]],
    field: str,
    *,
    multi: bool = False,
) -> dict[str, int]:
    values: Counter[str] = Counter()
    for record in records:
        raw = record.get(field)
        if multi:
            for value in raw or []:
                values[str(value)] += 1
        elif raw is not None:
            values[str(raw)] += 1
    return dict(sorted(values.items()))


def ontology_map(
    *,
    layer: str | None = None,
    detail: str = "summary",
    as_of: str | date | None = None,
) -> dict[str, Any]:
    """Describe the live registry graph without materializing a second fact store."""
    if layer is not None and layer not in ONTOLOGY_LAYERS:
        raise PolandDataError("unknown ontology layer", details={"field": "layer"})
    if detail not in {"summary", "full"}:
        raise PolandDataError("detail must be summary or full", details={"field": "detail"})
    target = _as_of_date(as_of)
    sources = all_sources()
    scenarios = _scenario_records()
    terms = _records(load_dataset("terms"), "terms", "terms")
    regions = _records(load_dataset("regions"), "regions", "regions")
    boundaries = _records(load_dataset("actions"), "boundaries", "action-boundaries")
    channels = all_digital_channels()
    skills = sorted(path.parent.name for path in (PLUGIN_ROOT / "skills").glob("*/SKILL.md"))
    authorities = sorted({str(source["authority"]) for source in sources})
    source_ids = {str(source["id"]) for source in sources}
    channel_ids = {str(channel["id"]) for channel in channels}
    skill_ids = set(skills)
    authority_ids = set(authorities)

    layers = [
        {
            "id": "services",
            "entity_type": "scenario",
            "origin": "data/scenarios.json",
            "record_count": len(scenarios),
            "dimensions": {
                "composition": _dimension_counts(scenarios, "composition"),
                "local_source_topic": _dimension_counts(scenarios, "local_source_topic"),
                "owner_skill_ids": _dimension_counts(scenarios, "owner_skill_ids", multi=True),
                "applicability_declared": {
                    "yes": sum("applicability" in scenario for scenario in scenarios),
                    "no": sum("applicability" not in scenario for scenario in scenarios),
                },
                "conflict_declared": {
                    "yes": sum(bool(scenario.get("conflicts")) for scenario in scenarios),
                    "no": sum(not scenario.get("conflicts") for scenario in scenarios),
                },
                "channel_rules_declared": {
                    "yes": sum(bool(scenario.get("channel_rules")) for scenario in scenarios),
                    "no": sum(not scenario.get("channel_rules") for scenario in scenarios),
                },
                "channel_rule_state": dict(
                    sorted(
                        Counter(
                            str(rule["state"])
                            for scenario in scenarios
                            for rule in scenario.get("channel_rules", [])
                        ).items()
                    )
                ),
            },
        },
        {
            "id": "evidence",
            "entity_type": "official_source",
            "origin": "data/sources.json",
            "record_count": len(sources),
            "dimensions": {
                field: _dimension_counts(sources, field)
                for field in (
                    "access",
                    "automation",
                    "effect",
                    "jurisdiction",
                    "source_kind",
                    "source_tier",
                    "status",
                )
            },
        },
        {
            "id": "channels",
            "entity_type": "digital_channel",
            "origin": "data/digital-channels.json",
            "record_count": len(channels),
            "dimensions": {
                field: _dimension_counts(channels, field)
                for field in ("channel_kind", "access_scope", "agent_mode")
            },
        },
        {
            "id": "vocabulary",
            "entity_type": "administrative_term",
            "origin": "data/terms.json",
            "record_count": len(terms),
            "dimensions": {},
        },
        {
            "id": "geography",
            "entity_type": "voivodeship",
            "origin": "data/regions.json",
            "record_count": len(regions),
            "dimensions": {},
        },
        {
            "id": "safety",
            "entity_type": "action_boundary",
            "origin": "data/action-boundaries.json",
            "record_count": len(boundaries),
            "dimensions": {"automation": _dimension_counts(boundaries, "automation")},
        },
        {
            "id": "ownership",
            "entity_type": "focused_skill",
            "origin": "skills/*/SKILL.md",
            "record_count": len(skills),
            "dimensions": {},
        },
        {
            "id": "authorities",
            "entity_type": "competent_or_publishing_authority",
            "origin": "derived:data/sources.json.authority",
            "record_count": len(authorities),
            "dimensions": {},
        },
    ]

    def direct_relation(
        relation_id: str,
        from_layer: str,
        to_layer: str,
        records: list[dict[str, Any]],
        field: str,
        targets: set[str],
    ) -> dict[str, Any]:
        values = [str(value) for record in records for value in record.get(field, [])]
        resolved = sum(value in targets for value in values)
        return {
            "id": relation_id,
            "from_layer": from_layer,
            "to_layer": to_layer,
            "kind": "direct",
            "field": field,
            "edge_count": len(values),
            "resolved": resolved,
            "unresolved": len(values) - resolved,
        }

    relationships = [
        direct_relation(
            "service-references-evidence",
            "services",
            "evidence",
            scenarios,
            "source_ids",
            source_ids,
        ),
        direct_relation(
            "term-references-evidence",
            "vocabulary",
            "evidence",
            terms,
            "source_ids",
            source_ids,
        ),
        direct_relation(
            "channel-references-evidence",
            "channels",
            "evidence",
            channels,
            "source_ids",
            source_ids,
        ),
        direct_relation(
            "service-owned-by-skill",
            "services",
            "ownership",
            scenarios,
            "owner_skill_ids",
            skill_ids,
        ),
    ]
    authority_edges = [str(source["authority"]) for source in sources]
    relationships.append(
        {
            "id": "evidence-attributed-to-authority",
            "from_layer": "evidence",
            "to_layer": "authorities",
            "kind": "derived",
            "field": "authority",
            "edge_count": len(authority_edges),
            "resolved": sum(value in authority_ids for value in authority_edges),
            "unresolved": 0,
            "derivation": "distinct authority labels from source records",
        }
    )
    conflict_values = [
        str(conflict["source_id"])
        for scenario in scenarios
        for conflict in scenario.get("conflicts", [])
    ]
    relationships.append(
        {
            "id": "service-records-evidence-conflict",
            "from_layer": "services",
            "to_layer": "evidence",
            "kind": "direct",
            "field": "conflicts.source_id",
            "edge_count": len(conflict_values),
            "resolved": sum(value in source_ids for value in conflict_values),
            "unresolved": sum(value not in source_ids for value in conflict_values),
        }
    )
    channel_rule_values = [
        str(channel_id)
        for scenario in scenarios
        for rule in scenario.get("channel_rules", [])
        for channel_id in rule.get("channel_ids", [])
    ]
    relationships.append(
        {
            "id": "service-selects-channel-by-rule",
            "from_layer": "services",
            "to_layer": "channels",
            "kind": "direct",
            "field": "channel_rules.channel_ids",
            "edge_count": len(channel_rule_values),
            "resolved": sum(value in channel_ids for value in channel_rule_values),
            "unresolved": sum(value not in channel_ids for value in channel_rule_values),
        }
    )
    channel_sources: dict[str, set[str]] = {}
    for channel in channels:
        for source_id in channel.get("source_ids", []):
            channel_sources.setdefault(str(source_id), set()).add(str(channel["id"]))
    scenario_channel_edges = {
        (str(scenario["id"]), channel_id)
        for scenario in scenarios
        for source_id in scenario.get("source_ids", [])
        for channel_id in channel_sources.get(str(source_id), set())
        if channel_id in channel_ids
    }
    relationships.append(
        {
            "id": "service-discoverable-through-channel",
            "from_layer": "services",
            "to_layer": "channels",
            "kind": "derived",
            "field": "shared source_ids",
            "edge_count": len(scenario_channel_edges),
            "resolved": len(scenario_channel_edges),
            "unresolved": 0,
            "derivation": "scenario and channel share at least one evidence source",
        }
    )

    direct_references, topic_discovered = _source_discovery_paths(
        sources,
        scenarios,
        terms,
        channels,
    )
    scenarios_with_channel = {service_id for service_id, _ in scenario_channel_edges}
    freshness = source_reality_audit(target)
    coverage = [
        {
            "id": "direct-source-linkage",
            "layer": "evidence",
            "classification": "partial" if len(direct_references & source_ids) < len(sources) else "linked",
            "observed": len(direct_references & source_ids),
            "total": len(sources),
            "ids": sorted(source_ids - direct_references),
        },
        {
            "id": "source-discovery-reachability",
            "layer": "evidence",
            "classification": "unlinked"
            if source_ids - direct_references - topic_discovered
            else "linked",
            "observed": len((direct_references | topic_discovered) & source_ids),
            "total": len(sources),
            "ids": sorted(source_ids - direct_references - topic_discovered),
        },
        {
            "id": "explicit-service-applicability",
            "layer": "services",
            "classification": "partial"
            if any("applicability" not in scenario for scenario in scenarios)
            else "linked",
            "observed": sum("applicability" in scenario for scenario in scenarios),
            "total": len(scenarios),
            "ids": sorted(
                str(scenario["id"])
                for scenario in scenarios
                if "applicability" not in scenario
            ),
        },
        {
            "id": "derived-service-channel-coverage",
            "layer": "services",
            "classification": "partial" if len(scenarios_with_channel) < len(scenarios) else "linked",
            "observed": len(scenarios_with_channel),
            "total": len(scenarios),
            "ids": sorted(
                str(scenario["id"])
                for scenario in scenarios
                if str(scenario["id"]) not in scenarios_with_channel
            ),
        },
        {
            "id": "explicit-service-channel-rules",
            "layer": "services",
            "classification": "partial"
            if any(not scenario.get("channel_rules") for scenario in scenarios)
            else "linked",
            "observed": sum(bool(scenario.get("channel_rules")) for scenario in scenarios),
            "total": len(scenarios),
            "ids": sorted(
                str(scenario["id"])
                for scenario in scenarios
                if not scenario.get("channel_rules")
            ),
        },
        {
            "id": "current-source-evidence",
            "layer": "evidence",
            "classification": "partial"
            if freshness["summary"]["fresh"] < len(sources)
            else "current",
            "observed": freshness["summary"]["fresh"],
            "total": len(sources),
            "ids": sorted(
                str(record["source_id"])
                for record in freshness["sources"]
                if record["status"] != "fresh"
            ),
        },
    ]
    if detail == "summary":
        coverage = [
            {key: value for key, value in item.items() if key != "ids"}
            for item in coverage
        ]
    unmodeled = [
        {
            "id": "topic-taxonomy",
            "reason": "source topics and scenario local_source_topic are discovery tags, not one governed taxonomy",
            "observed_values": len(
                {str(topic) for source in sources for topic in source.get("topics", [])}
            ),
        },
        {
            "id": "locality-to-region",
            "reason": "source localities may name gmina or cities and are not typed voivodeship edges",
            "observed_values": len(
                {str(locality) for source in sources for locality in source.get("localities", [])}
            ),
        },
        {
            "id": "checkpoint-to-action-boundary",
            "reason": "scenario stop_before values are checkpoints, not asserted boundary identifiers",
            "observed_values": len(
                {str(value) for scenario in scenarios for value in scenario.get("stop_before", [])}
            ),
        },
    ]
    visible_layers = [item for item in layers if layer is None or item["id"] == layer]
    visible_relationships = [
        item
        for item in relationships
        if layer is None or layer in {item["from_layer"], item["to_layer"]}
    ]
    visible_coverage = [
        item for item in coverage if layer is None or item["layer"] == layer
    ]
    return {
        "schema": "poland.ontology-map.v1",
        "data_mode": "OFFLINE_PACKAGED_DATA",
        "as_of": target.isoformat(),
        "projection": {"layer": layer, "detail": detail},
        "summary": {
            "layers": len(layers),
            "relationships": len(relationships),
            "direct_edges": sum(
                item["edge_count"] for item in relationships if item["kind"] == "direct"
            ),
            "derived_edges": sum(
                item["edge_count"] for item in relationships if item["kind"] == "derived"
            ),
            "broken_edges": sum(item["unresolved"] for item in relationships),
            "coverage_observations": len(coverage),
            "unmodeled_boundaries": len(unmodeled),
        },
        "layers": visible_layers,
        "relationships": visible_relationships,
        "coverage": visible_coverage,
        "unmodeled": unmodeled if layer is None else [],
        "limitations": [
            "Counts describe the packaged graph as of the requested date; they do not prove legal completeness.",
            "Evidence edges mean that a registry record references a source; they do not prove claim-level sufficiency or eligibility.",
            "Derived service-channel edges indicate discoverability through shared evidence, not executable availability.",
            "Unlinked and unmodeled observations are not validation failures without an owner-authored coverage policy.",
        ],
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
                for item in candidate:
                    if not isinstance(item, str):
                        continue
                    code = item.partition(":")[0]
                    if re.fullmatch(r"[A-Z0-9_]+", code):
                        warnings.add(code)
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
        "ontology-map.schema.json",
        "source-reality-report.schema.json",
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
            if source["jurisdiction"] not in {
                "national",
                "eu",
                "voivodeship",
                "powiat",
                "gmina",
            }:
                errors.append(f"source {label} has invalid jurisdiction")
            if source["access"] not in {"public", "authenticated", "credentialed_api"}:
                errors.append(f"source {label} has invalid access")
            if source["effect"] not in {"informational", "personal_record", "consequential"}:
                errors.append(f"source {label} has invalid effect")
            allowed_automation = {
                "human_in_loop_operator",
                "public_read_only",
                "public_read_only_handoff",
                "prohibited_external_effect",
                "user_handoff_then_stop",
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
                for rule in item.get("channel_rules", []):
                    unknown_rule_facts = set(rule.get("when", {})) - ROUTE_FACT_FIELDS
                    if unknown_rule_facts:
                        errors.append(
                            f"scenario {item_id} channel rule uses unsupported facts: "
                            + ", ".join(sorted(unknown_rule_facts))
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
    reality: dict[str, Any] | None = None
    if not errors:
        try:
            reality = source_reality_audit(as_of)
            future_ids = reality["problem_source_ids_by_issue"].get(
                "SOURCE_VERIFICATION_DATE_IN_FUTURE",
                [],
            )
            if future_ids:
                errors.append(
                    "SOURCE_VERIFICATION_DATE_IN_FUTURE: " + ", ".join(future_ids)
                )
            for issue_code in (
                "SOURCE_STALE",
                "SOURCE_REVIEW_DUE",
                "SOURCE_NOT_YET_EFFECTIVE",
                "SOURCE_EXPIRED",
                "SOURCE_INACTIVE",
                "SCENARIO_SOURCE_CONFLICT",
                "SOURCE_ORPHANED",
            ):
                issue_ids = sorted(
                    {
                        item["source_id"]
                        for item in reality["repair_queue"]
                        if item["issue_code"] == issue_code
                    }
                )
                if issue_ids:
                    warnings.append(f"{issue_code}: {', '.join(issue_ids)}")
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
        "reality": {
            "summary": reality["summary"] if reality else {},
            "repair_summary": reality["repair_summary"] if reality else {},
            "problem_source_ids_by_issue": (
                reality["problem_source_ids_by_issue"] if reality else {}
            ),
            "problem_source_ids": reality["problem_source_ids"] if reality else [],
            "problem_scenario_ids": reality["problem_scenario_ids"] if reality else [],
        },
        "bundle_sha256": digest,
    }


def overview() -> dict[str, Any]:
    validation = validate_bundle()
    return {
        "plugin": "poland",
        "version": "0.3.0",
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
            "task_scoped_assistance",
            "confirmation_gated_external_effect",
            "user_only_restricted",
        ],
        "notice": (
            "Navigation support only. Verify changing facts and competent locality at action time. "
            "The user handles authentication and user-only controls; caller-owned tools may assist "
            "within explicit task scope and confirmation gates."
        ),
    }
