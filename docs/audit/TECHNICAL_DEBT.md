# Technical debt register (Phase 0)

**Date:** 10 November 2026
**Severity:** S1 blocks the product vision or breaks soon · S2 must fix before any public exposure · S3 fix during normal development

Each item was reproduced or verified during the audit unless marked otherwise.

## Status (updated 10 Nov 2026, Phase 8)

| ID | Status |
|---|---|
| TD-01 | **Fixed.** Only identifiers/secrets are blocked; situational context is allowed and adds a privacy reminder. Tests cover both. |
| TD-02 | **Fixed.** Default `gemini-3.5-flash-lite` (developer confirmed both keys share one free-tier project). Embeddings stay `gemini-embedding-001` (supported to May 2028, off by default). |
| TD-03 | **Fixed.** EN/TA stop-words, prefix matching, curated keywords, absolute score floor, relative cut-off; 4 off-topic cases in the eval, which now fails CI on regression. |
| TD-04 | **Mostly fixed (10 Nov 2026).** Sources re-checked; CRA amounts now quoted with their 2023 dates; aliases added; change notices labelled official/news. Open: the BC/MBC department page (TLS error) and human verification of every record. |
| TD-05 | **Fixed.** Per-client limiter (5/min, 40/day default) with `Retry-After`, plus a 12 h in-memory answer cache. |
| TD-06 | **Fixed.** Brief's five health states; 429 cool-down honours `Retry-After`. |
| TD-07 | Partly: numeric and lexical claim–evidence gate. A live run of 8 answers had 23 claims and 0 rejections (see `docs/evaluation/RAG_EVALUATION_REPORT.md`). There is no entailment model, so a person still needs to review answers. |
| TD-08 | **Fixed.** 16 KB body limit, security headers, `no-store` on answers; sync handlers run in FastAPI's thread pool. |
| TD-09 | **Fixed (Phase 8).** Supabase Auth sign-in; the API verifies each token with Supabase and takes the role (viewer/reviewer/maintainer) from `admin_roles` (migration `0005`). Writes need a Supabase sign-in and a reviewer role, and each is audit-logged in the same transaction. The static token is local-only and viewer-only. |
| TD-10 | **Fixed.** MIT `LICENSE`. |
| TD-12 | **Fixed (Phase 8).** CI runs ruff, backend tests, the retrieval eval, ESLint, Vitest (component and integration tests), the frontend type-check/build and `npm audit`. No formatter is enforced. |
| TD-11 | **Fixed (Phase 8).** `App.tsx` is state and composition only; API calls in `api.ts`, the theme in `hooks/useTheme.ts`, and each section in `components/`. |
| TD-14 | **Fixed.** Corpus tokenised once at import. |
| TD-15, TD-16 | **Fixed** (doc corrected; branches pushed). |
| TD-17 | Mostly fixed (Phases 6–7): `0002` adds pgvector + HNSW and EN/TA full-text; `scripts/migrate.py` applies migrations once each; `0003` adds the persistent daily budget and RLS; `0004` + `scripts/seed_corpus.py` move the corpus into PostgreSQL and the API serves it from there with a built-in fallback. Phase 9: `0006` + `scripts/embed_corpus.py` store Gemini document embeddings in `embedding_768` with a text hash, and the API reuses them at startup with no Gemini call. Open: ranking is still done in process rather than with SQL full-text/vector search. That's fine at four documents, but should move to SQL as the corpus grows. |

## S1

### TD-01: The privacy filter blocks ordinary personal-context questions in both languages
`service.SENSITIVE_PATTERNS` includes `(?:நான்|என் குடும்பம்|…)` ("I", "my family") and `I am a student|farmer|widow…`. Reproduced on 10 Nov 2026:

