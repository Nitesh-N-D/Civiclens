"""Database-backed corpus: invalid rows are dropped and failures keep the last good corpus."""

import unittest
from datetime import date
from unittest.mock import patch

from app import corpus_store
from app.corpus import SOURCES, public_schemes
from app.gemini import GeminiProvider
from app.retrieval import retrieve


def _row(**overrides):
    row = {
        "id": "db-source", "title": "DB Source", "url": "https://example.gov.in/x", "owner": "Dept",
        "locator": "Overview", "status": None, "text_en": "zebrafish hatchery subsidy",
        "text_ta": "", "fetched_at": date(2026, 11, 10), "verified_at": None, "keywords": "",
    }
    row.update(overrides)
    return tuple(row.values())


class SourceRowTests(unittest.TestCase):
    def test_valid_row_maps_with_defaults(self):
        chunk = corpus_store.source_from_row(_row())
        self.assertEqual(chunk.desk_checked_at, "2026-11-10")
        self.assertIn("Review pending", chunk.status)

    def test_unsafe_rows_are_rejected(self):
        self.assertIsNone(corpus_store.source_from_row(_row(url="http://example.gov.in")))
        self.assertIsNone(corpus_store.source_from_row(_row(url="javascript:alert(1)")))
        self.assertIsNone(corpus_store.source_from_row(_row(text_en="  ", text_ta=None)))
        self.assertIsNone(corpus_store.source_from_row(_row(title="")))

    def test_change_with_unknown_status_is_rejected(self):
        row = ("c", "Name", None, [], "rumour", "rename", "s", "s", "t", "https://x.gov.in", date(2026, 1, 1))
        self.assertIsNone(corpus_store.change_from_row(row))


class RefreshTests(unittest.TestCase):
    def tearDown(self):
        corpus_store.reset()

    def test_database_failure_keeps_built_in_corpus(self):
        with patch.object(corpus_store, "load_from_database", side_effect=OSError("down")), \
                self.assertLogs("civiclens.corpus", level="WARNING"):
            corpus_store.refresh()
        self.assertIs(corpus_store.active(), corpus_store.BUILT_IN)

    def test_empty_database_keeps_current_corpus(self):
        with patch.object(corpus_store, "load_from_database", return_value=None):
            corpus_store.refresh()
        self.assertIs(corpus_store.active(), corpus_store.BUILT_IN)

    def test_loaded_corpus_drives_retrieval_and_schemes(self):
        chunk = corpus_store.source_from_row(_row())
        # Alongside the real sources so the term weights behave as in production.
        loaded = corpus_store.Corpus((*SOURCES, chunk), {}, (), "database")
        with patch.object(corpus_store, "load_from_database", return_value=loaded):
            corpus_store.refresh()
        hits = retrieve("zebrafish hatchery", GeminiProvider())
        self.assertEqual([source.id for source, _ in hits], ["db-source"])
        self.assertEqual(public_schemes(), [])
        corpus_store.reset()
        self.assertEqual(len(corpus_store.active().sources), len(SOURCES))


if __name__ == "__main__":
    unittest.main()
