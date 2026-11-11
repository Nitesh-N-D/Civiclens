# CivicLens

CivicLens is an independent, Tamil Nadu-first public information prototype. It helps people explore government service and scheme information with source links. It is not a government website and does not determine eligibility or submit applications.

## Current state

- **Research and requirements (Phases 0–3):** in [`docs/research`](docs/research/) and [`docs/audit`](docs/audit/).
- **Interface:** Tamil and English throughout, a responsive and accessible layout, a dark theme, scheme search, session history and a printable helper checklist.
- **Answers:** hybrid retrieval (lexical, plus optional Gemini embeddings stored in pgvector), source-grounded Gemini answers with citation and claim–evidence checks, a privacy filter, per-client limits, and a cited search-only fallback whenever Gemini is unavailable.
- **Eligibility screening:** a voluntary questionnaire that screens Pudhumai Penn and the Free Education Scheme against conditions quoted word for word from each scheme's source. It also gives a document checklist (never marked mandatory), application guidance and a side-by-side comparison. Because no condition has been verified by a person yet, the best possible result is *"requires official verification"*.
- **Data:** with `DATABASE_URL` set, the corpus, embeddings, daily Gemini budget, source checks and audit log live in Supabase PostgreSQL. Row-level security is on for every table. Without it, the built-in records keep working.
- **Maintainers:** Supabase Auth sign-in with viewer, reviewer and maintainer roles. Reviewers can record source checks, and each check is audit-logged.
- **Source monitoring:** a weekly GitHub Action fetches each official source (honouring robots.txt), fingerprints its visible text and records a check for a person to review. It never changes answers by itself.
- **Evaluation:** a 28-case EN/TA/mixed retrieval evaluation that runs in CI, plus an end-to-end answer evaluation. See [`docs/evaluation`](docs/evaluation/).
- The four source records are **discovery summaries**. None has yet been human-verified as the current controlling rule.
- **Not yet deployed:** `render.yaml` and the Cloudflare Pages headers are ready, but hosting needs accounts the developer creates ([deployment guide](docs/guides/DEPLOYMENT_GUIDE.md)).

## Requirements

- Windows PowerShell and Python 3.11+
- Node.js 22+
- Network access for initial project-local dependency installation
- Gemini API key(s) are optional for source-search fallback and are configured only on the backend

## Local setup

Create a local Python environment and install the locked dependencies:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
Copy-Item .env.example .env
```

Leave both Gemini key values empty for source-search mode. To enable Gemini, put eligible keys in `backend/.env`; never place them in frontend variables or commit `.env`. Set `GEMINI_ENABLE_EMBEDDINGS=true` only when you want hybrid dense + lexical retrieval. On the free Gemini tier, do not submit personal or sensitive content; the API terms permit submitted content to be reviewed/used to improve Google products.

Start the API in one PowerShell terminal:

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

Start the web client in a second terminal:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Open the local URL printed by Vite (normally `http://127.0.0.1:5173`). API documentation is at `http://127.0.0.1:8000/api/docs` while the local server is running.

## Verification

```powershell
cd frontend
npm.cmd run build
cd ..\backend
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

More detail (index: [`docs/README.md`](docs/README.md)): [`DEVELOPMENT_GUIDE.md`](docs/guides/DEVELOPMENT_GUIDE.md), [`TESTING.md`](docs/guides/TESTING.md), [`SECURITY.md`](SECURITY.md), [`ENVIRONMENT_SETUP.md`](docs/guides/ENVIRONMENT_SETUP.md), [`ADMIN_GUIDE.md`](docs/guides/ADMIN_GUIDE.md), [`DEPLOYMENT_GUIDE.md`](docs/guides/DEPLOYMENT_GUIDE.md), and [`PRODUCTION_CHECKLIST.md`](docs/guides/PRODUCTION_CHECKLIST.md).

## Known limitations

- No citizen interviews or user studies have been run, and the answer review is still waiting for a person (an agent pre-review only).
- The corpus has four hand-authored summaries. The latest Government Orders and the sources' reuse terms still need checking.
- Eligibility conditions are quoted from directory summaries, not verified rules, so screening never says "eligible".
- Gemini's free tier may use submitted text to improve Google products, so don't enter personal details. The privacy filter uses patterns and can be bypassed.
- The claim–evidence gate is a heuristic, not an entailment check.
- The per-client limiter and answer cache are held in memory per process. Only the daily budget is shared, through the database.
- Licensed under the [MIT License](LICENSE).
