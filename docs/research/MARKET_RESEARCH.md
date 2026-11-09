# CivicLens market and feasibility research

**Status:** Phase 0–3 research and baseline blueprint
**Research date:** 9 November 2026
**Scope:** Tamil Nadu, India

## Repository audit (Phase 0)

The selected workspace resolves to `D:\CivicLens`. It contains `AGENTS.md` and `CLAUDE.md` only. There is no Git repository metadata (`git status` reports “not a git repository”), no source code, dependency manifest, tests, documentation set, application configuration, or existing product behavior to assess. There is therefore nothing to reuse or replace yet. The project-specific safety instructions in both files were read; they reinforce a Windows-only workspace boundary, lightweight local work, no local model training, no secrets in source control, and no deployment or paid-service action without approval.

## Opportunity and problem evidence

Government information spans scheme directories, state departments, service portals, government orders, and assisted access channels. The Government of India presents myScheme as a way to reduce the effort of searching across government sites and reading guidelines; its documented features include eligibility checks and scheme search. Tamil Nadu separately offers service discovery and e-Sevai-assisted routes. These facts establish an existing information-navigation task and a mature set of incumbents. They do **not** establish how often citizens fail, which group experiences the greatest harm, whether AI is preferred, or market demand for an independent product. See [Problem validation](PROBLEM_VALIDATION.md).

The most credible initial opportunity is narrower than “one portal for every government service”: help a Tamil-speaking citizen understand a small, carefully maintained set of official program rules, see why a candidate may or may not apply, and reach the correct official or assisted channel. This is a product hypothesis to test against myScheme, department portals, and people’s existing helpers.

## Market framing

The product operates in a public-service access context rather than a proven commercial market. Do not publish TAM/SAM/SOM or monetization claims without a defined buyer, user research, and defensible data. Potential stakeholders to discover include citizens, colleges, community organizations, e-Sevai/CSC operators, and departments, but no partnership, procurement path, or willingness to pay has been established.

Tamil is a justified first language: Census 2011 reported Tamil as mother tongue for 88.37% of Tamil Nadu's population. The statistic is dated and cannot establish current preference. TRAI's March 2025 national internet subscriber tele-density was 45.03 per 100 rural population and 110.79 per 100 urban population; this motivates mobile/low-bandwidth and assisted-path considerations but is not a count of unique people or a Tamil Nadu figure. Cite these limits whenever using the data.

## Competitor landscape

The direct and adjacent alternatives are myScheme, UMANG, Tamil Nadu e-Sevai and department portals, National Government Services Portal, India.gov.in, DigiLocker, and in-person e-Sevai/CSC/community assistance. Existing public platforms already provide aggregation, discovery, service routing, and official transactions. CivicLens must demonstrate added value in comprehension, evidence-level citations, Tamil-English handling, transparent freshness, or comparison. A private competitor and AI-assistant landscape scan remains incomplete; absence from this limited search is not proof of uniqueness. Details: [Competitor analysis](COMPETITOR_ANALYSIS.md).

## Personas and validation

Provisional interview profiles: students, farmers/agricultural households, older adults/caregivers, women/families seeking welfare, small-business owners, and community helpers. These are sampling hypotheses only. No direct user research has taken place. Conduct 10–20 interviews, observe real tasks with public/sample data, and assess comprehension, source trust, completion time, Tamil usability, and when a person needs offline help before treating any persona as confirmed. Details: [User personas](USER_PERSONAS.md) and [Problem validation](PROBLEM_VALIDATION.md).

## Government source inventory

The first source set should include myScheme, Tamil Nadu department pages and notices, e-Sevai/TNeGA, the Tamil Nadu Gazette and government orders, TN Open Government Data, India.gov.in/NGSP, and relevant central ministry portals. The initial inventory identifies discovery starting points, not permission to scrape or guaranteed API access. Validate each specific source's authority, language, accessibility, reuse terms, and update path before ingestion. Details: [Source inventory](SOURCE_INVENTORY.md).

## Proposed MVP (hypothesis)

Start with a small, bounded set of high-value Tamil Nadu scheme/service journeys chosen after interviews. The MVP should include:

1. Tamil and English search/questions, including graceful handling of mixed input.
2. Curated records with scheme owner, geography, canonical URL, source document, effective/verification date, and review status.
3. Plain-language answers grounded only in approved source passages, with direct links and “not found/needs confirmation” behavior.
4. Deterministic eligibility questions for the subset of rules that can be represented unambiguously; explicitly label “possible match,” not official determination.
5. A practical document/next-step checklist with per-item evidence and a link to the official application or assisted route.
6. Feedback for incorrect, stale, or unclear content; an internal source review process before publishing corrections.

Defer unrestricted nationwide crawling, autonomous eligibility decisions, document uploads, storing sensitive profiles, voice, automated application submission, and broad scheme coverage until there is user evidence, governance, and a sustainable source review process.

## Differentiation hypothesis

Compete on trust and actionability, not “AI” or a larger scheme count: readable Tamil explanations; citations tied to concrete conditions; visible dates and source ownership; explicit conflicts/unknowns; and a verified next step that includes assisted service routes. Score and rationale: [Product differentiation](PRODUCT_DIFFERENTIATION.md).

## Initial technology direction

Keep this provisional until Phase 2–3 architecture work. A modest web application with a TypeScript/React client, a small Python API, PostgreSQL for curated source records and review metadata, and a server-side Gemini adapter is a plausible Windows-friendly starting point. Retrieval can begin with full-text search plus curated metadata and add vector retrieval only if evaluation shows a benefit. Avoid a separate vector database, multi-agent design, local model weights, and a large orchestration framework until needed. Use a data-ingestion/review workflow that keeps provenance and human approval explicit.

