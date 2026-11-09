# CivicLens MVP product requirements

**Status:** Phase 3 baseline; derived from Phase 0–2 research
**Date:** 9 November 2026
**Initial geography:** Tamil Nadu only
**Initial languages:** Tamil and English

## Product statement

CivicLens helps a person understand a potentially relevant public service or scheme, inspect the official evidence behind the explanation, and find the correct official or assisted next step. It is an independent information tool, not a government service, eligibility authority, or application processor.

## Users and problems

Primary users are Tamil-speaking residents seeking public information; initial research personas include students, farmers, older adults/caregivers, women/families, small businesses, and community helpers. These profiles are unvalidated. Student assistance is the proposed first workflow because an initial pair of candidate programs has identifiable official discovery routes. Proceed only after the controlling information is confirmed.

## MVP goals

1. Answer a bounded set of Tamil Nadu public-service questions with evidence from a reviewed official corpus.
2. Show the source owner, relevant evidence and checked date for each material claim.
3. Be understandable in Tamil and English, including a graceful path for mixed-language input.
4. Explain uncertainty and decline to answer from unsupported or conflicting evidence.
5. Help people reach an official digital or assisted service route.
6. Avoid unnecessary personal data collection and do not retain chat history by default.

## Non-goals for initial release

- Official eligibility decisions, benefit approval guarantees, legal advice, or professional case management.
- Application submission, payments, government identity integrations, or accounts for citizens.
- Uploading, storing, or extracting personal documents.
- Whole-web crawling, nationwide coverage, or automated ingestion without source permission.
- Training or hosting a custom LLM; local large-scale embedding or inference.
- Voice, speech transcription, WhatsApp integration, or government-department integrations.
- Staff admin dashboard exposed publicly; early corrections use a controlled maintainer workflow.

## Core user stories and acceptance criteria

### Discover and ask

- As a citizen, I can ask in Tamil or English and receive a response in the selected language.
- Search results are limited to the selected jurisdiction and currently approved sources.
- The system indicates when it has insufficient or conflicting evidence and does not invent an answer.
- The interface warns users not to enter identity numbers, bank details, health/disability details, or private document content.

### Understand a program

- Each candidate result names the program, administering authority, geographical scope, and status date.
- Each stated condition, benefit, document, or step has a source link and passage/page locator.
- Eligibility wording uses “may fit” or “does not appear to fit”; only a government authority decides.
- Time-sensitive details display the last human verification date; a fetch timestamp alone is not represented as verification.

### Take the next step

- The user can open the official application/service page or see a relevant assisted route.
- A checklist includes only requirements supported by a current reviewed source; each item links to evidence.
- CivicLens does not claim to submit or save an application.

### Report a problem

- User can report stale/unclear content without providing personal information.
- Reports go to a maintainer review process; they do not update the public corpus automatically.

## Functional requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-01 | Provide a mobile-first accessible search/chat interface with Tamil/English choice. | P0 |
| FR-02 | Search only reviewed active source records; filter by state/category and maintain source provenance. | P0 |
| FR-03 | Retrieve lexical and semantic candidates from the curated corpus; return source-grounded answer claims and citations. | P0 |
| FR-04 | Validate that every returned citation refers to retrieved evidence; abstain when evidence score/coverage is insufficient. | P0 |
| FR-05 | Render official links, passage/page locator, owner, publication/effective dates if known, and last human verification date. | P0 |
| FR-06 | Handle Gemini quota/timeouts/provider failures with a clear unavailable response and retry guidance; never leak key or stack trace. | P0 |
| FR-07 | Do not persist user prompts or profiles by default; avoid collecting direct identifiers. | P0 |
| FR-08 | Provide curated deterministic eligibility questions only after rule review; mark output as preliminary, not official. | P1 |
| FR-09 | Provide sourced document/process checklist for reviewed schemes. | P1 |
| FR-10 | Capture anonymous content quality feedback with rate limits and no default free-text personal data. | P1 |
| FR-11 | Record source fetch, human review, version and retirement events for maintainers. | P1 |
| FR-12 | Support comparison of approved scheme fields when equivalent data exists. | P2 |

## Content approval lifecycle

`discovered → terms checked → fetched or manually entered → normalized → human verified → published → review due / contested → updated or retired`.

No generated text becomes source data. Changes to source content require a review event; material eligibility or benefit changes should expire the old public answer until reverified. Keep document hashes and recoverable prior versions, without retaining unnecessary full documents.

## Safety and privacy requirements

- Gemini API keys are server-side secrets and never sent to the browser.
- Free-tier use must not transmit personal, sensitive, confidential, or private user content. UI and request handling should minimize/stop such content and disclose the limitation.
- Prompts contain only public source excerpts and the user's non-sensitive general question after basic risk filtering. Do not log raw prompts or responses by default.
- Treat retrieved content as untrusted data, never as instructions. The system prompt and application enforce fixed scope and citation schema.
- Rate limit and cap request length, output tokens, retrieval count, and daily/weekly total. A public demo is disabled or serves search-only when cap reached.
- No production secrets, paid services, data sharing, or deployment without the separately required authorization under project safety policy.

## Quality measures

Before pilot, maintain a reviewed bilingual evaluation set with expected answer, gold citations, and abstention label. Track answer correctness, citation precision/recall, unsupported-claim rate, eligibility rule accuracy, Tamil comprehension, abstention quality, official route success, latency, provider error rate, and source freshness. Establish thresholds with human reviewers and user tasks before public launch; no evaluation results exist yet.

## MVP release gates

1. Phase 2 source terms and controlling current content checked for every enabled record.
2. Tamil review completed for user-facing facts.
3. Corpus records carry provenance and human review state.
4. Evaluation set meets agreed correctness/citation thresholds; fail-closed behavior works.
5. Privacy and secret handling reviewed; no real personal data used in testing.
6. Mobile accessibility and official navigation manually reviewed.

Until these gates are met, label the application a demonstration and keep scheme content limited to clearly marked sample records.
