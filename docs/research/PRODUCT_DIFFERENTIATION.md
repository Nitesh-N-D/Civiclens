# Product differentiation hypotheses

**Status:** Unvalidated proposals from Phase 1 desk research
**Research date:** 9 November 2026

myScheme and UMANG already provide scheme discovery and public-service aggregation. Differentiation must show useful improvements in citizen understanding and safe navigation, not simply add a chat box.

| Proposed difference | Citizen value hypothesis | Feasibility | Novelty assessment | Priority |
|---|---|---|---|---|
| Evidence tied to each eligibility condition, with original official source and checked date | Helps a person verify why a condition was summarized and judge freshness | Medium: requires curated source passages and review | Not established as novel; make quality measurable | 1 |
| Plain Tamil and English explanations, including mixed-language questions | Reduces language and terminology friction for target Tamil Nadu journeys | Medium: language quality and administrative terms need human review | Strong local product focus, not a claim of technical uniqueness | 1 |
| Clear “possible match,” “does not appear to match,” and “cannot determine” outcomes | Reduces false certainty and highlights missing evidence | Medium: eligibility rules need structured, tested representation | Trust behavior is differentiating if consistently implemented | 1 |
| Action checklist connected to the official application or assisted channel | Converts reading into a realistic next step | Medium: source pages and document requirements can change | Useful workflow integration; validate against e-Sevai/department routes | 1 |
| Freshness status, change history, and contradiction escalation | Makes maintenance visible instead of implying live official status | Medium/high operational cost; depends on a review process | Potential product advantage if maintained reliably | 2 |
| Cross-scheme comparison | Helps users compare conditions and benefits across a narrow set | Medium: normalize dissimilar rules and prevent misleading comparisons | Not independently novel | 2 |
| Voice, broad personalization, automated application submission | Could help some users, but introduces privacy, usability, and operational risk | High | No evidence yet that these are MVP needs | Defer |

## Revision, 10 November 2026: the competitive landscape changed

The Government of Tamil Nadu's **Namma Arasu** WhatsApp chatbot (Jan 2026) already offers Tamil/English conversational access to scheme lookup and eligibility checks, plus transactions CivicLens will never do. **Kisan e-Mitra** covers PM-KISAN in Tamil. See [Competitor analysis](COMPETITOR_ANALYSIS.md). As a result:

- "Tamil conversational access" is no longer a differentiator by itself. It is **table stakes**.
- The remaining hypotheses, ranked by how hard they are for an official chatbot to copy:
  1. **Evidence transparency:** every condition shows the source passage, owning department, and last-checked date. An official channel has little incentive to show "this summary may be stale".
  2. **Change awareness:** the 2026 change of government renamed several schemes. A citizen holding an old name, an old amount, or an old screenshot needs "this scheme is now called X; here is what changed and the GO". This is concrete and timely, and the official bots focus on current state, not reconciling history.
  3. **Central + state in one explanation**, with comparison: "these 3 schemes may apply; here is how they differ".
  4. **Helper-mode for e-Sevai operators and NGO volunteers:** shareable, printable, cited checklists. Haqdarshak shows assisted access is where outcomes happen.
- **Kill criterion** (hands-on testing dropped, developer decision, 10 Nov 2026; re-check Namma Arasu's published feature list at each milestone): if Namma Arasu already gives cited, dated, condition-level explanations, CivicLens should narrow to helper-mode and change tracking, or stop. It should not be built as a duplicate.

## Differentiation principle

The core promise should be: **understand a potential public-service route, see the evidence and uncertainty, and take the official next step.** CivicLens is an independent information aid, not a government office and not an eligibility decision-maker.

## Validation measures

- Correctly understood conditions against a reviewed answer key.
- Proportion of factual statements with a supporting source passage.
- User ability to identify the responsible official portal and application route.
- Tamil and English task completion and comprehension.
- Time and errors versus the participant's current method and official alternatives.
- Correct abstention when authoritative sources conflict or are missing.
- Perceived trust and understanding that the output is informational only.

Run these comparisons with real users before claiming superiority or uniqueness.
