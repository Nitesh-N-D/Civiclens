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
- `GET /api/schemes?language=ta` returns Tamil catalog cards with eligibility disabled and marked unverified.
- `GET /api/changes?language=ta` returns Tamil change notices; each `reported` one says it is a news report.
- Ask "Magalir Urimai Thogai": no sources, one notice labelled as a news report. Ask about old-age pension, then use **Print checklist** and check the print preview shows only the checklist.
- With no `CIVICLENS_ADMIN_TOKEN`, `GET /api/admin/overview` returns 404; with a valid local bearer token it returns a read-only summary without keys.
- `POST /api/ask` with a general Pudhumai Penn question returns source-search mode without keys.
- An identifier-like question returns the privacy message without citations and without a provider call.
- A situational question ("I am a student, what scholarships can I get?") returns relevant sources plus a privacy reminder.
- An off-topic question ("what is the weather in Chennai") returns no sources.
- More than 5 questions a minute from one client returns `429` with `Retry-After`.

CI (`.github/workflows/ci.yml`) runs the backend tests, the retrieval evaluation (which fails on any regression), the frontend build, and `npm audit` on every push to `main` and every pull request.
- A wrong/absent key returns a safe fallback, not a stack trace or key value.

## RAG evaluation status

An initial offline lexical retrieval baseline is recorded in [`backend/evaluation/RAG_EVALUATION.md`](../../backend/evaluation/RAG_EVALUATION.md). It uses twenty synthetic cases (including six that must abstain, four first-person questions and three alternate-name or amount questions) over four hand-authored records and does not call Gemini. No generation-quality evaluation or citizen task study has been run. Current unit tests validate software safeguards only; they do not measure factual answer quality, bilingual comprehension, eligibility correctness, or claim entailment. Before enabling eligibility content, create a human-reviewed bilingual test set with source locators and gold citations, report answer correctness, citation precision/recall, unsupported-claim rate, abstention quality, and source freshness. Do not report zero hallucinations based solely on citation-ID checks.
