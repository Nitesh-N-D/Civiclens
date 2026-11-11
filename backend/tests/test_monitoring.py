"""Source monitoring compares visible text only and never treats errors as changes."""

import unittest

from app.monitoring import FetchResult, classify, content_hash, fetch, visible_text

PAGE = b"<html><head><style>p{}</style><script>var t=1</script></head><body><p>Pension &amp; rules</p></body></html>"


class MonitoringTests(unittest.TestCase):
    def test_visible_text_drops_markup_and_scripts(self):
        self.assertEqual(visible_text(PAGE), "Pension & rules")

    def test_cosmetic_markup_changes_keep_the_same_hash(self):
        restyled = b"<div class='new'>\n  Pension &amp;   rules</div><script>var t=2</script>"
        self.assertEqual(content_hash(PAGE), content_hash(restyled))

    def test_first_same_and_changed(self):
        ok = FetchResult(200, PAGE)
        self.assertEqual(classify(ok, None)[0], "reachable")
        self.assertEqual(classify(ok, content_hash(PAGE))[0], "reachable")
        self.assertEqual(classify(ok, "0" * 64)[0], "changed")

    def test_errors_are_unreachable_without_a_hash(self):
        outcome, digest, note = classify(FetchResult(503, b""), "abc")
        self.assertEqual((outcome, digest), ("unreachable", None))
        self.assertIn("HTTP 503", note)
        self.assertEqual(classify(FetchResult(None, b"", "timeout"), None)[0], "unreachable")

    def test_script_only_pages_need_manual_review(self):
        self.assertEqual(classify(FetchResult(200, b"<script>app()</script>"), None)[0], "manual_review")

    def test_non_https_urls_are_not_fetched(self):
        self.assertEqual(fetch("http://example.gov.in").error, "not an https URL")
