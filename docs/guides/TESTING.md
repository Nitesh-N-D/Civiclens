# Testing and evaluation

## Automated checks

From `frontend/`:

```powershell
npm.cmd run lint
npm.cmd test
npm.cmd run build
```

Frontend tests (Vitest, jsdom, Testing Library) mock `fetch` and cover: language switching, asking a question and showing its citation, session history, the rate-limit and API-down fallbacks, the theme toggle, scheme search and category filters, the print checklist, and maintainer sign-in (the password goes only to Supabase, the token only as a bearer header, nothing in `localStorage`, reviewers can record a check, viewers cannot).

From `backend/`:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Backend tests cover lexical retrieval, unknown queries, privacy filtering before API use, search-only fallback, citation allowlisting, uncited response abstention, and provider quota fallback. They do not call Gemini or use a live key.

## Manual local API smoke check

With Uvicorn running on loopback, confirm:

- `GET /api/health` returns `status: ok` and no secrets.
- `GET /api/sources` returns the curated public source list.
- `GET /api/schemes?language=ta` returns Tamil catalog cards marked unverified, with eligibility screening enabled.
- `POST /api/eligibility` with `{"profile": {"state": "tamil_nadu", "gender": "female", "school_type": "tn_government", "education": "undergraduate"}}` returns `requires_official_verification` for Pudhumai Penn, never `appears_eligible`.
- `GET /api/changes?language=ta` returns Tamil change notices; each `reported` one says it is a news report.
- Ask "Magalir Urimai Thogai": no sources, one notice labelled as a news report. Ask about old-age pension, then use **Print checklist** and check the print preview shows only the checklist.
- With no `CIVICLENS_ADMIN_TOKEN` and no Supabase sign-in, `GET /api/admin/overview` returns 404; with the local token it returns a viewer-only summary without keys, and `POST /api/admin/sources/{id}/checks` returns 403.
- `POST /api/ask` with a general Pudhumai Penn question returns source-search mode without keys.
- An identifier-like question returns the privacy message without citations and without a provider call.
- A situational question ("I am a student, what scholarships can I get?") returns relevant sources plus a privacy reminder.
- An off-topic question ("what is the weather in Chennai") returns no sources.
- More than 5 questions a minute from one client returns `429` with `Retry-After`.

CI (`.github/workflows/ci.yml`) runs ruff, the backend tests, the retrieval evaluation (which fails on any regression), ESLint, the frontend tests, the frontend build, and `npm audit` on every push to `main` and every pull request.
- A wrong/absent key returns a safe fallback, not a stack trace or key value.

## RAG evaluation

From `backend/`:

```powershell
$env:PYTHONIOENCODING="utf-8"
.\.venv\Scripts\python.exe evaluation\evaluate_retrieval.py        # 28 cases, no Gemini calls (runs in CI)
.\.venv\Scripts\python.exe evaluation\evaluate_answers.py          # full answer pipeline, search mode
.\.venv\Scripts\python.exe evaluation\evaluate_answers.py --live 8 # up to 8 paced Gemini calls; writes answer_review.md
```

Use `--live` sparingly, because both keys share one free-tier quota. Results, the dataset and coverage are in [`docs/evaluation`](../evaluation/). Answers in `answer_review.md` need a person to review them before anyone relies on them. Don't report "zero hallucinations" from citation or gate checks alone.

Coverage: `coverage run --source=app -m unittest discover -s tests` and `coverage report` from `backend/`, or `npm.cmd run coverage` from `frontend/`.
