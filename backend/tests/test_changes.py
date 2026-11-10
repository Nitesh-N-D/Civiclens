import unittest

from app.changes import CHANGES, matching_changes
from app.retrieval import retrieve
from app.service import RequestBudget, answer_question
from tests.test_retrieval_and_service import NoProvider


def ask(question, language="en"):
    return answer_question(question, language, NoProvider(), RequestBudget(), 10, 100)


class ChangeTrackingTests(unittest.TestCase):
    def test_every_change_names_its_evidence_type_and_check_date(self):
        for change in CHANGES:
            self.assertIn(change.status, {"official", "reported"})
            self.assertTrue(change.source_url.startswith("https://"))
            self.assertRegex(change.checked_at, r"^\d{4}-\d{2}-\d{2}$")
            self.assertTrue(change.summary_en and change.summary_ta)
        reported = [change for change in CHANGES if change.status == "reported"]
        # A news-sourced change must say so, so it is never read as a government decision.
        for change in reported:
            self.assertIn("news", change.summary_en.lower())

    def test_old_and_new_names_find_the_same_change(self):
        for question in ("Magalir Urimai Thogai amount", "What is Mathippumigu Magalir Thittam?",
                         "மகளிர் உரிமைத் தொகை எப்போது வரும்?"):
            ids = [change.id for change in matching_changes(question)]
            self.assertIn("magalir-urimai-rename-reported-2026", ids, question)

    def test_unrelated_question_has_no_change_notice(self):
        self.assertEqual(matching_changes("How do I get an income certificate?"), [])

    def test_scheme_without_reviewed_source_abstains_but_shows_the_notice(self):
        response = ask("Kalaignar Magalir Urimai Thogai eligibility")
        self.assertEqual(response.citations, [])
        self.assertEqual([notice.status for notice in response.notices], ["reported"])

    def test_pension_question_gets_official_rate_notice_and_source(self):
        response = ask("old age pension amount", "ta")
        self.assertEqual(response.citations[0].id, "cra-social-security-overview")
        self.assertEqual(response.notices[0].status, "official")
        self.assertIn("1,200", response.notices[0].summary)

    def test_privacy_blocked_question_gets_no_notices(self):
        response = ask("My Aadhaar number is 1234 5678 9012, Magalir Urimai status?")
        self.assertEqual(response.notices, [])
        self.assertEqual(response.citations, [])

    def test_alternate_spellings_retrieve_pudhumai_penn(self):
        for question in ("Puthumai Penn scheme", "Moovalur Ramamirtham Ammaiyar scheme"):
            hits = retrieve(question, NoProvider(), limit=4)
            self.assertEqual(hits[0][0].id, "myscheme-pudhumai-penn", question)

    def test_changes_endpoint_is_bilingual(self):
        from app import main

        english = main.changes("en")["changes"]
        tamil = main.changes("ta")["changes"]
        self.assertEqual(len(english), len(CHANGES))
        self.assertNotEqual(english[0]["summary"], tamil[0]["summary"])


if __name__ == "__main__":
    unittest.main()
