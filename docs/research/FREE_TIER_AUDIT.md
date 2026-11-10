# Free-tier audit

**Checked:** 10 November 2026. Re-check at every deployment milestone, because free tiers change without notice.
**Source quality:** Gemini facts come from Google's official docs (now served at `aistudio.google.com/docs/*`). Hosting facts come from third-party summaries dated Sept–Nov 2026 that cite the providers' own pages. **Re-verify those on the provider site before creating any account.**

No account, project, key, or billing was created during this audit.

| Service | Purpose | Free allowance (as found) | Limitations | Fallback |
|---|---|---|---|---|
| **Gemini API**, generation | Answer explanation, structured claims | Free-of-charge models include `gemini-3.8-flash`, `gemini-3.6-flash`, `gemini-3.5-flash-lite`, `gemini-3.1-flash-lite`. Exact limits are **not published**; they appear only in the AI Studio dashboard. One third-party reading (21 Oct 2026): 3.8 Flash about 5 RPM / 20 RPD; 3.5 and 3.1 Flash-Lite about 15 RPM / 500 RPD. | **Limits are per project, not per key**, so two keys in one project share the quota. RPD resets at midnight Pacific. Free-tier content is **used to improve Google products**. No Search grounding, and no Batch/Flex on 3.8/3.6 Flash. `gemini-2.5-flash` shuts down **1 Dec 2026**. | Search-only mode (already implemented); cache answers to repeated public questions |
| **Gemini API**, embeddings | Dense retrieval | `gemini-embedding-2` (recommended, stable, 8,192-token input, 128–3072 dims) and `gemini-embedding-001` (shutdown 14 May 2028) are both free for standard input. | The same project-level quota applies. Batch is unavailable on free for `-001`. Embed the corpus **once** and store the vectors, never per request. | Lexical/FTS retrieval only |
| **Supabase** Free | Postgres + pgvector + FTS, Auth | 2 active projects; 500 MB database; 1 GB file storage; 5 GB egress; 50k MAU | **Pauses after 1 week of inactivity**; goes read-only above 500 MB; **no backups**; no SLA | Scheduled keep-alive check (within terms); nightly `pg_dump` to the developer's storage; the corpus is small (estimated well under 50 MB) |
| **Render** Free web service | FastAPI backend | 750 instance-hours per workspace per month; 512 MB RAM, 0.1 CPU | **Sleeps after 15 min**, with a cold start of about 1 min; one always-on service uses the whole allowance; bandwidth reportedly cut to 5 GB/month (Apr 2026); Render says "do not use for production" | Frontend shows a "waking up" state; consider a different backend host at pilot |
| **Render** Free Postgres | — | 1 GB, 1 per workspace | **Expires 30 days after creation, then deleted** | **Do not use.** Use Supabase |
| **Vercel** Hobby | Static frontend | 100 GB transfer; 1M edge requests | **Non-commercial personal use only**; commercial use requires Pro ($20/mo) | Cloudflare Pages |
| **Cloudflare Pages** Free | Static frontend (recommended) | Unlimited bandwidth and requests for static assets; 500 builds/month; Functions use Workers' 100k requests/day | Cloudflare now recommends Workers for new projects; Functions are capped daily | Vercel Hobby, only while clearly non-commercial |
| **GitHub** Free | Source control, CI | Actions minutes for private repos are limited (re-check the current allowance); public repos are free | Do not run heavy jobs in CI | Run tests locally |
| **Kaggle** Notebooks | Embedding/reranker experiments | Free GPU hours per week (re-check the current quota) | Never put keys or personal data in public notebooks | Defer experiments |

## Feasibility verdict

- **Prototype and small pilot: feasible within free tiers**, provided that (a) answers are cached, (b) per-client rate limits exist before public exposure (TD-05), and (c) search-only fallback stays first-class. At about 20–500 generations per day, Gemini is the binding constraint, not hosting.
- **Production for the public: not sustainably free.** Free Gemini usage sends content to Google for product improvement (incompatible with citizens' personal details); Supabase Free has no backups; Render Free sleeps. A real launch needs either an approved budget or a sponsor/partner. That decision belongs to the developer, at the deployment gate.

## Developer confirmations (10 Nov 2026)

- Both keys belong to **one free-tier project**, so they share one quota; the second key is a credential fallback only. The developer reports the quota runs out quickly.
- AI Studio shows, for reference: `gemini-3.5-flash-lite` 1,048,576 input / 65,536 output tokens, Batch API 10,000,000 concurrent; `gemini-3.8-flash` 1,000,000 input / 64,000 output tokens, Batch API 3,000,000 concurrent. These are token and batch limits, **not** the interactive RPM/RPD that CivicLens consumes, so they don't change the design.
- **Decision:** default `gemini-3.5-flash-lite` (the higher reported free RPD of the two). Server-side, the answer cache, per-client limits, and lexical-first retrieval with embeddings off keep Gemini calls to a minimum.
