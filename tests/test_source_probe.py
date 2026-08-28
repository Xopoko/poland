from __future__ import annotations

import importlib.util
from http.client import RemoteDisconnected
from io import StringIO
import json
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
PROBE_PATH = ROOT / "scripts" / "source_probe.py"
SPEC = importlib.util.spec_from_file_location("poland_source_probe", PROBE_PATH)
PROBE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(PROBE)


class FakeResponse:
    status = 200
    headers = {"Content-Type": "text/html", "ETag": '"abc"'}

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def geturl(self):
        return "https://www.gov.pl/web/udsc-en"

    def read(self, _limit):
        return b"<html><title>Office for Foreigners</title></html>"


class FakeOpener:
    def open(self, _request, timeout):
        self.timeout = timeout
        return FakeResponse()


class DisconnectingOpener:
    def open(self, _request, timeout):
        raise RemoteDisconnected("closed")


class UnexpectedFinalResponse(FakeResponse):
    def geturl(self):
        return "https://lookalike.example/foreigners"


class UnexpectedFinalOpener:
    def open(self, _request, timeout):
        return UnexpectedFinalResponse()


class DownloadResponse(FakeResponse):
    headers = {
        "Content-Type": "application/pdf",
        "Content-Disposition": "attachment; filename=form.pdf",
    }


class DownloadOpener:
    def open(self, _request, timeout):
        return DownloadResponse()


class SourceProbeTests(unittest.TestCase):
    def test_get_probe_returns_bounded_receipt(self):
        with patch.object(PROBE, "build_opener", return_value=FakeOpener()):
            result = PROBE.probe("udsc-home", method="GET", timeout=5, max_bytes=4096)
        self.assertEqual(200, result["status"])
        self.assertEqual("Office for Foreigners", result["title"])
        self.assertEqual("untrusted_evidence", result["content_trust"])
        self.assertEqual("public_read_only", result["automation_boundary"])
        self.assertRegex(result["content_sha256"], r"^[0-9a-f]{64}$")

    def test_authenticated_source_is_rejected_before_network(self):
        with patch.object(PROBE, "build_opener") as opener:
            with self.assertRaises(PROBE.PolandDataError) as caught:
                PROBE.probe("mos-residence")
            opener.assert_not_called()
        self.assertEqual("SOURCE_PROBE_NOT_ALLOWED", caught.exception.code)
        self.assertEqual(
            "source probe supports public_read_only sources only",
            str(caught.exception),
        )

    def test_public_handoff_source_routes_to_browser_before_network(self):
        with patch.object(PROBE, "build_opener") as opener:
            with self.assertRaises(PROBE.PolandDataError) as caught:
                PROBE.probe("gov-meldunek-polish-citizens")
            opener.assert_not_called()
        self.assertEqual("SOURCE_PROBE_HANDOFF_REQUIRED", caught.exception.code)
        self.assertEqual(
            "public_read_only_handoff sources are not probeable; "
            "use Browser or manual official-page verification",
            str(caught.exception),
        )
        self.assertEqual(
            "browser_or_manual_official_page",
            caught.exception.details["verification_route"],
        )

    def test_public_handoff_cli_error_has_stable_code_and_message(self):
        stderr = StringIO()
        with patch.object(PROBE, "build_opener") as opener, patch.object(
            PROBE.sys, "stderr", stderr
        ):
            status = PROBE.main(["gov-meldunek-polish-citizens"])
            opener.assert_not_called()
        self.assertEqual(2, status)
        self.assertEqual(
            {
                "code": "SOURCE_PROBE_HANDOFF_REQUIRED",
                "error": (
                    "public_read_only_handoff sources are not probeable; "
                    "use Browser or manual official-page verification"
                ),
            },
            json.loads(stderr.getvalue()),
        )

    def test_arbitrary_url_and_unsafe_limits_are_not_supported(self):
        with self.assertRaises(PROBE.PolandDataError):
            PROBE.probe("https://example.com")
        with self.assertRaises(PROBE.PolandDataError):
            PROBE.probe("udsc-home", timeout=60)
        with self.assertRaises(PROBE.PolandDataError):
            PROBE.probe("udsc-home", max_bytes=20)

    def test_redirect_must_remain_on_declared_https_origin(self):
        redirect = PROBE.OriginBoundRedirect(["gov.pl"])
        with self.assertRaises(PROBE.PolandDataError):
            redirect.redirect_request(None, None, 302, "Found", None, "https://example.com/login")

    def test_redirect_uses_exact_idna_normalized_origin(self):
        redirect = PROBE.OriginBoundRedirect(["gov.pl"])
        for target in (
            "https://service.gov.pl/login",
            "http://gov.pl/login",
            "https://g\u043ev.pl/login",
            "https://gov.pl:444/login",
        ):
            with self.subTest(target=target):
                with self.assertRaises(PROBE.PolandDataError):
                    redirect.ensure_allowed(target)

    def test_unicode_and_punycode_hosts_have_one_canonical_origin(self):
        unicode_origin = PROBE.normalize_https_origin(
            "https://b\u00fccher.example/path"
        )
        ascii_origin = PROBE.normalize_https_origin(
            "https://xn--bcher-kva.example/other"
        )
        self.assertEqual(unicode_origin, ascii_origin)

    def test_final_url_is_checked_even_when_opener_returns_it_directly(self):
        with patch.object(PROBE, "build_opener", return_value=UnexpectedFinalOpener()):
            with self.assertRaises(PROBE.PolandDataError):
                PROBE.probe("udsc-home", method="GET", timeout=5, max_bytes=4096)

    def test_get_rejects_download_response(self):
        with patch.object(PROBE, "build_opener", return_value=DownloadOpener()):
            with self.assertRaises(PROBE.PolandDataError):
                PROBE.probe("udsc-home", method="GET", timeout=5, max_bytes=4096)

    def test_declared_origins_include_only_exact_hosts(self):
        source = PROBE.get_source("udsc-home")
        policy = PROBE.OriginBoundRedirect(PROBE.declared_origin_inputs(source))
        policy.ensure_allowed("https://www.gov.pl/web/udsc-en")
        policy.ensure_allowed("https://gov.pl/")
        with self.assertRaises(PROBE.PolandDataError):
            policy.ensure_allowed("https://other.gov.pl/web/udsc-en")

    def test_remote_disconnect_is_a_structured_network_result(self):
        with patch.object(PROBE, "build_opener", return_value=DisconnectingOpener()):
            result = PROBE.probe("udsc-home")
        self.assertIsNone(result["status"])
        self.assertEqual("RemoteDisconnected", result["error"])


if __name__ == "__main__":
    unittest.main()
