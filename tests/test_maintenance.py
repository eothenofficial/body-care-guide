"""Maintenance boundary tests; no test is allowed to make a real connection."""
from __future__ import annotations

import copy
from contextlib import contextmanager
from datetime import date, timedelta
import json
from pathlib import Path
import shutil
import socket
import ssl
import sys
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError
import uuid


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts import check_links, review_due  # noqa: E402


URL = "https://example.org/source"


@contextmanager
def workspace_tempdir():
    # mkdtemp's mode 0700 can deny the restricted Windows token access. Inherit
    # the checkout permissions instead, and verify the exact cleanup target.
    target = PROJECT_ROOT / (".test-maintenance-" + uuid.uuid4().hex)
    target.mkdir()
    resolved = target.resolve()
    resolved.relative_to(PROJECT_ROOT.resolve())
    try:
        yield resolved
    finally:
        if resolved.parent != PROJECT_ROOT.resolve() or not resolved.name.startswith(".test-maintenance-"):
            raise AssertionError("Refusing to remove a fixture outside the checkout")
        shutil.rmtree(resolved)


class FakeResponse:
    def __init__(self, status=200, url=URL):
        self.status = status
        self.url = url
        self.headers = {}

    def getcode(self):
        return self.status

    def geturl(self):
        return self.url

    def read(self, size=-1):
        return b""

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def http_error(code):
    return HTTPError(URL, code, "simulated HTTP response", None, None)


class NoNetworkTest(unittest.TestCase):
    def setUp(self):
        # A broken mock or a future refactor must fail instead of reaching DNS/TCP.
        guard = patch.object(
            socket, "create_connection",
            side_effect=AssertionError("Tests must not make real network connections"),
        )
        guard.start()
        self.addCleanup(guard.stop)


class LinkStatusTests(NoNetworkTest):
    def test_success_uses_head_and_passes_timeout(self):
        opener = Mock(return_value=FakeResponse())
        result = check_links.check_url(URL, timeout=2.5, opener=opener)
        self.assertEqual(result["status"], "reachable")
        self.assertEqual(result["method"], "HEAD")
        opener.assert_called_once()
        request = opener.call_args.args[0]
        self.assertEqual(request.get_method(), "HEAD")
        self.assertEqual(request.full_url, URL)
        self.assertEqual(opener.call_args.kwargs["timeout"], 2.5)

    def test_head_405_retries_once_with_get(self):
        opener = Mock(side_effect=[http_error(405), FakeResponse()])
        result = check_links.check_url(URL, opener=opener)
        self.assertEqual(result["status"], "reachable")
        self.assertEqual(result["method"], "GET")
        self.assertEqual(
            [call.args[0].get_method() for call in opener.call_args_list],
            ["HEAD", "GET"],
        )

    def test_get_fallback_failure_retains_get_method(self):
        opener = Mock(side_effect=[http_error(405), http_error(403)])
        result = check_links.check_url(URL, opener=opener)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["method"], "GET")
        self.assertEqual(opener.call_count, 2)

    def test_http_errors_are_not_all_reported_as_missing(self):
        cases = {
            404: "missing", 410: "missing", 401: "blocked", 403: "blocked",
            429: "rate_limited", 500: "server_error", 501: "server_error",
            503: "server_error", 418: "http_error",
        }
        for code, expected in cases.items():
            with self.subTest(code=code):
                opener = Mock(side_effect=http_error(code))
                result = check_links.check_url(URL, opener=opener)
                self.assertEqual(result["status"], expected)
                self.assertEqual(result["method"], "HEAD")
                self.assertEqual(opener.call_count, 1, "Only HTTP 405 retries with GET")

    def test_unresolved_redirect_is_not_reachable(self):
        opener = Mock(return_value=FakeResponse(status=302))
        result = check_links.check_url(URL, opener=opener)
        self.assertEqual(result["status"], "redirect_unresolved")
        opener.assert_called_once()

    def test_followed_redirect_can_be_reachable(self):
        opener = Mock(return_value=FakeResponse(url="https://example.org/moved"))
        result = check_links.check_url(URL, opener=opener)
        self.assertEqual(result["status"], "reachable")
        self.assertEqual(result["method"], "HEAD")

    def test_timeout_network_and_tls_failures_are_distinct(self):
        cases = [
            (TimeoutError("slow response"), "timeout"),
            (URLError(socket.timeout("slow response")), "timeout"),
            (URLError("connection refused"), "network_error"),
            (URLError(ssl.SSLCertVerificationError("untrusted certificate")), "tls_error"),
            (ssl.SSLError("TLS handshake failed"), "tls_error"),
        ]
        for error, expected in cases:
            with self.subTest(error=repr(error)):
                opener = Mock(side_effect=error)
                result = check_links.check_url(URL, opener=opener)
                self.assertEqual(result["status"], expected)
                self.assertEqual(opener.call_count, 1)

    def test_invalid_urls_never_call_opener(self):
        for url in ["", "not a URL", "https://", "file:///tmp/paper.pdf", "javascript:alert(1)"]:
            with self.subTest(url=url):
                opener = Mock(side_effect=AssertionError("Invalid URL must not be fetched"))
                result = check_links.check_url(url, opener=opener)
                self.assertEqual(result["status"], "invalid_url")
                opener.assert_not_called()


