import unittest
from unittest.mock import patch

from app.gemini import GeminiProvider, ProviderFailure
from app.corpus import public_schemes
from app.retrieval import lexical_scores, retrieve
from app.security import valid_bearer_token
from app.service import RequestBudget, answer_question, contains_sensitive_details


class NoProvider:
    available = False

    def generate(self, *_args, **_kwargs):
        raise AssertionError("Generation must not run when no key is configured")

    def embed(self, *_args, **_kwargs):
        raise AssertionError("Embeddings must not run when disabled")


class FakeProvider:
    available = True

    def __init__(self, result=None):
        self.result = result
        self.generated = 0

    def generate(self, *_args, **_kwargs):
        self.generated += 1
        if isinstance(self.result, Exception):
            raise self.result
        return self.result

    def embed(self, *_args, **_kwargs):
        raise AssertionError("Embeddings are disabled in these tests")


class RetrievalTests(unittest.TestCase):
    def test_admin_bearer_token_requires_exact_secret_without_leaking_it(self):
        secret = "local-admin-token-do-not-log"
        self.assertTrue(valid_bearer_token(secret, f"Bearer {secret}"))
        self.assertTrue(valid_bearer_token(secret, f"bearer {secret}"))
        self.assertFalse(valid_bearer_token(secret, "Bearer wrong"))
        self.assertFalse(valid_bearer_token(secret, None))
        self.assertFalse(valid_bearer_token("", f"Bearer {secret}"))

    def test_scheme_catalog_is_bilingual_and_never_claims_verified_eligibility(self):
        english = public_schemes("en")
        tamil = public_schemes("ta")
        self.assertEqual(len(english), 2)
        self.assertEqual(len(tamil), 2)
        self.assertEqual(english[0].id, tamil[0].id)
        self.assertTrue(all(not item.eligibility_enabled for item in english + tamil))
        self.assertTrue(all("not verified" in item.status.lower() for item in english))

    def test_lexical_retrieval_ranks_relevant_public_record(self):
        scores = lexical_scores("Pudhumai Penn college student")
        self.assertEqual(len(scores), 4)
        ranked = retrieve("Pudhumai Penn college student", NoProvider())
        self.assertTrue(ranked)
        self.assertEqual(ranked[0][0].id, "myscheme-pudhumai-penn")

    def test_unmatched_query_returns_no_candidates(self):
        self.assertEqual(retrieve("volcanic telescope astronomy", NoProvider()), [])

    def test_privacy_filter_blocks_identifiers_before_retrieval_or_generation(self):
        for question in (
            "My Aadhaar number is 123456789012",
            "My age is 62 and I need a pension",
            "என் வயது 62, முதியோர் உதவி என்ன?",
        ):
            with self.subTest(question=question):
                self.assertTrue(contains_sensitive_details(question))
                provider = FakeProvider()
                response = answer_question(question, "en", provider, RequestBudget(), 10, 100)
                self.assertEqual(response.mode, "search")
                self.assertEqual(response.citations, [])
                self.assertEqual(provider.generated, 0)

    def test_search_fallback_returns_sources_without_api_key(self):
        response = answer_question(
            "Pudhumai Penn college support", "en", NoProvider(), RequestBudget(), 10, 100
        )
        self.assertEqual(response.mode, "search")
        self.assertTrue(response.citations)
        self.assertIn("directory", response.warning.lower())

    def test_generated_citations_are_restricted_to_retrieved_ids(self):
        from app.models import AnswerClaim, GeneratedAnswer

        provider = FakeProvider(GeneratedAnswer(claims=[AnswerClaim(
            text="The directory has a scheme overview.",
            citation_ids=["myscheme-pudhumai-penn", "invented-id"],
        )]))
        response = answer_question(
            "Pudhumai Penn college support", "en", provider, RequestBudget(), 10, 100
        )
        self.assertEqual(response.mode, "ai")
        self.assertEqual([item.id for item in response.citations], ["myscheme-pudhumai-penn"])

    def test_invalid_or_uncited_generation_abstains(self):
        from app.models import AnswerClaim, GeneratedAnswer

        provider = FakeProvider(GeneratedAnswer(claims=[AnswerClaim(
            text="Unsupported claim", citation_ids=["invented-id"]
        )]))
        response = answer_question(
            "Pudhumai Penn college support", "en", provider, RequestBudget(), 10, 100
        )
        self.assertEqual(response.mode, "search")

    def test_provider_failure_falls_back_to_cited_search(self):
        provider = FakeProvider(ProviderFailure("quota", 429))
        response = answer_question(
            "Pudhumai Penn college support", "ta", provider, RequestBudget(), 10, 100
        )
        self.assertEqual(response.mode, "search")
        self.assertTrue(response.citations)
        self.assertTrue(response.text.startswith("பாதுகாப்பாக"))
        self.assertIn("தமிழ் நிபுணர்", response.warning)

    def test_gemini_key_health_never_returns_credentials(self):
        provider = GeminiProvider()
        provider._keys = ("primary-secret", "secondary-secret")
        provider._key_health = ["configured", "configured"]
        self.assertNotIn("primary-secret", str(provider.public_status))
        self.assertNotIn("secondary-secret", str(provider.public_status))
        self.assertEqual(provider.public_status["configured_keys"], 2)

    def test_key_failover_is_limited_to_credential_errors(self):
        provider = GeminiProvider()
        provider._keys = ("primary-secret", "secondary-secret")
        provider._key_health = ["configured", "configured"]
        with patch.object(
            GeminiProvider,
            "_request",
            side_effect=[ProviderFailure("http", 401), {"ok": True}],
        ) as request:
            result = provider._call("test:model", {})
        self.assertEqual(result, {"ok": True})
        self.assertEqual(request.call_count, 2)
        self.assertEqual(provider.public_status["key_health"][0]["status"], "credential_error")

    def test_quota_error_does_not_rotate_to_secondary_key(self):
        provider = GeminiProvider()
        provider._keys = ("primary-secret", "secondary-secret")
        provider._key_health = ["configured", "configured"]
        with patch.object(GeminiProvider, "_request", side_effect=ProviderFailure("http", 429)) as request:
            with self.assertRaises(ProviderFailure):
                provider._call("test:model", {})
        self.assertEqual(request.call_count, 1)
        self.assertEqual(provider.public_status["key_health"][0]["status"], "quota_limited")


if __name__ == "__main__":
    unittest.main()
