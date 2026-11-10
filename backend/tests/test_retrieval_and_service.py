import unittest
from dataclasses import replace
from unittest.mock import patch

from app.corpus import public_schemes
from app.gemini import GeminiProvider, ProviderFailure
from app.retrieval import lexical_scores, retrieve
from app.security import valid_bearer_token
from app.service import (
    AnswerCache,
    ClientLimiter,
    RequestBudget,
    answer_question,
    contains_sensitive_details,
)


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
            "my aadhaar is 1234 5678 9012",
            "Call me on 9876543210 about pensions",
            "my bank account number: 50100234567890",
            "OTP is 482913, is this scheme real?",
            "PAN ABCDE1234F for scholarship",
            "என் ஆதார் எண் 123456789012",
            "mail me at someone@example.com",
        ):
            with self.subTest(question=question):
                self.assertTrue(contains_sensitive_details(question))
                provider = FakeProvider()
                response = answer_question(question, "en", provider, RequestBudget(), 10, 100)
                self.assertEqual(response.mode, "search")
                self.assertEqual(response.citations, [])
                self.assertEqual(provider.generated, 0)

    def test_situational_context_is_allowed_with_privacy_reminder(self):
        # TD-01: the core use case is people describing their situation.
        for question, expected in (
            ("நான் கல்லூரியில் படிக்கிறேன், எனக்கு என்ன உதவித்தொகை கிடைக்கும்?", "myscheme-pudhumai-penn"),
            ("I am a student, what scholarships can I get?", "myscheme-pudhumai-penn"),
            ("I am 67 years old, any pension?", "cra-social-security-overview"),
            ("My age is 62 and I need a pension", "cra-social-security-overview"),
        ):
            with self.subTest(question=question):
                self.assertFalse(contains_sensitive_details(question))
                response = answer_question(question, "en", NoProvider(), RequestBudget(), 10, 100)
                self.assertTrue(response.citations)
                self.assertEqual(response.citations[0].id, expected)
                self.assertIn("personal details", response.warning)

    def test_general_question_mentioning_an_id_type_is_not_blocked(self):
        question = "Is Aadhaar needed for the old age pension?"
        self.assertFalse(contains_sensitive_details(question))
        response = answer_question(question, "en", NoProvider(), RequestBudget(), 10, 100)
        self.assertEqual(response.citations[0].id, "cra-social-security-overview")
        self.assertNotIn("personal details", response.warning)

    def test_off_topic_questions_abstain_without_sources(self):
        # TD-03: unrelated questions must not be answered with unrelated sources.
        for question in (
            "what is the weather in Chennai",
            "Tamil Nadu bus timings",
            "current government scheme for cricket",
            "how do I get a passport renewal",
        ):
            with self.subTest(question=question):
                self.assertEqual(retrieve(question, NoProvider()), [])
                response = answer_question(question, "en", FakeProvider(), RequestBudget(), 10, 100)
                self.assertEqual(response.citations, [])
                self.assertEqual(response.mode, "search")

    def test_ai_answers_are_cached_to_save_quota(self):
        from app.models import AnswerClaim, GeneratedAnswer

        provider = FakeProvider(GeneratedAnswer(claims=[AnswerClaim(
            text="The directory has a scheme overview.", citation_ids=["myscheme-pudhumai-penn"],
        )]))
        cache = AnswerCache()
        first = answer_question("Pudhumai Penn support", "en", provider, RequestBudget(), 10, 100, cache)
        second = answer_question("  pudhumai penn   SUPPORT ", "en", provider, RequestBudget(), 10, 100, cache)
        self.assertEqual(first.mode, "ai")
        self.assertEqual(second.text, first.text)
        self.assertEqual(provider.generated, 1)

    def test_client_limiter_isolates_clients(self):
        limiter = ClientLimiter()
        self.assertTrue(limiter.allow("a", 2, 10))
        self.assertTrue(limiter.allow("a", 2, 10))
        self.assertFalse(limiter.allow("a", 2, 10))
        self.assertTrue(limiter.allow("b", 2, 10))

    def test_ask_endpoint_rate_limits_per_client_with_retry_after(self):
        from fastapi import HTTPException
        from starlette.requests import Request

        from app import main
        from app.models import AskRequest

        def request_from(host: str) -> Request:
            return Request({"type": "http", "headers": [], "client": (host, 1234)})

        payload = AskRequest(question="Pudhumai Penn college support", language="en")
        with patch.object(main, "client_limiter", ClientLimiter()), \
                patch.object(main, "provider", NoProvider()), \
                patch.object(main, "settings", replace(main.settings, client_requests_per_minute=2)):
            main.ask(payload, request_from("10.0.0.1"))
            main.ask(payload, request_from("10.0.0.1"))
            with self.assertRaises(HTTPException) as raised:
                main.ask(payload, request_from("10.0.0.1"))
            self.assertEqual(raised.exception.status_code, 429)
            self.assertEqual(raised.exception.headers["Retry-After"], "60")
            self.assertEqual(main.ask(payload, request_from("10.0.0.2")).mode, "search")

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

    def test_claims_with_amounts_or_words_absent_from_evidence_are_dropped(self):
        from app.models import AnswerClaim, GeneratedAnswer

        provider = FakeProvider(GeneratedAnswer(claims=[
            AnswerClaim(text="Social security pensions are Rs 1,200 a month from August 2023.",
                        citation_ids=["cra-social-security-overview"]),
            AnswerClaim(text="The old age pension is Rs 3,000 a month.",
                        citation_ids=["cra-social-security-overview"]),
            AnswerClaim(text="Cricket coaching camps run every summer.",
                        citation_ids=["cra-social-security-overview"]),
        ]))
        response = answer_question("old age pension amount", "en", provider, RequestBudget(), 10, 100)
        self.assertEqual(response.mode, "ai")
        self.assertIn("1,200", response.text)
        self.assertNotIn("3,000", response.text)
        self.assertNotIn("Cricket", response.text)

    def test_answer_with_only_unsupported_claims_abstains(self):
        from app.models import AnswerClaim, GeneratedAnswer

        provider = FakeProvider(GeneratedAnswer(claims=[AnswerClaim(
            text="Every student receives Rs 50,000.", citation_ids=["myscheme-pudhumai-penn"])]))
        response = answer_question("Pudhumai Penn college support", "en", provider, RequestBudget(), 10, 100)
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


    def test_quota_error_starts_cooldown_without_further_network_calls(self):
        provider = GeminiProvider()
        provider._keys = ("primary-secret",)
        provider._key_health = ["configured"]
        with patch.object(GeminiProvider, "_request", side_effect=ProviderFailure("http", 429, 30.0)) as request:
            with self.assertRaises(ProviderFailure):
                provider._call("test:model", {})
            with self.assertRaises(ProviderFailure) as again:
                provider._call("test:model", {})
        self.assertEqual(request.call_count, 1)
        self.assertEqual(again.exception.status, 429)
        self.assertEqual(provider.public_status["state"], "RATE_LIMITED")

    def test_health_state_vocabulary(self):
        provider = GeminiProvider()
        provider._keys = ()
        self.assertEqual(provider.public_status["state"], "CONFIGURATION_ERROR")
        provider._keys = ("primary-secret", "secondary-secret")
        provider._key_health = ["configured", "configured"]
        self.assertEqual(provider.public_status["state"], "HEALTHY")
        provider._key_health = ["credential_error", "healthy"]
        self.assertEqual(provider.public_status["state"], "DEGRADED")
        provider._last_failure = "provider_unavailable"
        self.assertEqual(provider.public_status["state"], "UNAVAILABLE")


if __name__ == "__main__":
    unittest.main()
