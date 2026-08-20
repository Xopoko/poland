#!/usr/bin/env python3
"""Read-only CLI for Poland source discovery and evidence-gated planning."""

from __future__ import annotations

import argparse
import json
import re
import sys
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
    "boundary",
}
BOOLEAN_FACT_FIELDS = {"safe_to_speak", "urgent"}
DATE_FACT_FIELDS = {"intended_arrival_date", "target_date"}


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
        elif field in BOOLEAN_FACT_FIELDS:
            parser.add_argument(flag, action=argparse.BooleanOptionalAction, default=None)
        else:
            parser.add_argument(
                flag,
                metavar="CATEGORY" if field not in DATE_FACT_FIELDS else "YYYY-MM-DD",
                help="Non-sensitive categorical fact only.",
            )


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
    sources.add_argument("--jurisdiction", choices=["national", "eu", "voivodeship", "gmina"])
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

    boundary = sub.add_parser("boundary", help="Classify an intended action boundary")
    boundary.add_argument("action")
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
        return freshness_report(args.as_of)
    if args.command == "boundary":
        return action_boundary(validate_public_literal(args.action, "action", allow_empty=False))
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
