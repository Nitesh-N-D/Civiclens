# Development guide

## Project layout

- `frontend/`: Vite, React and TypeScript client.
- `backend/app/`: FastAPI endpoints, Gemini adapter, public-source corpus, retrieval and response validation.
- `backend/tests/`: lightweight Python standard-library unit tests.
- `docs/research/`: phase research, source audit, product requirements, and architecture blueprint.

## Local workflow

1. Start the API bound to `127.0.0.1:8000` and the Vite client on `127.0.0.1:5173`.
2. Use generic, non-personal questions. The UI and API reject several common identifier/personal-detail patterns, but the filter is not exhaustive.
3. Keep source data changes in `backend/app/corpus.py`. Add an official source URL, source owner, locator, status caveat, and reviewed summaries in both languages.
4. Do not publish eligibility conditions or required documents until the responsible department's current controlling source has been reviewed and recorded.
5. Run the frontend build and backend unit tests before committing a change.
6. Keep `.env` files, virtual environments, node modules, and build output local; `.gitignore` excludes them.

## Source content changes

Use the review lifecycle in `docs/research/PRODUCT_REQUIREMENTS.md`. A maintainer must confirm the source owner, current document/version, effective date, passage, language, access/reuse conditions, and official user route. A crawl timestamp does not count as human verification. Do not copy source page content wholesale or bypass access controls.

## API conventions

- API routes are under `/api`.
- Response errors do not contain provider messages, credentials, or tracebacks.
- `GET /api/health` reports coarse configuration health only, including `provider.state` (`HEALTHY`, `DEGRADED`, `RATE_LIMITED`, `UNAVAILABLE`, `CONFIGURATION_ERROR`) and `database` (`not_configured`, `connected`, `unavailable`; cached 60 s, never the URL).
- Lint the backend with `pip install -r requirements-dev.txt` then `python -m ruff check .` (also run in CI).
- `GET /api/sources` returns public source metadata.
- `POST /api/ask` takes `{ "question": "...", "language": "en" | "ta" }` and returns an answer mode, cited sources, a caveat, and `notices` (scheme change notices labelled `official` or `reported`).
- `GET /api/changes?language=en|ta` lists tracked scheme changes. Add new ones in `backend/app/changes.py` with the evidence type, source URL and check date.
- No prompt history or profile is persisted.
