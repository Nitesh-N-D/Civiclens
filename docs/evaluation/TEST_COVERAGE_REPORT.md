# Test coverage report

**Date:** 11 Nov 2026 · Measured locally on Windows. CI runs the same tests but doesn't collect coverage.

## Backend: 86 unit tests, 84% statement coverage

`coverage run --source=app -m unittest discover -s tests` then `coverage report`, run from `backend/`.

| Module | Statements | Coverage | Notes |
|---|---:|---:|---|
| eligibility, changes, config, models, text | 201 | 100% | |
| corpus | 33 | 97% | |
| service | 174 | 94% | Answer pipeline, privacy filter, limiter, cache |
| main | 114 | 88% | |
| security | 8 | 88% | |
| db | 43 | 81% | |
| corpus_store | 108 | 79% | Live database load paths are tested with fakes only |
| retrieval | 108 | 79% | The embedding branch is only partly covered |
| auth | 82 | 78% | |
| monitoring | 58 | 69% | `allowed_by_robots` and network `fetch` have no tests |
| admin | 22 | 68% | |
| gemini | 137 | 64% | The HTTP transport and response parsing aren't exercised without a live key |
| **Total** | **1,088** | **84%** | |

## Frontend: 20 tests, 90.8% statements

`npm run coverage`, run from `frontend/` (Vitest with `@vitest/coverage-v8`, over `src/`).

| Statements | Branches | Functions | Lines |
|---:|---:|---:|---:|
| 90.79% (296/326) | 77.73% (185/238) | 87.5% (126/144) | 91.63% (252/275) |

## Beyond unit tests

- Retrieval evaluation (28 cases) and answer evaluation (20 in-scope plus 8 abstention cases): see the [RAG evaluation report](RAG_EVALUATION_REPORT.md). The retrieval evaluation fails CI on regression.
- Migrations, the corpus seed, embedding storage and the first source-monitor run were each run once against the real Supabase database during development. They aren't part of the automated suite.
- No browser end-to-end tests (such as Playwright) and no load tests exist yet.

## Biggest gaps

The biggest gaps are the Gemini HTTP adapter, robots.txt handling and fetching in monitoring, and the admin endpoints' error paths. Coverage percentages measure which lines run, not whether answers are correct.
