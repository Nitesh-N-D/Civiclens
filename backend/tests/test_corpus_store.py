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


class StoredVectorTests(unittest.TestCase):
    def _row(self, source, model=None, text_hash=None, size=768):
        values = "[" + ",".join(["0.1"] * size) + "]"
        return (source.id, values, model or corpus_store.settings.embedding_model,
                text_hash or corpus_store.embedding_text_hash(source))

    def test_matching_vector_is_kept(self):
        vectors = corpus_store.vectors_from_rows([self._row(SOURCES[0])], SOURCES)
        self.assertEqual(len(vectors[SOURCES[0].id]), 768)

    def test_stale_text_other_model_wrong_size_or_unknown_id_are_dropped(self):
        rows = [
            self._row(SOURCES[0], text_hash="0" * 64),
            self._row(SOURCES[1], model="some-other-embedding"),
            self._row(SOURCES[2], size=3),
            ("not-a-source", "[0.1]", corpus_store.settings.embedding_model, "x"),
            (SOURCES[3].id, "not json", corpus_store.settings.embedding_model,
             corpus_store.embedding_text_hash(SOURCES[3])),
        ]
        self.assertEqual(corpus_store.vectors_from_rows(rows, SOURCES), {})

    def test_hash_changes_when_text_changes(self):
        from dataclasses import replace
        edited = replace(SOURCES[0], text_en=SOURCES[0].text_en + " Updated.")
        self.assertNotEqual(corpus_store.embedding_text_hash(edited), corpus_store.embedding_text_hash(SOURCES[0]))
