# CivicLens

CivicLens is an independent, Tamil Nadu-first public information prototype. It helps people explore government service and scheme information with source links. It is not a government website and does not determine eligibility or submit applications.

## Current state

- Phase 0–3 research, source audit, requirements, and architecture baseline are in [`docs/research`](docs/research/).
- Phase 4 interface includes Tamil/English language switching and a responsive, accessible layout.
- Phase 5 API provides lexical retrieval, optional Gemini vector retrieval, source-grounded structured Gemini responses, citation ID validation, privacy filtering, bounded retries, and a search-only fallback.
- The current four source records are **discovery summaries**. They are not cleared as current scheme rules; no authoritative eligibility answer should be inferred from them.
- No production deployment, service account, billing, or government integration is configured.

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

More detail: [`DEVELOPMENT_GUIDE.md`](DEVELOPMENT_GUIDE.md), [`TESTING.md`](TESTING.md), [`SECURITY.md`](SECURITY.md), and [`ENVIRONMENT_SETUP.md`](ENVIRONMENT_SETUP.md).

## Known limitations

- No citizen interviews have been conducted.
- Source access/reuse terms and latest controlling government orders remain to be verified.
- The source corpus is hand-authored and static; no ingestion or monitoring worker exists.
- Gemini and embeddings require keys and consume provider quota. The local daily request budget is process-local, not a production distributed quota.
- The sensitive-content filter is best-effort and cannot guarantee detection of every personal detail.
- Eligibility checklists, comparison, admin review UI, source monitoring, and production hosting are not yet implemented.