def entry(entry_id, checked, clinical="not_clinically_reviewed"):
    return {
        "id": entry_id, "title": entry_id,
        "content_checked_at": checked, "clinical_review_status": clinical,
    }


def source(source_id, checked):
    return {
        "id": source_id, "citation": source_id, "url": URL,
        "content_checked_at": checked,
    }


def review_inputs(entries=None, sources=None, checked="2026-10-28", clinical="clinically_reviewed"):
    book = {
        "id": "book", "title": "Test guide", "chapter_ids": ["eyes"],
        "content_checked_at": checked, "clinical_review_status": clinical,
    }
    chapters = [{"id": "eyes", "title": "Eyes", "entries": entries or []}]
    return book, chapters, sources or []


def record_ids(records):
    return {record["id"] for record in records}


class ReviewDateTests(unittest.TestCase):
    AS_OF = date(2026, 10, 28)

    def summarize(self, entries=None, sources=None, **kwargs):
        args = review_inputs(entries, sources, **kwargs)
        return review_due.summarize_reviews(*args, as_of=self.AS_OF, interval_days=180)

    def test_180_days_due_but_179_days_current(self):
        inputs = [
            entry("eyes-180", (self.AS_OF - timedelta(days=180)).isoformat()),
            entry("eyes-179", (self.AS_OF - timedelta(days=179)).isoformat()),
        ]
        result = self.summarize(entries=inputs)
        records = {r["id"]: r for r in result["records"] if r["kind"] == "entry"}
        self.assertEqual(records["eyes-180"]["age_days"], 180)
        self.assertEqual(records["eyes-180"]["status"], "due")
        self.assertEqual(records["eyes-179"]["age_days"], 179)
        self.assertEqual(records["eyes-179"]["status"], "current")
        self.assertEqual(record_ids(result["due"]), {"eyes-180"})

    def test_leap_day_uses_calendar_arithmetic(self):
        args = review_inputs(
            entries=[entry("eyes-leap", "2024-02-29", "clinically_reviewed")],
            checked="2024-08-27",
        )
        result = review_due.summarize_reviews(*args, as_of=date(2024, 8, 27), interval_days=180)
        leap = next(r for r in result["records"] if r["id"] == "eyes-leap")
        self.assertEqual(leap["age_days"], 180)
        self.assertEqual(leap["status"], "due")

    def test_missing_invalid_and_future_dates_are_not_due(self):
        items = [entry("missing", None), entry("bad", "2026-10-99"),
                 entry("bad-leap", "2023-02-29"), entry("future", "2026-10-29")]
        del items[0]["content_checked_at"]
        result = self.summarize(entries=items)
        self.assertEqual(record_ids(result["invalid_dates"]), {"missing", "bad", "bad-leap"})
        self.assertEqual(record_ids(result["future_dates"]), {"future"})
        self.assertFalse(result["due"])
        by_id = {r["id"]: r for r in result["records"]}
        self.assertEqual(by_id["future"]["status"], "future_date")
        self.assertEqual(by_id["bad"]["status"], "invalid_date")

    def test_recent_clinical_pending_is_separate_from_due(self):
        result = self.summarize(entries=[
            entry("recent", "2026-10-28"),
            entry("signed", "2026-10-28", "clinically_reviewed"),
        ], clinical="not_clinically_reviewed")
        self.assertFalse(result["due"])
        self.assertEqual({r["kind"] for r in result["clinical_review_pending"]}, {"book", "entry"})
        pending_entries = {r["id"] for r in result["clinical_review_pending"] if r["kind"] == "entry"}
        self.assertEqual(pending_entries, {"recent"})
        self.assertTrue(all(r["status"] == "current" for r in result["clinical_review_pending"]))

    def test_source_dates_are_reviewed_without_clinical_signoff_requirement(self):
        sources = [source("src-old", (self.AS_OF - timedelta(days=180)).isoformat()),
                   source("src-new", "2026-10-28"), source("src-bad", "")]
        sources[1]["clinical_review_status"] = "not_clinically_reviewed"
        result = self.summarize(sources=sources)
        self.assertEqual(record_ids(result["due"]), {"src-old"})
        self.assertEqual(record_ids(result["invalid_dates"]), {"src-bad"})
        self.assertFalse(result["clinical_review_pending"])

    def test_summary_preserves_inputs_and_exposes_expected_sections(self):
        args = review_inputs(entries=[entry("eyes-001", "2026-10-28")], sources=[source("src-a", "2026-10-28")])
        before = copy.deepcopy(args)
        result = review_due.summarize_reviews(*args, as_of=self.AS_OF, interval_days=180)
        self.assertEqual(args, before)
        self.assertTrue({"records", "due", "invalid_dates", "future_dates", "clinical_review_pending", "counts"} <= set(result))
        self.assertIsInstance(result["counts"], dict)
        self.assertEqual({r["kind"] for r in result["records"]}, {"book", "entry", "source"})
        self.assertEqual(len(result["records"]), 3)


