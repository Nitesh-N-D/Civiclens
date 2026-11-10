# Problem validation: CivicLens

**Status:** Phase 0–1 desk research, not field validation
**Research date:** 9 November 2026
**Geography:** Tamil Nadu first

## Executive finding

There is a credible access and comprehension problem worth investigating further. Government platforms themselves describe fragmented discovery and the effort required to locate schemes and determine eligibility. Tamil Nadu already has a substantial digital service network, so CivicLens should complement those services by helping a person understand and navigate official information, not imply that it replaces application portals or assisted service centers.

This is institutional and desk-research evidence. No citizens have been interviewed or observed for this project. Frequency, severity, willingness to use an independent assistant, and the most valuable first user group remain unvalidated.

## Verified signals

| Signal | Evidence | What it supports | Limit |
|---|---|---|---|
| Scheme discovery is recognized as a user problem | The Government of India describes myScheme as reducing the time and effort involved in searching multiple sites and studying scheme guidelines. [Digital India: myScheme](https://www.digitalindia.gov.in/initiative/myscheme/) | There is a recognized need for consolidated discovery and eligibility guidance. | A government's product rationale is not independent evidence of user outcomes or unmet demand. |
| Scheme eligibility is a supported use case | myScheme describes eligibility checks, scheme finder filters, and scheme detail pages. [myScheme: About](https://myapp.umangapp.in/about) | Eligibility and guidance are practical information tasks, not speculative features. | It also establishes an existing solution to account for. |
| Tamil Nadu has multiple digital and assisted service routes | The state e-Sevai portal describes services and a center-based process; Tamil Nadu's Directorate of e-Governance lists citizen-service categories. [e-Sevai](https://www.tnesevai.tn.gov.in/NewIndex.html), [Directorate of e-Governance](https://deg.tn.gov.in/services.html) | Information discovery must connect users to official digital and assisted channels. | Portal descriptions do not measure service quality, reach, or barriers. Published service counts vary across sources and dates; do not treat them as current comparable counts. |
| Tamil language is central to the state context | Census 2011's language table records Tamil as the mother tongue of 63,753,997 people, or 88.37% of Tamil Nadu's population at that time. [Census of India, C-16 / Language Survey](https://censusindia.gov.in/nada/index.php/catalog/10222) | Tamil-first content and interaction deserve priority. | This is 2011 census data, not a current population estimate; mother tongue is not the same as preferred service language or literacy. |
| Internet access remains uneven by geography | TRAI reported March 2025 internet subscriber tele-density of 45.03 per 100 in rural India and 110.79 per 100 in urban India. [TRAI, Indian Telecom Services Performance Indicators](https://www.trai.gov.in/sites/default/files/2025-07/YIR_08072025_0.pdf) | Design should support mobile, low-bandwidth use and non-digital handoff. | Subscriber tele-density is not the share of unique people online; it is national context, not a Tamil Nadu estimate. |

### Signals added 10 November 2026

| Signal | Evidence | What it supports | Limit |
|---|---|---|---|
| The state itself invested in conversational Tamil access | TN launched the Namma Arasu WhatsApp chatbot (Jan 2026), including welfare-scheme lookup. [Elets eGov](https://egov.eletsonline.com/2026/01/tamil-nadu-launches-namma-arasu-whatsapp-chatbot-to-offer-50-government-services/) | The access problem is real enough for government to act on it | It also means part of the problem is already being addressed officially |
| Scheme information churns | After the 2026 election, the state budget renamed several existing schemes (e.g. *Kalaignar Magalir Urimai Thogai → Magalir Urimai Thittam*; *Naan Mudhalvan → Vetri Skill Training Scheme*), and new schemes were created by GO (e.g. *Annan Seer Thittam*, GO dated 5 Oct 2026, per secondary reporting). [The Federal](https://thefederal.com/category/states/south/tamil-nadu/tn-budget-welfare-schemes-rebranding-to-vetri-opposition-slams-tvk-252624) | Freshness and change-tracking are a live problem, not a hypothetical one | News sources, not GOs; each rename must be confirmed against the official order |
| Scale demand exists for scheme-specific AI help | Wadhwani AI reports Kisan e-Mitra resolved 3M+ queries since Feb 2024. [Wadhwani AI](https://www.wadhwaniai.org/impact/agriculture-solutions/kisan-e-mitra/) | Citizens will use an AI channel for scheme questions | Self-reported, single scheme, official channel |
| AI scheme bots carry misinformation risk | Jugalbandi coverage (2023) noted errors could mislead people about benefits. [MediaNama](https://www.medianama.com/2023/06/223-jugalbandi-chatbot-rural-india-what-to-know/) | Evidence-first answers and abstention are justified | Anecdotal; no measured error rate |

## Claims not yet validated

- Citizens routinely miss eligible schemes because information is hard to find.
- The primary pain is language, rather than awareness, eligibility rules, documentation, application friction, or trust.
- A conversational AI product is more useful or trusted than search, a public portal, an e-Sevai center, or a human helper.
- Tamil-English code-switching works reliably for the intended users and government vocabulary.
- A personalized checklist improves application completion.
- Users will trust a non-government product with sensitive eligibility details.

These claims need interviews and usability work. Avoid presenting them as measured facts or building personalization that collects sensitive attributes before need and safeguards are demonstrated.

## Proposed validation work (before a public pilot)

Conduct 10–20 voluntary, consent-based interviews with a varied group: students, farmers, older adults or caregivers, women seeking welfare information, job seekers, small businesses, and community-service volunteers. Recruit across rural/urban settings and levels of digital confidence. Do not collect identity numbers or copies of personal documents.

Ask participants to recount a recent real task: how they found the scheme or service, what they tried, where they got stuck, what source they trusted, what language they used, and whether they completed the task. Observe a task using public/sample information. Record failure points and outcomes, not unnecessary personal details.

Test whether users can, without prompting:

1. Find a potentially relevant service or scheme.
2. Explain why it might apply and what uncertainty remains.
3. Identify the official source and its date.
4. Identify the next step and distinguish information from application submission.

**Initial go/no-go question:** Does an official-source-backed explanation meaningfully reduce time or confusion compared with the participant's current method, while preserving trust and appropriate expectations? Set thresholds after the baseline interviews, not retroactively.

## Sources

- [myScheme FAQ](https://search.myscheme.gov.in/faqs)
- [myScheme overview, Digital India](https://www.digitalindia.gov.in/initiative/myscheme/)
- [Tamil Nadu e-Sevai portal](https://www.tnesevai.tn.gov.in/NewIndex.html)
- [Tamil Nadu Directorate of e-Governance services](https://deg.tn.gov.in/services.html)
- [Census of India: Tamil Nadu mother-tongue table](https://censusindia.gov.in/nada/index.php/catalog/10222)
- [TRAI telecom performance report, March 2025 data](https://www.trai.gov.in/sites/default/files/2025-07/YIR_08072025_0.pdf)
