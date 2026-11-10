# Development safety (Phase 0)

**Date:** 10 November 2026

`CLAUDE.md` and `AGENTS.md` are the binding policies. This page records how they apply to this specific repository, so later phases don't have to re-derive them.

## Boundaries

- **Workspace:** `D:\CivicLens` only. Every write, delete, and generated artefact stays inside it; temporary scratch files go to the agent's session scratch directory, never elsewhere on disk.
- **Git:** work on feature branches (`phase-N/...`). No direct commits to `main`, no merge, push, force-push, history rewrite, `reset --hard`, or `clean` without explicit approval. Commits are authored with the developer's configured identity (`Nitesh-N-D`) and carry no co-author trailers, per the developer's instruction.
- **Secrets:** never open, print, or regenerate `backend/.env`. Keys live only in the backend environment and in the hosting provider's secret store.
- **Network:** official documentation and government pages may be read for research. No automated crawling of government sites until per-source terms and robots rules are recorded in the source registry (Phase 2).

## Actions that always need developer approval

| Action | Why |
|---|---|
| Creating cloud accounts or projects (Supabase, Render, Vercel, Cloudflare, Kaggle) | External and account-bound |
| Any billing or paid-tier activation | Cost |
| Public deployment or exposing a local port | Abuse and quota exhaustion (TD-05) |
| Pushing to `origin` or merging to `main` | Shared history |
| Bulk deletion, or deleting source/migration/config files | Irreversible |
| Applying migrations to any non-throwaway database | Data |
| Choosing the default Gemini model (TD-02) | Depends on quota visible only in the developer's AI Studio dashboard |
| Choosing a licence (TD-10) | Legal |

## Safe to do autonomously

Read code and docs; edit project source; add tests; run unit tests, builds, and `npm audit`; run small offline evaluations; install project-local dependencies listed in the lockfiles.

## Hardware rules in practice

- One dev server of each kind at a time; Uvicorn with `--workers 1`.
- No local model weights, training, or large embedding jobs. Embedding the corpus is a remote API call and must respect the free quota.
- No Docker unless approved with a memory cap.
