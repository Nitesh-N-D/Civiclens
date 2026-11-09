# Deployment guide — preparation only

**Status:** No deployment has been selected or performed.  
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

## Release sequence

1. Validate source rights, latest controlling rules, and Tamil specialist review.
2. Complete the security, privacy, and production checklist.
3. Run backend tests, frontend build, source-evidence evaluation, and mobile/accessibility review.
4. Deploy to a non-public staging environment with synthetic questions and no citizen data.
5. Verify links, citations, provider-unavailable behavior, quotas, backups, and incident response.
6. Obtain explicit public-release approval before publishing.