class MaintenanceCliTests(NoNetworkTest):
    def make_root(self, parent):
        root = Path(parent) / "guide"
        content = root / "content"
        (content / "chapters").mkdir(parents=True)
        book, chapters, sources = review_inputs(
            entries=[entry("eyes-001", "2026-10-28")],
            sources=[source("src-example", "2026-10-28")],
        )
        for path, data in [(content / "book.json", book),
                           (content / "chapters" / "eyes.json", chapters[0]),
                           (content / "sources.json", sources)]:
            path.write_text(json.dumps(data), encoding="utf-8")
        return root

    @staticmethod
    def snapshot(root):
        return {str(p.relative_to(root)): p.read_bytes() for p in (root / "content").rglob("*.json")}

    def test_link_cli_strict_fails_only_for_missing(self):
        for status, strict, should_fail in [
            ("missing", True, True), ("missing", False, False),
            ("blocked", True, False), ("timeout", True, False),
        ]:
            with self.subTest(status=status, strict=strict), workspace_tempdir() as tmp:
                root = self.make_root(tmp)
                output = Path(tmp) / "reports"
                before = self.snapshot(root)
                error = {"missing": http_error(404), "blocked": http_error(403),
                         "timeout": TimeoutError("slow response")}[status]
                result = check_links.check_url(URL, opener=Mock(side_effect=error))
                argv = ["--root", str(root), "--output-dir", str(output)]
                if strict:
                    argv.append("--strict")
                with patch.object(check_links, "check_url", return_value=result):
                    code = check_links.main(argv)
                self.assertEqual(bool(code), should_fail)
                self.assertTrue((output / "link-health.md").is_file())
                json.loads((output / "link-health.json").read_text(encoding="utf-8"))
                self.assertEqual(self.snapshot(root), before)

    def test_review_cli_fixed_date_and_custom_interval_do_not_change_content(self):
        with workspace_tempdir() as tmp:
            root = self.make_root(tmp)
            output = Path(tmp) / "reports"
            before = self.snapshot(root)
            code = review_due.main([
                "--root", str(root), "--output-dir", str(output),
                "--as-of", "2026-10-29", "--interval-days", "1",
            ])
            self.assertFalse(code)
            report = json.loads((output / "review-due.json").read_text(encoding="utf-8"))
            self.assertEqual(len(report["due"]), 3)
            self.assertEqual({r["kind"] for r in report["due"]}, {"book", "entry", "source"})
            self.assertTrue((output / "review-due.md").is_file())
            self.assertEqual(self.snapshot(root), before)


if __name__ == "__main__":
    unittest.main()
