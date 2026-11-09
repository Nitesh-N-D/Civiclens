# Preliminary official source inventory

**Status:** Discovery shortlist plus Phase 2 source audit; not ingestion authorization
**Research date:** 9 November 2026

This inventory is a set of official starting points surfaced in Phase 0–1, with a bounded Phase 2 desk audit documented separately. No sources were crawled or ingested. No public API availability, scraping permission, reuse license, or update cadence is assumed. Verify the terms, robots policy, copyright/reuse conditions, and actual content format for each specific endpoint before automated access.

The bounded desk audit is now recorded in [PHASE2_SOURCE_AUDIT.md](PHASE2_SOURCE_AUDIT.md). No source has been approved for automated collection or unreviewed eligibility answers.

| ID | Source / owner | Jurisdiction and likely content | Public discovery URL | Access observations / next check |
|---|---|---|---|---|
| TN-ESVAI | Tamil Nadu e-Sevai / TNeGA | State citizen services, service process, center-assisted route | [tnesevai.tn.gov.in](https://www.tnesevai.tn.gov.in/NewIndex.html) | Public web pages; confirm current citizen-facing pages, service list, languages, and terms. The portal describes a center process; do not treat it as a general open API. |
| TN-DEG | Directorate of e-Governance, Tamil Nadu | Service categories and e-governance links | [deg.tn.gov.in/services.html](https://deg.tn.gov.in/services.html) | HTML discovery page; follow only official links and verify the destination owner. |
| TN-IT-GO | Information Technology and Digital Services Department | Department government orders | [it.tn.gov.in/en/government_order](https://it.tn.gov.in/en/government_order) | Orders listed by year; identify actual document URLs, effective status, amendments, language, and permissions. Not a complete state-wide order source. |
| TN-GAZETTE | Stationery and Printing Department, Tamil Nadu | Gazette notifications and statutory notices | [stationeryprinting.tn.gov.in/gazette.php](https://stationeryprinting.tn.gov.in/gazette.php) | Public Gazette archive; inspect file availability and terms and preserve issue/date identifiers. |
| TN-OGD | Open Government Data Platform, Tamil Nadu / NIC | Published datasets, documents, tools, APIs where offered | [tn.data.gov.in](https://tn.data.gov.in/) and [API directory](https://tn.data.gov.in/apis) | Portal has API listings, but this does not establish a scheme-content API. Check dataset-level metadata, license, last update, and API key/rate terms. |
| TN-MYSCHEME | National myScheme platform / NeGD and participating ministries/departments | Scheme discovery, eligibility, application guidance | [myscheme.gov.in](https://www.myscheme.gov.in/), [Tamil FAQ](https://www.myscheme.gov.in/ta/faqs) | Official discovery resource and closest comparator. Verify each scheme against the owning department's current notice. Do not assume bulk API/export or permission to crawl. |
| TN-DEPT | Relevant Tamil Nadu department and district administration pages | Department scheme rules, circulars, benefits, application route | [Chennai district social welfare index](https://chennai.nic.in/departments/social-welfare-sw/) (example directory) | District pages can be indexes and may be dated or localized. For any scheme, locate and record the actual administering department source and controlling order/guideline. |
| IN-INDIACODE | Legislative Department / NIC, Government of India | Central Acts, rules, notifications, orders and subordinate legislation | [India Code](https://www.indiacode.nic.in/indiacode/home.jsp) | Official legal reference; determine version, amendments, state applicability, and terms for any legal material used. |
| IN-NGSP | National Government Services Portal | Service directory across departments and jurisdictions | [services.india.gov.in](https://services.india.gov.in/) | Use as a discovery/index and official handoff. Verify at the originating department page. |
| IN-INDIAGOV | National Portal of India | Government information and service discovery | [india.gov.in](https://www.india.gov.in/) | Directory/discovery role; locate authoritative source owner for substantive eligibility content. |
| IN-UMANG | NeGD / UMANG | Aggregated government service discovery and access | [web.umang.gov.in](https://web.umang.gov.in/), [NeGD overview](https://negd.gov.in/our_projects/umang/) | Service route and comparator; do not assume a machine-readable public catalog API. |
| IN-DATA | Open Government Data Platform India / NIC | Central open datasets and listed APIs | [data.gov.in](https://data.gov.in/) | Check dataset-specific provenance, license, update dates, and API limits; datasets may be contextual rather than authoritative scheme rules. |

## Authority and use hierarchy (proposed)

1. Current Gazette notification, Government Order, Act/rule, or official scheme guideline from the responsible government authority.
2. Current official page/document from the administering ministry or Tamil Nadu department.
3. Official state/national scheme directory or service portal, used for discovery and cross-checking.
4. Official district, institution, or service-center instructions where the route is locally administered.
5. Secondary sources only as leads, never as sole evidence for eligibility or required documents.

Where sources disagree, preserve both references, identify the controlling authority/date, and route for human review instead of silently selecting one.

## Registry fields for Phase 2

Each approved record should capture source ID; title; department/owner; jurisdiction; canonical URL; document type; language; publication/effective date; version or order number; access method (manual, download, API, RSS, other); reuse/access terms; checked/fetched timestamps; content hash; last human verification; reviewer; current status; known conflicts; backup/recovery reference; and next review date. Store only necessary public source content and its provenance.

## Initial references

- [Tamil Nadu Directorate of e-Governance](https://deg.tn.gov.in/services.html)
- [Tamil Nadu e-Sevai](https://www.tnesevai.tn.gov.in/NewIndex.html)
- [Tamil Nadu Government Orders, IT Department](https://it.tn.gov.in/en/government_order)
- [Tamil Nadu Gazette](https://stationeryprinting.tn.gov.in/gazette.php)
- [Tamil Nadu Open Government Data](https://tn.data.gov.in/about)
- [myScheme](https://www.myscheme.gov.in/)
- [India Code](https://www.indiacode.nic.in/indiacode/home.jsp)
- [National Government Services Portal](https://services.india.gov.in/)
- [UMANG / NeGD](https://negd.gov.in/our_projects/umang/)
