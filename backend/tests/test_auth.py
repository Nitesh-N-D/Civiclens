"""Maintainer sign-in: Supabase token -> admin_roles role; static token is viewer-only."""

import unittest
from dataclasses import replace
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from fastapi import HTTPException
from pydantic import ValidationError

from app import auth, main
from app.models import SourceCheckRequest

CONFIGURED = replace(
    auth.settings,
    admin_token="",
    supabase_url="https://example.supabase.co",
    supabase_publishable_key="sb_publishable_test",
    database_url="postgresql://x",
)
USER = {"id": "11111111-1111-1111-1111-111111111111", "email": "reviewer@example.org"}


class AuthenticateTests(unittest.TestCase):
    def setUp(self):
        auth.clear_cache()

    def test_static_token_is_viewer_only(self):
        settings = replace(auth.settings, admin_token="local-token")
        with patch.object(auth, "settings", settings):
            principal = auth.authenticate("Bearer local-token")
        self.assertEqual((principal.role, principal.via), ("viewer", "static_token"))
        self.assertFalse(principal.can("reviewer"))

    def test_nothing_configured_means_no_access(self):
        settings = replace(auth.settings, admin_token="", supabase_url="", supabase_publishable_key="")
        with patch.object(auth, "settings", settings), patch.object(auth, "supabase_user") as remote:
            self.assertIsNone(auth.authenticate("Bearer anything"))
        remote.assert_not_called()

    def test_supabase_user_gets_role_from_table(self):
        with patch.object(auth, "settings", CONFIGURED), patch.object(auth, "supabase_user", return_value=USER), \
                patch.object(auth, "role_for", return_value="reviewer"):
            principal = auth.authenticate("Bearer jwt")
        self.assertEqual((principal.email, principal.role, principal.via), (USER["email"], "reviewer", "supabase"))
        self.assertTrue(principal.can("reviewer"))
        self.assertFalse(principal.can("maintainer"))

    def test_signed_in_account_without_role_has_no_access(self):
        with patch.object(auth, "settings", CONFIGURED), patch.object(auth, "supabase_user", return_value=USER), \
                patch.object(auth, "role_for", return_value=None):
            self.assertIsNone(auth.authenticate("Bearer jwt"))

    def test_rejected_token_and_supabase_outage_fail_closed(self):
        with patch.object(auth, "settings", CONFIGURED), patch.object(auth, "supabase_user", return_value=None):
            self.assertIsNone(auth.authenticate("Bearer bad"))
        auth.clear_cache()
        with patch.object(auth, "settings", CONFIGURED), patch.object(
            auth, "supabase_user", side_effect=TimeoutError()
        ):
            self.assertIsNone(auth.authenticate("Bearer jwt"))

    def test_result_is_cached_by_token_hash_not_token(self):
        remote = MagicMock(return_value=USER)
        with patch.object(auth, "settings", CONFIGURED), patch.object(auth, "supabase_user", remote), \
                patch.object(auth, "role_for", return_value="viewer"):
            auth.authenticate("Bearer secret-jwt-value")
            auth.authenticate("Bearer secret-jwt-value")
        self.assertEqual(remote.call_count, 1)
        self.assertNotIn("secret-jwt-value", " ".join(auth._cache))

    def test_malformed_header_is_rejected(self):
        with patch.object(auth, "settings", CONFIGURED), patch.object(auth, "supabase_user") as remote:
            for header in (None, "", "Bearer", "Basic abc", "Bearer   "):
                self.assertIsNone(auth.authenticate(header))
        remote.assert_not_called()


class AdminEndpointTests(unittest.TestCase):
    def _as(self, role: str | None, via: str = "supabase"):
        principal = None if role is None else auth.Principal(USER["id"], USER["email"], role, via)
        return patch.object(main, "authenticate", return_value=principal)

    def _status(self, call) -> int:
        with self.assertRaises(HTTPException) as caught:
            call()
        return caught.exception.status_code

    def _check(self, source_id="s1", outcome="reachable", note="opened the page"):
        return main.record_source_check(source_id, SourceCheckRequest(outcome=outcome, note=note), "Bearer x")

    def test_overview_hidden_without_access(self):
        with self._as(None):
            self.assertEqual(self._status(lambda: main.admin_overview(None)), 404)

    def test_overview_reports_role_and_write_access(self):
        settings = replace(main.settings, database_url="")
        with self._as("reviewer"), patch.object(main, "settings", settings):
            body = main.admin_overview("Bearer x")
        self.assertEqual(body["you"]["role"], "reviewer")
        self.assertTrue(body["mutations_enabled"])
        with self._as("viewer", via="static_token"), patch.object(main, "settings", settings):
            self.assertFalse(main.admin_overview("Bearer x")["mutations_enabled"])

    def test_viewer_and_static_token_cannot_record_checks(self):
        with patch.object(main.admin, "record_source_check") as write:
            with self._as("viewer"):
                self.assertEqual(self._status(self._check), 403)
            with self._as("maintainer", via="static_token"):
                self.assertEqual(self._status(self._check), 403)
        write.assert_not_called()

    def test_reviewer_records_check(self):
        result = {"id": 7, "source_id": "s1", "outcome": "changed", "checked_at": "2026-11-10T00:00:00+00:00"}
        with self._as("reviewer"), patch.object(main.admin, "record_source_check", return_value=result) as write:
            self.assertEqual(self._check(outcome="changed", note=" new GO "), result)
        self.assertEqual(write.call_args.args[1:], ("s1", "changed", "new GO"))

    def test_invalid_outcome_and_unknown_source(self):
        with self.assertRaises(ValidationError):
            SourceCheckRequest(outcome="deleted", note="abc")
        with self._as("reviewer"), patch.object(main.admin, "record_source_check", side_effect=LookupError("s9")):
            self.assertEqual(self._status(lambda: self._check(source_id="s9")), 404)


class AdminStoreTests(unittest.TestCase):
    def test_check_and_audit_written_in_one_transaction(self):
        conn = MagicMock()
        conn.__enter__.return_value = conn
        conn.execute.return_value.fetchone.side_effect = [(1,), (5, datetime(2026, 11, 10, tzinfo=UTC))]
        principal = auth.Principal(USER["id"], USER["email"], "reviewer", "supabase")
        with patch("app.admin.connect", return_value=conn):
            result = main.admin.record_source_check(principal, "s1", "reachable", "ok")
        conn.transaction.assert_called_once()
        statements = [call.args[0] for call in conn.execute.call_args_list]
        self.assertTrue(any("INSERT INTO source_checks" in sql for sql in statements))
        self.assertTrue(any("INSERT INTO audit_log" in sql for sql in statements))
        self.assertEqual(result["id"], 5)

    def test_unknown_source_writes_nothing(self):
        conn = MagicMock()
        conn.__enter__.return_value = conn
        conn.execute.return_value.fetchone.return_value = None
        principal = auth.Principal(USER["id"], USER["email"], "reviewer", "supabase")
        with patch("app.admin.connect", return_value=conn), self.assertRaises(LookupError):
            main.admin.record_source_check(principal, "nope", "reachable", "ok")
        self.assertEqual(conn.execute.call_count, 1)


if __name__ == "__main__":
    unittest.main()