All Gemini use must remain server-side. The Gemini API is explicitly the requested runtime provider, but unpaid API terms allow submitted content and responses to be used to improve Google products and may involve human review; terms instruct developers not to submit sensitive, confidential, or personal information to unpaid services. Therefore a free-tier-only prototype must use public government documents and synthetic/non-sensitive test questions, never citizen profile details. Two API keys do not imply two independent quotas: Gemini limits are applied per project and limits vary by model/account. Treat the secondary key as a failover credential only where account/project boundaries and terms support that, never as a quota multiplication scheme. [Gemini terms](https://ai.google.dev/gemini-api/terms), [rate limits](https://ai.google.dev/gemini-api/docs/rate-limits), [pricing](https://ai.google.dev/gemini-api/docs/pricing).

## Free-tier feasibility

**Prototype: plausible, with hard limits. Production: not yet established as sustainably free.**

- Gemini currently offers free API access for eligible models, but quota is model- and account-dependent, and rate limits are not guaranteed. Unpaid terms are incompatible with sensitive personal questions unless the product prevents their submission. Do not put the free API behind an unrestricted public endpoint.
- Free hosting and database plans have quotas and can change. Supabase documents free-project, storage/database, and egress allowances; Vercel Hobby is limited to personal/non-commercial use in its terms. A public-interest or commercial production launch cannot assume Hobby is eligible. Verify terms at the deployment milestone and model costs for backups, domains, email, monitoring, and traffic as well as API tokens.
- No paid plan, billing activation, cloud project, account, API key, or service integration was created in this research phase.
- No honest monthly production-cost estimate is possible without chosen providers, request volumes, retention, source ingestion cadence, and support requirements. Free-tier ceilings can mean degraded availability, paused service, or a forced upgrade.

Sources: [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing), [Gemini API terms](https://ai.google.dev/gemini-api/terms), [Gemini rate limits](https://ai.google.dev/gemini-api/docs/rate-limits), [Supabase plans and billing](https://supabase.com/docs/guides/platform/billing-on-supabase), [Vercel Hobby plan](https://vercel.com/docs/plans/hobby), [Vercel terms](https://vercel.com/legal/terms).

## Hardware safety

The proposed initial scope fits ordinary source editing and lightweight development on the specified Windows laptop. Keep datasets small and curated; no model training or large-scale embeddings on-device; no unnecessary containers or local databases; no model weights. Do not install packages or start services during this research stage. If a later phase proposes heavier work, estimate resource use first and follow the project's Kaggle-only policy for computationally intensive ML experiments.

## Major risks

1. **Incorrect or stale guidance:** scheme rules change; mitigate with source lineage, dates, review, and abstention.
2. **False eligibility assurance:** explanations may be mistaken for official determinations; use cautious language and official handoff.
3. **Free-tier privacy:** unpaid Gemini content may be reviewed/used to improve services; do not send personal/sensitive inputs.
4. **Quota and availability:** limits vary and keys do not give a dependable quota pool; enforce server-side caps, retries, and graceful degradation.
5. **Source rights and access:** public webpages are not automatically reusable or scrapeable; verify terms, robots policy, and APIs per source.
6. **Language accuracy:** Tamil translation can distort legal/administrative conditions; review high-impact content with fluent humans.
7. **Inclusion and trust:** a chatbot may not fit low-literacy users or those without devices; preserve assisted and offline routes.
8. **Existing alternatives:** myScheme/UMANG already offer discovery; incremental product value must be demonstrated.
9. **Sustainability:** “free” services can pause, change quotas, restrict non-commercial use, or require paid plans.
10. **No repository history:** this folder is not presently a Git repository, so current history and branch state cannot be inspected. No Git initialization was performed.

## Recommended roadmap and gate

**Phase 0 (completed):** workspace and instruction audit.
**Phase 1 (completed as desk research only):** problem/competitor scan, hypotheses, MVP direction, feasibility and risk notes. Direct citizen validation remains open.
**Phase 2 (completed as a bounded desk audit):** a preliminary source audit and pilot corpus recommendation are in [Phase 2 source audit](PHASE2_SOURCE_AUDIT.md). Terms/reuse permissions, controlling current orders, and live application status remain unverified; no automated ingestion or eligibility publishing is authorized by this research.
**Phase 3 (baseline complete):** initial user requirements and architecture are in [Product requirements](PRODUCT_REQUIREMENTS.md) and [Architecture blueprint](ARCHITECTURE_BLUEPRINT.md). The initial implementation may proceed as a clearly labeled demonstration using only reviewed, non-sensitive sample content. Current source rules must be human-verified before represented as live authoritative guidance. Paid resources and public deployment remain subject to the project safety policy.

### Implementation progress update — 9 November 2026

The repository now has a bilingual Tamil-default web client, a local FastAPI source/ask/catalog API, four discovery-only source summaries, two scheme catalog entries, Gemini key configuration and optional hybrid retrieval, citation allowlisting, privacy filtering, and an offline lexical retrieval check. Eligibility matching is deliberately disabled for both catalog entries because current controlling orders and route status have not been verified. Document checklists, scheme comparison, automated source monitoring, editable admin/content management, production database integration, and public hosting remain outstanding. See the root README and changelog for the current build state.

## Research documents

- [Problem validation](PROBLEM_VALIDATION.md)
- [Competitor analysis](COMPETITOR_ANALYSIS.md)
- [User personas](USER_PERSONAS.md)
- [Product differentiation](PRODUCT_DIFFERENTIATION.md)
- [MVP priorities](MVP_FEATURE_PRIORITIES.md)
- [Official source inventory](SOURCE_INVENTORY.md)
