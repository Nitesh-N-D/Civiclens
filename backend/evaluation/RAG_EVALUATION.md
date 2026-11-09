# CivicLens retrieval evaluation — initial offline baseline

**Date:** 9 November 2026
**Run:** `python evaluation/evaluate_retrieval.py` from `backend/`
**Corpus:** Four hand-authored public-source discovery summaries
**Model/API calls:** None

## Results

| Measure | Result |
|---|---:|
| Relevant-source Recall@4 | 7/7 (1.000) |
| Mean Reciprocal Rank | 1.000 |
| Top-1 source accuracy | 7/7 (1.000) |
| Out-of-scope abstention accuracy | 1/1 (1.000) |

All seven expected-source queries ranked the expected record first. The one synthetic astronomy query returned no record. Case-level output is printed by the evaluator.

## Interpretation and limits

This is a smoke baseline for the lexical retriever, not a RAG quality claim. The cases are synthetic and closely match the four curated records; there are only seven in-scope questions and one out-of-scope question. No citizens, native Tamil reviewers, production data, or Gemini-generated answers were involved. The metrics do not measure correctness, source authority, claim-to-passage entailment, Tamil natural-language coverage, eligibility accuracy, or hallucination rate.

The current retriever can optionally combine BM25-style lexical scores with Gemini embeddings when configured. This run had no Gemini keys, so the dense branch was not exercised. Before a pilot, expand the bilingual evaluation set with independently authored paraphrases, hard negatives, conflicting/stale sources, and a reviewed gold citation for each factual claim; assess with Tamil reviewers and hold out questions from retrieval tuning.
