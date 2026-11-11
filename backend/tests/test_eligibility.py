"""Eligibility screening is deterministic, source-grounded and never guarantees eligibility."""

import asyncio
import unittest

from app import eligibility, main
from app.corpus import SOURCES, public_schemes
from app.models import EligibilityRequest

SOURCE_TEXT = {source.id: source.text_en for source in SOURCES}
PP_ALL_MET = {"state": "tamil_nadu", "gender": "female", "school_type": "tn_government", "education": "undergraduate"}


class GroundingTests(unittest.TestCase):
    def test_every_criterion_basis_is_quoted_from_its_source(self):
        for criteria in eligibility.CRITERIA.values():
            for criterion in criteria:
                self.assertIn(criterion.basis, SOURCE_TEXT[criterion.source_id], criterion.id)

    def test_documents_and_guidance_point_at_real_criteria_and_sources(self):
        for scheme_id, documents in eligibility.DOCUMENTS.items():
            ids = {c.id for c in eligibility.CRITERIA[scheme_id]}
            for document in documents:
                self.assertIn(document.criterion_id, ids)
                self.assertIn(document.source_id, SOURCE_TEXT)
        for guide in eligibility.GUIDANCE.values():
            self.assertIn(guide.source_id, SOURCE_TEXT)

    def test_every_profile_field_explains_why_it_is_asked(self):
        self.assertEqual(set(eligibility.FIELD_PURPOSE), set(eligibility.PROFILE_FIELDS))


class AssessTests(unittest.TestCase):
    def test_all_conditions_met_still_requires_official_verification(self):
        result = eligibility.assess("pudhumai-penn", PP_ALL_MET, "en")
        self.assertEqual(result["status"], "requires_official_verification")
        self.assertTrue(all(row["outcome"] == "met" for row in result["criteria"]))

    def test_one_unmet_condition_appears_ineligible(self):
        result = eligibility.assess("pudhumai-penn", {**PP_ALL_MET, "school_type": "other"}, "en")
        self.assertEqual(result["status"], "appears_ineligible")

    def test_missing_answers_are_insufficient_information(self):
        result = eligibility.assess("free-education-tn", {"state": "tamil_nadu"}, "en")
        self.assertEqual(result["status"], "insufficient_information")
        self.assertEqual(result["missing_fields"], ["college_type", "community", "education"])

    def test_unknown_fields_and_values_are_ignored(self):
        self.assertEqual(eligibility.clean_profile({"aadhaar": "1234", "state": "mars", "gender": "female"}),
                         {"gender": "female"})

    def test_documents_are_never_marked_mandatory_and_skip_unmet_conditions(self):
        result = eligibility.assess("free-education-tn", {"community": "other"}, "en")
        self.assertNotIn("fe-community", [d["criterion_id"] for d in result["documents"]])
        self.assertTrue(all(d["mandatory"] is False for d in result["documents"]))

    def test_verified_criteria_can_reach_appears_eligible(self):
        self.assertEqual(eligibility.overall(["met", "met"], verified=True), "appears_eligible")

    def test_tamil_labels_and_steps(self):
        result = eligibility.assess("pudhumai-penn", {}, "ta")
        self.assertIn("மாணவி", [row["label"] for row in result["criteria"]])
        self.assertTrue(result["guidance"]["steps"][0].startswith("கீழே"))


class EndpointTests(unittest.TestCase):
    def test_check_returns_results_and_only_cited_sources(self):
        data = main.eligibility_check(EligibilityRequest(profile=PP_ALL_MET, scheme_ids=["pudhumai-penn", "nope"]))
        self.assertEqual([r["scheme_id"] for r in data["results"]], ["pudhumai-penn"])
        self.assertEqual([s["id"] for s in data["sources"]], ["myscheme-pudhumai-penn"])

    def test_check_without_scheme_ids_screens_every_scheme(self):
        data = main.eligibility_check(EligibilityRequest())
        self.assertEqual({r["scheme_id"] for r in data["results"]}, set(eligibility.CRITERIA))

    def test_compare_limits_to_known_schemes(self):
        data = main.compare("pudhumai-penn,free-education-tn,unknown", "en")
        self.assertEqual(len(data["schemes"]), 2)
        self.assertEqual(len(data["sources"]), 2)

    def test_questions_and_scheme_cards_enable_screening(self):
        self.assertEqual(len(main.eligibility_questions("ta")["questions"]), len(eligibility.PROFILE_FIELDS))
        self.assertTrue(all(card.eligibility_enabled for card in public_schemes()))

    def test_eligibility_responses_are_not_cached(self):
        from tests.test_security_middleware import _ok, _request
        response = asyncio.run(main.guard_requests(_request("/api/eligibility"), _ok))
        self.assertEqual(response.headers["cache-control"], "no-store")
