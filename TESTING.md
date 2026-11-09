# Testing and evaluation

## Automated checks

From `frontend/`:

```powershell
npm.cmd run build
```

From `backend/`:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Backend tests cover lexical retrieval, unknown queries, privacy filtering before API use, search-only fallback, citation allowlisting, uncited response abstention, and provider quota fallback. They do not call Gemini or use a live key.

## Manual local API smoke check

With Uvicorn running on loopback, confirm:

- `GET /api/health` returns `status: ok` and no secrets.
- `GET /api/sources` returns the curated public source list.
- `POST /api/ask` with a general Pudhumai Penn question returns source-search mode without keys.
- An identifier-like question returns the privacy message without citations and without a provider call.
- A wrong/absent key returns a safe fallback, not a stack trace or key value.

## RAG evaluation status

An initial offline lexical retrieval baseline is recorded in [`backend/evaluation/RAG_EVALUATION.md`](backend/evaluation/RAG_EVALUATION.md). It uses eight synthetic cases over four hand-authored records and does not call Gemini. No generation-quality evaluation or citizen task study has been run. Current unit tests validate software safeguards only; they do not measure factual answer quality, bilingual comprehension, eligibility correctness, or claim entailment. Before enabling eligibility content, create a human-reviewed bilingual test set with source locators and gold citations, report answer correctness, citation precision/recall, unsupported-claim rate, abstention quality, and source freshness. Do not report zero hallucinations based solely on citation-ID checks.