| Query | Blocked? |
|---|---|
| நான் கல்லூரியில் படிக்கிறேன். எனக்கு என்ன அரசு உதவித்தொகைகள் கிடைக்கும்? (the brief's flagship example) | **Yes** |
| I am a student, what scholarships can I get? | **Yes** |
| I am 67 years old, any pension? | **Yes** |
| What scholarships exist for college girls? | No |

A citizen cannot describe their situation, which is the core of eligibility guidance. **Root cause:** one filter mixes two concerns. *Identifiers* (Aadhaar, PAN, phone, email, IFSC, account numbers, OTPs) must always be blocked. *Situational attributes* (student, age range, occupation) are what the product needs, but they should not be sent verbatim to free-tier Gemini.
**Proposed fix (Phase 6/9):** keep blocking identifiers. Collect situational attributes through a structured, consent-explained form evaluated by deterministic rules, and send Gemini only coarse, de-identified categories (e.g. `occupation=student`, `age_band=18-25`). Strip or generalise first-person free text before the provider call instead of refusing the question.

### TD-02: The default Gemini model shuts down on 1 December 2026
`config.py` and `.env.example` default to `gemini-2.5-flash`. Google's deprecations page (checked 10 Nov 2026) lists a shutdown date of **1 December 2026**: requests re-route to `gemini-3.5-flash-lite`, and API access is already restricted to existing users. `gemini-embedding-001` is still served (shutdown 14 May 2028), but `gemini-embedding-2` is now the recommended embedding model.
**Proposed fix:** change the defaults once the developer confirms the per-project free-tier quotas shown in their AI Studio dashboard. See [FREE_TIER_AUDIT.md](../research/FREE_TIER_AUDIT.md) for candidates. No code changes were made in this phase.

### TD-03: Retrieval has no confidence threshold, so off-topic questions are answered with citations
`retrieval.retrieve` divides lexical scores by the maximum, so the top document always gets a lexical component of 1.0 × 0.55. Any overlap on a common token (`in`, `the`, `Tamil`, `Nadu`) produces "evidence":

| Query | Returned |
|---|---|
| what is the weather in Chennai | 4 sources (top 0.55) |
| Tamil Nadu bus timings | 4 sources |
| current government scheme for cricket | 4 sources |

In search-only mode these appear as citations. The offline eval reports Recall@4 7/7 only because its single negative case happens to share no tokens.
**Proposed fix:** stop-word list (EN + TA), threshold on the absolute (un-normalised) BM25 score, and negative cases in the eval set, with false-positive rate as a reported metric.

### TD-04: The corpus may be stale after the 2026 change of state government
After the May 2026 Assembly election the new government's budget renamed several welfare schemes; secondary reporting includes *Kalaignar Magalir Urimai Thogai → Magalir Urimai Thittam* and *Naan Mudhalvan → Vetri Skill Training Scheme*. The four corpus records were desk-checked on 9 Nov 2026, but they cite myScheme summaries rather than post-budget Government Orders. Pudhumai Penn's current status was **not confirmed** by this audit.
**Proposed fix:** Phase 2 must check each record against the current owning department or GO. This is also concrete evidence for the source-monitoring feature (Module G).

## S2: required before any public exposure

| ID | Debt | Fix |
|---|---|---|
| TD-05 | `RequestBudget` is global: one anonymous client can use the whole daily Gemini allowance, denying AI answers to everyone else | Per-IP/session token bucket in front of the global budget; cache answers for repeated public questions |
| TD-06 | Provider health states do not match the brief (`HEALTHY / DEGRADED / RATE_LIMITED / UNAVAILABLE / CONFIGURATION_ERROR`); `Retry-After` is ignored | Map the existing states; honour `Retry-After` with a cool-down instead of immediate retries |
| TD-07 | Citation validation checks only that cited IDs were retrieved, not that the passage supports the claim | Claim-to-evidence check (lexical overlap gate first, then an LLM entailment pass only where evaluation shows benefit) |
| TD-08 | No per-request body-size limit, no security headers, sync `urllib` inside request handlers | Middleware for size limits and headers; move to `httpx` with a timeout, or run in a threadpool |
| TD-09 | Single shared static admin token | Supabase Auth (or similar) + roles before any admin mutation is enabled |
| TD-10 | No `LICENSE` | **Developer decision.** Licence choice affects reuse and contributions |

## S3: normal development

| ID | Debt |
|---|---|
| TD-11 | `App.tsx` is a 28 kB single component with inline strings; no `locales/`, router, or feature folders |
| TD-12 | No frontend tests, linter, or formatter on either side; no CI workflow |
| TD-13 | Settings frozen at import time, so environment-dependent tests are awkward |
| TD-14 | The corpus is re-tokenised on every request (fine at 4 docs, but O(N) per query) |
| TD-15 | `MARKET_RESEARCH.md` Phase 0 section says "not a git repository" (stale; corrected in this phase) |
| TD-16 | Local `main` is 6 commits ahead of `origin/main` (unpushed work; pushing is the developer's decision) |
| TD-17 | Migration has embeddings as JSONB, no FTS/pgvector, and no runner |
