# Changelog

## 2026-11-10 — Phase 5: deployment preparation (not deployed)

- **Migration 0002 (TD-17):** pgvector `VECTOR(768)` column with HNSW index, English and Tamil (`simple`) full-text GIN indexes, `scheme_aliases` and `scheme_changes` tables. Additive; not applied anywhere.
- **Hosting config:** `render.yaml` for a free Render API service (manual deploys, secrets entered in the dashboard) and `frontend/public/_headers` for Cloudflare Pages security headers.
- **Frontend:** optional public `VITE_API_BASE` so the client can call an API on another origin.

## 2026-11-10 — Phase 4: hardening

- **Provider health (TD-06):** `/api/health` and the maintainer overview report `HEALTHY`, `DEGRADED`, `RATE_LIMITED`, `UNAVAILABLE` or `CONFIGURATION_ERROR`. After a Gemini 429 the backend stops calling Gemini for the server's `Retry-After` (default 60 s, max 10 min) and answers in cited search mode.
- **Claim–evidence gate (TD-07):** each generated claim must use only numbers that appear in the sources it cites (so an invented amount, age or date is dropped) and share at least a quarter of its content words with them. Answers left with no supported claim fall back to search mode. This is a heuristic, not entailment.
- **Request hardening (TD-08):** request bodies over 16 KB get 413; responses carry `nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, a JSON-only CSP (docs page exempt) and `Cache-Control: no-store` on answers. Handlers are sync, so FastAPI already runs Gemini calls in its thread pool.
- **Lint (TD-12):** ruff (`backend/ruff.toml`, dev-only `requirements-dev.txt`) runs in CI.
- Tests: 34 unit tests.

## 2026-11-10 — Phase 3: source freshness, change tracking, helper checklist

- **Freshness re-check (TD-04):** every source re-checked against 2026 information on 10 Nov 2026. The CRA pension record now states the rates the official page gives (Rs 1,500 disability pension from 1 Jan 2023; Rs 1,200 for the others from Aug 2023), labelled as dated. Pudhumai Penn and the Free Education Scheme gained alternate names (Puthumai Penn, Moovalur Ramamirtham Ammaiyar, FES) as search keywords. The BC/MBC department page could not be fetched (its TLS certificate does not verify), so the Free Education record stays a directory lead.
- **Scheme change tracking:** new `backend/app/changes.py` and `GET /api/changes`. Answers now carry `notices` for matching renames, continuations and rate revisions. Every notice says whether it comes from an official page or a news report, and news-only items (Pudhumai Penn continuation, the reported Magalir Urimai rename) are labelled as not confirmed by a Government Order. Notices are never used as answer evidence and are not attached to privacy-blocked questions.
- **Helper mode:** a "Print checklist" button prints the question, the cited answer, official links with check dates, change notices, and four safety steps (confirm the rule, ask which documents, apply only through official channels, never share Aadhaar/bank/OTP). No personal data is printed.
- **Frontend structure (TD-11, part):** UI strings moved to `src/copy.ts`; shared types to `src/types.ts`; new `ChangeNotices.tsx` and `PrintChecklist.tsx`.
- **Docs:** guides moved to `docs/guides/`, with an index in `docs/README.md`. The root keeps README, CHANGELOG, SECURITY and LICENSE.
- Tests: 26 unit tests (8 new). Retrieval evaluation: 20 cases, Recall@4 14/14, abstention 6/6.

## 2026-11-10 — Phase 2: blocker fixes

- **Privacy filter (TD-01):** blocks identifiers and secrets only; questions describing a situation in Tamil or English are now answered, with a privacy reminder. The old behaviour that refused "I am a student…" was intentionally removed.
- **Retrieval relevance (TD-03):** EN/TA stop-words, prefix matching for Tamil suffixes and plurals, curated per-source keywords, an absolute score floor, and a relative cut-off. Off-topic questions now return no sources. The evaluation grew from 8 to 16 cases and fails CI on regression.
- **Default model (TD-02):** `gemini-3.5-flash-lite` (`gemini-2.5-flash` shuts down 1 Dec 2026).
- **Quota protection (TD-05):** per-client rate limit with `Retry-After`; 12 h in-memory answer cache. The frontend shows a bilingual "please wait" message on 429 and no longer lists unrelated sources on errors.
- Added the MIT `LICENSE` and GitHub Actions CI.
- Dropped the Namma Arasu hands-on benchmark and citizen interviews from the plan (developer decision).

## 2026-11-10 — Phase 0/1 re-audit (documentation only)

- Added `docs/audit/` (project audit, existing-system analysis, technical-debt register TD-01…TD-17, environment requirements, development safety).
- Refreshed Phase 1 research: Namma Arasu, the myScheme chatbot, Kisan e-Mitra, Jugalbandi and Haqdarshak added to the competitor analysis; differentiation re-ranked; post-2026 scheme renames and DPDP Rules timeline noted.
- Added `docs/research/FREE_TIER_AUDIT.md`.
- No application code changed. Known blockers (privacy over-blocking, no retrieval threshold, deprecated default model) are recorded but not yet fixed.

## 2026-11-09 — Initial implementation milestone

- Audited official government discovery sources and documented source freshness/access conditions.
- Added Phase 3 product requirements and architecture blueprint.
- Added a bilingual React interface and a FastAPI server with a hand-curated, directory-only source corpus.
- Added a bilingual catalog for two higher-education directory leads; eligibility remains disabled until current rules receive human verification.
- Added an unapplied PostgreSQL schema proposal, deployment/production readiness guidance, incident and recovery procedures, and a consent-based pilot/impact measurement plan.
- Added an optional, token-gated read-only maintainer overview for source review status and coarse provider health.
- Added lexical retrieval, optional Gemini embedding retrieval, Gemini structured generation, citation allowlisting, API-key health/failover handling, and safe fallback behavior.
- Added privacy warnings, identifier-pattern blocking, local request budgets, setup/security/testing documentation, and a small offline retrieval evaluation.
- No citizen interviews, current scheme-rule approval, automated ingestion, production database, public deployment, or production Gemini credentials are included.
