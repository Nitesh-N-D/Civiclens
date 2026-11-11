# RAG evaluation report

**Date:** 11 Nov 2026 · **Corpus:** 4 discovery summaries (none human-verified as current rules) · **Dataset:** [28 cases](EVALUATION_DATASET.md)

Every number below came from a real run of the scripts named. None was estimated.

## 1. Retrieval (`python evaluation/evaluate_retrieval.py`, no Gemini calls, runs in CI)

| Slice | Cases | Recall@4 | Recall@1 | MRR | Precision@4 | Abstention |
|---|---:|---:|---:|---:|---:|---:|
| All | 28 | 20/20 | 1.000 | 1.000 | 0.263 | 8/8 |
| English | 19 | 12/12 | 1.000 | 1.000 | 0.271 | 7/7 |
| Tamil | 6 | 5/5 | 1.000 | 1.000 | 0.250 | 1/1 |
| Mixed | 3 | 3/3 | 1.000 | 1.000 | 0.250 | — |

- Median retrieval latency is 0.5 ms and the maximum is 1.4 ms (in process, lexical only).
- Precision@4 is low by construction: each case has one relevant source, and related sources are also returned (for example both education schemes for "scholarship"). It is not a quality signal.
- Change made during this phase: a short query whose every word matches one source's curated keywords is no longer abstained. "scholarship" alone used to score below the floor in a four-document corpus. "cricket" and "scholarship cricket" still abstain, and unit tests check both.
- The CI run is lexical only. The Gemini embedding branch (`ENABLE_EMBEDDINGS=true`, vectors stored in pgvector) hasn't been evaluated against this set, and `MIN_SEMANTIC_SCORE = 0.75` is still uncalibrated.

## 2. End-to-end answers (`python evaluation/evaluate_answers.py`)

The script runs the real `answer_question` pipeline. That pipeline covers the privacy filter, retrieval, Gemini, citation-ID checks, the claim–evidence gate and the search fallback.

| Measure | Search mode (0 Gemini calls) | Live (`--live 8`, 8 Gemini calls) |
|---|---:|---:|
| In-scope cases | 20 | 20 (8 answered by AI) |
| Citation precision (cited sources that are the expected one) | 0.808 | 0.840 |
| Citation coverage (expected source cited) | 1.000 | 1.000 (AI answers 8/8) |
| Claims generated / rejected by the gate | — | 23 / 0 |
| Out-of-scope abstention | 8/8 | 8/8 |
| Maximum AI answer latency | — | 3,357 ms |
| Provider state after the run | HEALTHY | HEALTHY |

- The live run was paced at one call every 13 seconds, using `gemini-3.5-flash-lite` on the free tier. Only 8 of the 20 in-scope cases were sent, to conserve the shared daily quota. The other 12 were answered in search mode.
- A zero gate-rejection rate on 23 claims doesn't prove there were no hallucinations. The gate is a heuristic (numbers and content words must appear in the cited source), not an entailment check.

## 3. Answer review

The 8 AI answers are in [`backend/evaluation/answer_review.md`](../../backend/evaluation/answer_review.md), with checkboxes for a reviewer.

**Status: no human review yet.** The development agent read all 8 against their cited source text. In that pre-review:

- Every claim it checked appeared in, or was a close paraphrase of, the cited summary.
- No amount, date or condition was invented.
- Each answer told the reader to confirm with the responsible department.
- The e-Sevai documents answer is only partial: the source lists no documents, and the answer correctly doesn't make any up.

This agent check doesn't replace review by a person, ideally a native Tamil speaker for the 4 Tamil answers. The boxes in the review file stay unticked until that review is done.

## 4. Not measured

- Factual correctness against current Government Orders. The sources themselves aren't verified as current.
- Tamil fluency and comprehension with real users.
- Eligibility correctness against real cases. The eligibility tests only prove that each condition is quoted from its source and that the decision logic is deterministic.
- Behaviour at a larger corpus size.
