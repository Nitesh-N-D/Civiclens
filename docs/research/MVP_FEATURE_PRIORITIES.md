# MVP feature priorities

**Status:** Phase 1 proposal; requires user and source validation
**Research date:** 9 November 2026

Priorities use citizen value, trust risk, and feasibility as qualitative judgments. They are not measured scores.

| Priority | Feature | Why it belongs / acceptance idea | Gate or dependency |
|---|---|---|---|
| P0 (added 10 Nov 2026) | **Fix the blockers found in the Phase 0 audit** | Personal-context questions such as "நான் கல்லூரியில் படிக்கிறேன்…" must not be refused (TD-01); off-topic questions must abstain (TD-03); the default model must not be one that shuts down 1 Dec 2026 (TD-02). | [Technical debt](../audit/TECHNICAL_DEBT.md); model choice needs developer approval |
| ~~P0~~ Dropped | ~~Competitive benchmark against Namma Arasu~~ | Out of scope (developer decision, 10 Nov 2026). Differentiation rests on features official bots publicly lack: per-condition evidence, dates, and rename history. | — |
| P0 (added 10 Nov 2026) | **Post-2026 freshness re-check** of every corpus record | Each record either cites a current GO/department page or is withdrawn; renamed schemes carry their old names as aliases. | Phase 2 |
| P0 | Narrow, Tamil Nadu-only curated source set | Keep review work bounded; every record has official owner, canonical URL, effective date when available, checked date, and review status. | Phase 2 must confirm candidate sources and reuse/access conditions. |
| P0 | Tamil and English question/search | Core inclusion need; accept a small validated task set in both languages and disclose unsupported language cases. | Fluent Tamil review and user interviews. |
| P0 | Evidence-backed plain-language response | Claims link to source passages; answer says when evidence is missing or conflicting. | Build a reviewed question/answer evaluation set before implementation. |
| P0 | Official next-step links | Each result distinguishes information from application and points to the official digital or assisted route. | Validate every link and route. |
| P1 | Structured eligibility helper for a few schemes | Ask only necessary questions and show condition-by-condition reasoning; never assert official approval. | Rules reviewed by a knowledgeable human; privacy design approved. |
| P1 | Document and process checklist | Show only requirements supported by current official evidence, with a citation per item. | Verify document rules and application paths. |
| P1 | Feedback and content-review queue | Let users report stale/unclear answers; human review controls publication. | Define owner, response expectations, and secure operations. |
| P1 (promoted 10 Nov 2026) | **Scheme change tracking with old-name aliases** | "Is X still running? What is it called now?" answered with the GO and its date. This is the most defensible differentiator after Namma Arasu. | Source registry + versioning (Phase 2/6) |
| P1 (added 10 Nov 2026) | **Helper mode**: printable, shareable cited checklist | Serves e-Sevai operators and NGO volunteers, who drive assisted outcomes. | Interviews with 2–3 helpers |
| P2 | Scheme comparison | Compare a few normalized fields with source links and caveats. | User research must show value and source data can be normalized safely. |
| Defer | Citizen account, saved profile, document uploads, automated application, nationwide coverage, unrestricted web crawling | Adds privacy, regulatory, data quality, and support burden before product value is demonstrated. | Revisit only with explicit user evidence, policy, and operational controls. |

## MVP success criteria to define after discovery

Citizen interviews are out of scope (developer decision, 10 Nov 2026); set thresholds from the offline evaluation set instead and revisit if real users are recruited later. Measure factual correctness, citation support, successful route-to-official-source, language comprehension, abstention quality, task time, and user trust. Do not use usage volume alone as evidence of public benefit.
