# Evaluation dataset

**File:** [`backend/evaluation/retrieval_cases.json`](../../backend/evaluation/retrieval_cases.json) · **Cases:** 28 · **Last changed:** 11 Nov 2026

The cases were written by the development team against the four discovery summaries in the corpus. Nobody outside the team wrote them, and a native Tamil reviewer has not checked them. They are a regression set for retrieval and abstention. They do not measure citizen task success.

## Composition

| Group | Cases | What it checks |
|---|---:|---|
| English, in scope | 12 | Scheme names, portals, documents, first-person questions, alternate names (Puthumai, Moovalur), amounts, a wrong assumption ("Rs 50,000 to boys"), an ambiguous one-word query ("scholarship") |
| Tamil, in scope | 5 | Scheme names, fee help for Denotified Communities, old-age pension, a student question, the income certificate |
| Mixed Tamil–English, in scope | 3 | Code-mixed questions ("Pudhumai Penn scheme-க்கு எப்படி apply பண்றது?") |
| Must abstain | 8 | Off-topic (weather, bus timings, cricket, passport, astronomy), a scheme that isn't in the corpus (Magalir Urimai Thogai), and two prompt injections (English and Tamil) |

## Case format

```json
{ "id": "en-pudhumai", "question": "...", "expected_source": "myscheme-pudhumai-penn" }
```

- `expected_source: null` means the system must return no sources.
- `expected_any: [...]` is used for ambiguous questions; a hit on any listed source counts.
- The language is detected from the question's script: Tamil characters only means `ta`, Latin only means `en`, and both together means `mixed`. That puts the Tamil injection probe in the Tamil slice.

## Known gaps

- Each in-scope case has exactly one relevant source, so precision@4 is capped by design and is not a useful quality signal.
- There is no held-out split; some keywords in the corpus were tuned on these questions.
- There are no gold answers or claim-level citations yet. Answer quality is judged by human review (see [RAG evaluation report](RAG_EVALUATION_REPORT.md)).
- The set has no conflicting sources, no stale sources, and nothing from outside the four records' domains apart from the abstention probes.
