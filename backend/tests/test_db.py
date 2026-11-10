"""Optional PostgreSQL budget: the API must keep answering whatever the database does."""

import unittest
from dataclasses import replace
from unittest.mock import MagicMock, patch

from app import db
from app.service import PersistentBudget


def _settings(url: str):
    return replace(db.settings, database_url=url)


class DatabaseStatusTests(unittest.TestCase):
    def setUp(self):
        db._status_cache = None
        db._budget_retry_at = 0.0

    def test_not_configured_without_url(self):
        with patch.object(db, "settings", _settings("")):
            self.assertEqual(db.database_status(), "not_configured")
            self.assertIsNone(db.claim_daily_slot("gemini", 5))

    def test_unreachable_database_reports_unavailable_without_leaking_url(self):
        url = "postgresql://user:secret-password@example.invalid:6543/postgres"
        with patch.object(db, "settings", _settings(url)), patch.object(
            db, "connect", side_effect=OSError("could not connect")
        ), self.assertLogs("civiclens.db", level="WARNING") as logs:
            self.assertEqual(db.database_status(), "unavailable")
        self.assertNotIn("secret-password", " ".join(logs.output))

    def test_claim_returns_none_and_pauses_after_failure(self):
        failing = MagicMock(side_effect=OSError("down"))
        with patch.object(db, "settings", _settings("postgresql://x")), patch.object(db, "connect", failing):
            with self.assertLogs("civiclens.db", level="WARNING"):
                self.assertIsNone(db.claim_daily_slot("gemini", 5))
            # Second call inside the pause must not touch the database again.
            self.assertIsNone(db.claim_daily_slot("gemini", 5))
        self.assertEqual(failing.call_count, 1)

    def test_claim_maps_returned_row_to_allow_or_deny(self):
        for row, expected in (((3,), True), (None, False)):
            conn = MagicMock()
            conn.__enter__.return_value = conn
            conn.execute.return_value.fetchone.return_value = row
            with patch.object(db, "settings", _settings("postgresql://x")), patch.object(
                db, "connect", return_value=conn
            ):
                self.assertIs(db.claim_daily_slot("gemini", 5), expected)


class PersistentBudgetTests(unittest.TestCase):
    def test_falls_back_to_memory_when_database_absent(self):
        budget = PersistentBudget()
        with patch("app.db.claim_daily_slot", return_value=None):
            self.assertTrue(budget.allow(per_minute=10, per_day=1))
            self.assertFalse(budget.allow(per_minute=10, per_day=1))

    def test_persisted_denial_wins(self):
        budget = PersistentBudget()
        with patch("app.db.claim_daily_slot", return_value=False):
            self.assertFalse(budget.allow(per_minute=10, per_day=100))

    def test_minute_window_still_applies_with_database(self):
        budget = PersistentBudget()
        with patch("app.db.claim_daily_slot", return_value=True):
            self.assertTrue(budget.allow(per_minute=1, per_day=100))
            self.assertFalse(budget.allow(per_minute=1, per_day=100))


if __name__ == "__main__":
    unittest.main()
