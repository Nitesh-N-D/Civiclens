# Deployment guide — preparation only

**Status:** Free-tier configuration prepared (Render + Cloudflare Pages + optional Supabase); nothing deployed.
**Current runtime:** Vite client + FastAPI API + static in-process discovery corpus.

## Deployment shape

For a later pilot, use a static frontend host/CDN, a separate Python API service, and a managed PostgreSQL database only after the source registry and privacy design are ready. Keep the Gemini integration server-side. Do not expose the development servers or use the current in-memory request budget as public abuse protection.

## Provider selection gates

Before selecting a host, compare current terms and limits for the intended public-interest/non-commercial use, deployment geography and data processing, API execution/network needs, sleep/availability behavior, database backup and restore, log retention, custom-domain/TLS cost, traffic quotas, and overage behavior. Free tiers can change or be restricted; no free production availability is promised. For example, Vercel documents its Hobby plan as personal/non-commercial use only: [Vercel Hobby plan](https://vercel.com/docs/plans/hobby), [terms](https://vercel.com/legal/terms).

Do not create accounts, enable billing, provision resources, publish a URL, or connect production credentials as part of this preparation. Public deployment requires explicit authorization under the project safety policy.

## Build and configuration

1. Build the client with `npm.cmd run build` in `frontend/`.
2. Build a backend image or install from `backend/requirements-lock.txt` in a clean Python 3.11 environment.
3. Configure allowed browser origins to the exact deployed HTTPS frontend origin.
4. Set Gemini key(s), model, and request caps through the host's secret manager; never use frontend environment variables for keys.
5. Do not configure public Gemini requests with free-tier personal/sensitive user details.
6. Configure an externally observable health check that returns no credential values.
7. Do not apply the PostgreSQL migration until it has been reviewed against the selected server version and recovery plan.

## Prepared free-tier configuration (not applied)

The repository now carries configuration for one candidate free-tier shape. The developer creates the accounts and approves any public URL; nothing here has been deployed.

| Piece | Candidate | File |
|---|---|---|
| API | Render free web service (sleeps when idle; first request after sleep is slow) | [`render.yaml`](../../render.yaml) — `autoDeploy: false`, health check `/api/health`, keys and `ALLOWED_ORIGINS` entered in the dashboard (`sync: false`) |
| Frontend | Cloudflare Pages, build `npm run build`, root `frontend`, output `dist` | [`frontend/public/_headers`](../../frontend/public/_headers) — security headers and CSP; set the CSP `connect-src` to the exact API origin |
| Database | Supabase free PostgreSQL (optional). Stores the aggregate daily Gemini counter and the reviewed corpus; if it is down the API answers from the last good or built-in corpus | [`0001`–`0004`](../../backend/migrations/README.md), [`scripts/migrate.py`](../../backend/scripts/migrate.py) |

Steps once approved:

1. Create the Render service from the blueprint; enter `GEMINI_API_KEY_1`, `GEMINI_API_KEY_2` and `ALLOWED_ORIGINS` (the Pages origin) as secrets. `TRUST_FORWARDED_FOR=true` is correct only behind Render's proxy.
2. Create the Pages project with environment variable `VITE_API_BASE=https://<service>.onrender.com` (public, not a secret). Narrow `connect-src` in `_headers` to that origin.
3. Check `/api/health` reports `HEALTHY`, ask one English and one Tamil synthetic question, and confirm a 429 falls back to cited search mode.
4. Leave `CIVICLENS_ADMIN_TOKEN` unset on the public service.

### Optional: Supabase

1. Create a free Supabase project (no billing). Note the database password; do not commit it.
2. Copy the **Transaction pooler** connection string (Connect → port 6543, IPv4-compatible; Render free has no IPv6 egress for the direct host) and append `?sslmode=require`.
3. Put it in `backend/.env` as `DATABASE_URL=` and run `python scripts/migrate.py` from `backend/` once (`--status` lists what is applied). Each file runs in one transaction and records itself, so re-running is safe. Then run `python scripts/seed_corpus.py` to copy the built-in corpus into the database (also safe to re-run).
4. Enter the same URL as the `DATABASE_URL` secret on Render.
5. `/api/health` should then report `"database": "connected"` and `"corpus": "database"`. `unavailable` means the API keeps working on the in-memory budget.

Only this server-side URL is used. The anon and `service_role` keys are not needed and should not be configured: the frontend never calls Supabase, and migration 0003 enables RLS with no policies on every table so the public Data API sees nothing. Free projects pause after about a week without activity and have no automatic backups (see [backup and recovery](BACKUP_AND_RECOVERY.md)); losing this database loses a usage counter and seeded copies of records that are also in the repository, so re-running the migrations and the seed script restores it.

## Release sequence

1. Validate source rights, latest controlling rules, and Tamil specialist review.
2. Complete the security, privacy, and production checklist.
3. Run backend tests, frontend build, source-evidence evaluation, and mobile/accessibility review.
4. Deploy to a non-public staging environment with synthetic questions and no citizen data.
5. Verify links, citations, provider-unavailable behavior, quotas, backups, and incident response.
6. Obtain explicit public-release approval before publishing.
