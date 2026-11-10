# Environment requirements (Phase 0)

**Date:** 10 November 2026

## Developer machine (given)

Windows 11 · 16 GB RAM · 512 GB storage · VS Code · Claude Code. PowerShell is the primary shell; Git Bash is also available.

## Required tools (verified present)

| Tool | Required | Observed | Scope |
|---|---|---|---|
| Python | 3.11+ | 3.11.9 | Project `.venv` only; never the global site-packages |
| Node.js | 22 LTS | v22.20.0 | `npm.cmd` (PowerShell execution policy blocks `npm.ps1` on some machines) |
| Git | any recent | present | Repo-local identity: `Nitesh-N-D` |

Not required now: Docker, local PostgreSQL, GPU drivers, CUDA, model weights. Later phases should use a managed Supabase project rather than a local Postgres. A local container needs explicit approval and a memory cap.

## Local resource budget

| Activity | Expected RAM | Disk | Notes |
|---|---|---|---|
| Vite dev server | ~150–300 MB | `node_modules` ~100 MB | One instance only |
| Uvicorn (`--workers 1`) | ~80–150 MB | `.venv` ~60 MB | Loopback only |
| Unit tests | < 100 MB, < 1 s | — | |
| Frontend build | ~300 MB peak, ~1 s | `dist/` < 1 MB | |
| Embedding the corpus | negligible locally | — | Runs on Google's servers; bounded by corpus size and free quota |

The whole stack fits comfortably under 1 GB of RAM and 500 MB of disk. Anything that would exceed **2 GB RAM or 1 GB of new disk** must be raised with the developer first (the policy hard limit is 5 GB of disk).

## Off-machine compute

- **Generation and embeddings:** Gemini API (server-side).
- **Experiments** (embedding-model comparison, reranker trials, larger evals): Kaggle Notebooks, with no keys or personal data in public notebooks. Nothing in Phases 0–1 needs this.

## Configuration

`backend/.env` (git-ignored) holds `GEMINI_API_KEY_1`, `GEMINI_API_KEY_2`, `GEMINI_MODEL`, `GEMINI_EMBEDDING_MODEL`, budgets, and `ALLOWED_ORIGINS`. The frontend holds **no** secrets. See `backend/.env.example`.
