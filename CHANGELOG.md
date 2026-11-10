# Changelog

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
