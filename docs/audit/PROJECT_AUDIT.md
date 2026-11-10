# Project audit (Phase 0)

**Audit date:** 10 November 2026
**Auditor:** development agent, at the developer's request
**Branch:** `phase-0-1/audit-and-research` (branched from `main` at `4341742`)
**Workspace:** `D:\CivicLens` (verified absolute path; no symlinks or junctions leaving the workspace were found among project files)

## Summary

The repository is **not empty**. It holds a working, deliberately narrow prototype built on 9 November 2026: a bilingual (Tamil/English) React client, a FastAPI backend with lexical and optional Gemini-vector retrieval, structured Gemini generation with citation-ID allowlisting, a privacy filter, a request budget, an unapplied PostgreSQL schema, and about 20 research and operations documents.

The prototype is cautious and honest about its limits. This audit finds that it should be **extended, not replaced**. Two defects block the product vision, though, and one dependency expires within three weeks. See [TECHNICAL_DEBT.md](TECHNICAL_DEBT.md).

## Repository state

| Item | Finding |
|---|---|
| Git | 7 commits on `main`, all authored by `Nitesh-N-D`. Local `main` is **6 commits ahead of `origin/main`** (unpushed). The working tree was clean at the start of the audit. |
| Branches | `main` only (plus `origin/main`). This audit created `phase-0-1/audit-and-research`. |
| Tracked files | 56. `frontend/dist/`, `backend/.venv/`, and `frontend/node_modules/` exist locally but are git-ignored. |
| Secrets | No `.env` file is tracked. `backend/.env.example` holds placeholders only. No key-like strings were found in tracked files. A local `backend/.env` was **not opened** (policy: never print environment files). |
| Deployments | None configured. No hosting config, CI workflow, or cloud project reference exists. |
| Database | None connected. `backend/migrations/0001_initial_schema.sql` is a reviewed-but-unapplied proposal. |
| External integrations | Gemini REST only (server-side, optional). No government APIs, no scraping, no other providers. |
| Licence | **No `LICENSE` file.** The repository's legal reuse status is undefined. |

## Verification run during this audit

| Check | Command | Result |
|---|---|---|
| Backend unit tests | `.venv\Scripts\python.exe -m unittest discover -s tests` | 12 / 12 pass (0.009 s) |
| Offline retrieval eval | `python evaluation/evaluate_retrieval.py` | Recall@4 7/7, MRR 1.000 (but see TD-03: the metric cannot detect false positives) |
| Frontend build | `npm.cmd run build` | Pass; JS 246 kB (76 kB gzip), CSS 19.6 kB |
| Frontend dependency audit | `npm.cmd audit --omit=dev` | 0 vulnerabilities |
| Manual probes | Privacy filter and retrieval with ad-hoc queries | **Two blocking defects found** (TD-01, TD-03) |

No services were started, no packages were installed, and no files outside the workspace were touched.

## Installed runtime (observed)

- Python 3.11.9 (project-local `.venv`): fastapi 0.162.2, starlette 1.10.0, pydantic 2.14.3, uvicorn 0.54.0
- Node.js v22.20.0: react 19.2, vite 7.1, typescript 5.9

## Related Phase 0 documents

- [EXISTING_SYSTEM_ANALYSIS.md](EXISTING_SYSTEM_ANALYSIS.md): component-by-component review: reuse, modify, replace
- [TECHNICAL_DEBT.md](TECHNICAL_DEBT.md): prioritised defects and debt
- [ENVIRONMENT_REQUIREMENTS.md](ENVIRONMENT_REQUIREMENTS.md): tools, versions, resource budget
- [DEVELOPMENT_SAFETY.md](DEVELOPMENT_SAFETY.md): how the CLAUDE.md / AGENTS.md rules apply to this project
