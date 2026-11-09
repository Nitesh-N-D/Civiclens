# Phase 2: official source audit and pilot corpus

**Review date:** 9 November 2026
**Scope:** Tamil Nadu-first discovery; public web pages only
**Status:** Desk audit complete; no content copied into an application database

## Decision

Start with a **small, manually reviewed, student-assistance pilot**, using the Tamil Nadu Pudhumai Penn scheme as the first candidate journey and Tamil Nadu Free Education Scheme as a second candidate. Add a social-security pension journey only after the responsible department and current controlling rules are resolved. This limits early scope and gives the team a way to compare a positive scheme description, a current official route, and source disagreement without presenting a legal/benefit determination.

This is a source-selection decision, not a claim that eligibility content is ready to publish. Scheme terms and required documents need source-by-source human reconciliation before being represented as current answers.

## Audited discovery sources

| Source ID | Issuer / authority | Current discovery reference | Content observed | Access / update conclusion | Use in pilot |
|---|---|---|---|---|---|
| MS-PUDHUMAI | myScheme, Government of India / NeGD | [Pudhumai Penn](https://www.myscheme.gov.in/schemes/pudhumai-penn-scheme) | Scheme description, benefit, eligibility and FAQ; official application route is identified as Penkalvi. Page was indexed/crawled recently in this research. | Public page. No public bulk/API access or scraping permission was verified. Dynamic content; preserve page checked date and direct link. Treat as a discovery/summary source, not a substitute for a current Tamil Nadu order. | Candidate for display only after comparison with controlling TN source and portal. |
| MS-FREE-EDU | myScheme, Government of India / NeGD | [Free Education Scheme](https://www.myscheme.gov.in/schemes/fes) | Summary states target communities, eligible colleges/courses and fee assistance. | Public page; its stated 2012 launch does not prove current terms. No API or reuse terms verified. | Candidate second education record; verify all current criteria with BC/MBC/DNC Welfare department. |
| CRA-SOCIAL | Commissionerate of Revenue Administration and Disaster Management, Government of Tamil Nadu | [Tamil social-security schemes](https://cra.tn.gov.in/about_schemes_t.php) | Tamil-language overview of state and centrally supported social-security pension schemes, eligibility summaries and amounts. Page refers to 2024–25 budget context. | Government department source, but page's referenced period shows that apparently detailed data can still be stale. No machine API or formal update cadence verified. | Useful cross-check; do not publish amounts/criteria as current without newer controlling order or direct confirmation. |
| TNES-SERVICES | Tamil Nadu e-Sevai / TNeGA | [Service list](https://www.tnesevai.tn.gov.in/Pages/ServiceList.aspx) | Large public HTML service list; examples include pension, certificate and other application routes and document lists. Includes a Tamil Pudhumai item under services in current indexed content. | Public HTML table; no public API, automated reuse permission, or update SLA verified. Source contains typos/inconsistent spellings and lists highly sensitive document types. A service checklist is not proof of scheme eligibility. | Service routing and evidence of available process only. Do not relay sensitive document lists without a clear necessity and explicit official citation. |
| PENKALVI | Tamil Nadu Social Welfare and Women Empowerment Department's Pudhumai Penn portal | [Penkalvi](https://penkalvi.tn.gov.in/index.php) | myScheme names this as official application portal. A 2023 state PDF says registrations were closed at that time. | Portal is an authoritative route, but current user-facing terms and intake status were not independently confirmed in this audit. Do not infer open/closed status from old PDF or failed/timeout page fetch. | Handoff link only; check route before every publication. |
| UMIS | Government of Tamil Nadu, Higher Education Department / University Management Information System | [UMIS](https://umis.tn.gov.in/) | Official site search result showed college-nodal-officer attendance verification for Pudhumai Penn and Tamil Pudhalvan for Q1 Jan–Mar 2026. | Current role-specific workflow exists, but page fetch timed out during review; not a citizen-facing authority for all eligibility terms. | Possible corroboration with department; not the primary citizen application link. |
| TN-IT-GO | Information Technology and Digital Services Department, Tamil Nadu | [Government Orders](https://it.tn.gov.in/en/government_order) | Order index grouped by year. | Official source, but this department index is not comprehensive for social welfare/education. Search department-specific GOs and Gazette notices for controlling material. | Order discovery, not sole corpus. |
| TN-GAZETTE | Stationery and Printing Department, Tamil Nadu | [Gazette archive](https://stationeryprinting.tn.gov.in/gazette.php) | Current and archived Gazette issue listings. | Official statutory publication source. Need identify issue/document, legal status, amendments, and reuse rights per item. | Preferred authority for formal notification where applicable. |
| TN-OGD | OGD Platform Tamil Nadu / NIC | [Portal overview](https://tn.data.gov.in/about), [API listings](https://tn.data.gov.in/apis) | Dataset and API directory. | APIs are listed, but no scheme eligibility API was identified. Terms, dataset-specific freshness, and API limits vary. | Useful only if a suitable official dataset is later verified; not a scheme-content backend by assumption. |

## Evidence chain for the first candidate

For Pudhumai Penn, the discovery evidence is currently:

1. myScheme describes the program and states a link to the official Penkalvi portal. [Scheme page](https://www.myscheme.gov.in/schemes/pudhumai-penn-scheme)
2. A Tamil Nadu government IT department information PDF, indexed in search, describes the scheme and reports registration closed in its publication context. [Tamil Nadu IT Department PDF](https://it.tn.gov.in/sites/default/files/2025-08/it_e_pn_2023_24.pdf)
3. UMIS indexed content shows a college nodal-officer verification workflow in 2026. [UMIS](https://umis.tn.gov.in/)

These references describe different views and time points. Before a citizen-facing eligibility answer or checklist is enabled, obtain the latest Social Welfare department order/guideline and verify the live Penkalvi route and current process. The app must not merge a discovery summary, old PDF, and role-specific UMIS workflow as if they were one current authoritative rule set.

## Source reliability and publication rule

1. Current Act/rule/Gazette notification or Government Order issued by the responsible authority.
2. Current detailed scheme guideline from the administering department.
3. Current official application portal/service instructions for application process and documents.
4. myScheme and other official directories for discovery, cross-check, and citizen navigation.
5. Official district pages as local help or route confirmation.

For each answer claim, save the exact source URL, passage/page locator, source owner, document identifier/date, retrieved date, human reviewer and decision. If rule and portal disagree or recency is uncertain, suppress the affected claim, explain that it needs official confirmation, and give the responsible department route. A URL alone is not sufficient evidence.

## Access and ingestion constraints

- No source's robots policy, terms, API conditions, or content-reuse license were checked exhaustively. Therefore this audit authorizes no bulk crawler or automated copying.
- Phase 2 pilot data entry should be manual and limited to content that can be reviewed by a person. Keep short factual summaries and source links; store only the minimum source excerpt necessary for attribution and verification.
- For a future fetcher, use a per-domain allowlist, low request rate, conditional requests where supported, size/time caps, a user-agent/contact policy, audit logs, and a stop switch. Do not fetch authenticated pages or bypass access controls.
- A fetch timestamp must not be called a verification timestamp. Human verification is a separate event.
- Do not scrape citizen data, application submissions, or identity documents. Do not ask users to upload Aadhaar, bank documents, certificates, or similar records.

## Registry status fields

`source_id`, `department`, `jurisdiction`, `canonical_url`, `source_type`, `language`, `access_method`, `access_terms_status`, `publication_date`, `effective_from`, `effective_to`, `document_number`, `last_fetch_at`, `last_human_verified_at`, `content_hash`, `reviewer`, `review_status`, `known_conflicts`, `next_review_due_at`, `backup_reference`, `failure_count`, and `notes`.

Current registry rows have `last_fetch_at = not fetched by CivicLens`; `last_human_verified_at = desk review only, 2026-11-09`; `access_terms_status = not verified`; `review_status = candidate / not approved for automated answers`.

## Research still required before enabling eligibility answers

- Latest controlling Pudhumai Penn scheme Government Order/guidelines, including amendments.
- Current Penkalvi application status, eligibility, document list, grievance/appeal path, and intake periods.
- Whether the latest rules allow all courses/categories described on myScheme and reconcile the first-course rule and bank account conditions.
- Current Free Education Scheme orders/guidelines and responsible department's application route.
- Official authorization/reuse terms and machine-readable access for all selected pages/PDFs.
- Fluent Tamil human review of all extracted eligibility and document text.
