#!/usr/bin/env python3
"""Probe bundled public official sources without accepting arbitrary URLs."""

from __future__ import annotations

import argparse
import hashlib
from http.client import RemoteDisconnected
import json
import re
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT / "lib"))

from poland_core import PolandDataError, get_source  # noqa: E402


HttpsOrigin = tuple[str, str, int]
SAFE_GET_CONTENT_TYPES = {
    "application/json",
    "application/xhtml+xml",
    "text/html",
    "text/plain",
}
HANDOFF_ERROR_CODE = "SOURCE_PROBE_HANDOFF_REQUIRED"
HANDOFF_ERROR_MESSAGE = (
    "public_read_only_handoff sources are not probeable; "
    "use Browser or manual official-page verification"
)
NOT_PROBEABLE_ERROR_CODE = "SOURCE_PROBE_NOT_ALLOWED"
NOT_PROBEABLE_ERROR_MESSAGE = "source probe supports public_read_only sources only"


def normalize_hostname(host: str) -> str:
    """Return the canonical ASCII hostname used for exact origin checks."""
    if not isinstance(host, str) or not host.strip():
        raise PolandDataError("origin requires a hostname")
    try:
        normalized = host.strip().rstrip(".").encode("idna").decode("ascii")
    except UnicodeError as exc:
        raise PolandDataError("origin hostname is not valid IDNA") from exc
    if not normalized:
        raise PolandDataError("origin requires a hostname")
    return normalized.lower()


def normalize_https_origin(url: str) -> HttpsOrigin:
    """Normalize an HTTPS URL to an exact scheme, IDNA host, and port tuple."""
    try:
        parsed = urlparse(url)
        host = parsed.hostname
        port = parsed.port
    except ValueError as exc:
        raise PolandDataError("origin URL is malformed") from exc
    if parsed.scheme.lower() != "https" or host is None:
        raise PolandDataError("origin must use HTTPS and include a hostname")
    if parsed.username is not None or parsed.password is not None:
        raise PolandDataError("origin URL must not contain credentials")
    normalized_port = port if port is not None else 443
    if normalized_port != 443:
        raise PolandDataError("origin must use the default HTTPS port")
    return ("https", normalize_hostname(host), normalized_port)


def declared_origin_inputs(source: dict[str, Any]) -> list[str]:
    """Build exact origins from the source URL and explicitly declared hosts."""
    values = [str(source["url"])]
    values.extend(f"https://{domain}" for domain in source.get("domains", []))
    return values


def normalize_declared_origin(value: str) -> HttpsOrigin:
    """Accept an explicit HTTPS URL or a bare exact host from registry data."""
    candidate = value if "://" in value else f"https://{value}"
    return normalize_https_origin(candidate)


class OriginBoundRedirect(HTTPRedirectHandler):
    def __init__(self, origins: Iterable[str]) -> None:
        super().__init__()
        self.origins = frozenset(normalize_declared_origin(item) for item in origins)
        if not self.origins:
            raise PolandDataError("source requires at least one exact HTTPS origin")

    def ensure_allowed(self, url: str) -> None:
        if normalize_https_origin(url) not in self.origins:
            raise PolandDataError("URL left the source's exact declared HTTPS origins")

    def redirect_request(
        self,
        req: Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> Request:
        self.ensure_allowed(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def probe(
    source_id: str,
    *,
    method: str = "HEAD",
    timeout: float = 10.0,
    max_bytes: int = 131072,
) -> dict[str, Any]:
    if method not in {"HEAD", "GET"}:
        raise PolandDataError("method must be HEAD or GET")
    if not 1 <= timeout <= 30:
        raise PolandDataError("timeout must be from 1 to 30 seconds")
    if not 1024 <= max_bytes <= 1048576:
        raise PolandDataError("max_bytes must be from 1024 to 1048576")
    source = get_source(source_id)
    if source["access"] == "public" and source["automation"] == "public_read_only_handoff":
        raise PolandDataError(
            HANDOFF_ERROR_MESSAGE,
            code=HANDOFF_ERROR_CODE,
            details={
                "source_id": source_id,
                "verification_route": "browser_or_manual_official_page",
            },
        )
    if source["access"] != "public" or source["automation"] != "public_read_only":
        raise PolandDataError(
            NOT_PROBEABLE_ERROR_MESSAGE,
            code=NOT_PROBEABLE_ERROR_CODE,
        )
    redirect_policy = OriginBoundRedirect(declared_origin_inputs(source))
    redirect_policy.ensure_allowed(source["url"])
    opener = build_opener(redirect_policy)
    request = Request(
        source["url"],
        method=method,
        headers={"User-Agent": "poland-agent-skills-source-probe/0.1 (+https://github.com/Xopoko/poland)"},
    )
    checked_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    try:
        with opener.open(request, timeout=timeout) as response:
            final_url = response.geturl()
            redirect_policy.ensure_allowed(final_url)
            content_type = response.headers.get("Content-Type", "") or ""
            media_type = content_type.split(";", 1)[0].strip().lower()
            disposition = response.headers.get("Content-Disposition", "") or ""
            if method == "GET" and (
                media_type not in SAFE_GET_CONTENT_TYPES
                or disposition.lower().lstrip().startswith("attachment")
            ):
                raise PolandDataError("source returned an unsupported download response")
            raw = response.read(max_bytes + 1) if method == "GET" else b""
            if len(raw) > max_bytes:
                raise PolandDataError("response exceeded max_bytes")
            title = ""
            if raw:
                match = re.search(rb"<title[^>]*>(.*?)</title>", raw, re.I | re.S)
                if match:
                    title = re.sub(r"\s+", " ", match.group(1).decode("utf-8", "replace")).strip()[:300]
            return {
                "source_id": source_id,
                "checked_at": checked_at,
                "method": method,
                "content_trust": "untrusted_evidence",
                "automation_boundary": "public_read_only",
                "status": response.status,
                "final_url": final_url,
                "content_type": content_type,
                "last_modified": response.headers.get("Last-Modified"),
                "etag": response.headers.get("ETag"),
                "bytes_read": len(raw),
                "content_sha256": hashlib.sha256(raw).hexdigest() if raw else None,
                "title": title,
            }
    except HTTPError as exc:
        return {
            "source_id": source_id,
            "checked_at": checked_at,
            "method": method,
            "status": exc.code,
            "error": "http_error",
        }
    except (URLError, socket.timeout, TimeoutError, RemoteDisconnected, ConnectionResetError) as exc:
        reason = getattr(exc, "reason", exc)
        return {
            "source_id": source_id,
            "checked_at": checked_at,
            "method": method,
            "status": None,
            "error": type(reason).__name__,
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_ids", nargs="+", help="Stable IDs from data/sources.json")
    parser.add_argument("--method", choices=["HEAD", "GET"], default="HEAD")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--max-bytes", type=int, default=131072)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    results = []
    try:
        for source_id in args.source_ids:
            results.append(probe(source_id, method=args.method, timeout=args.timeout, max_bytes=args.max_bytes))
    except PolandDataError as exc:
        print(
            json.dumps({"code": exc.code, "error": str(exc)}, sort_keys=True),
            file=sys.stderr,
        )
        return 2
    print(json.dumps({"results": results}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if all(item.get("status") is not None and item.get("status", 500) < 500 for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
