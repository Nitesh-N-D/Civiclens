# Maintainer guide

CivicLens has a small maintainer area (**Maintainer overview**, at the bottom of the page). It shows source review status and Gemini provider health, and lets a reviewer record a **source check**: that they opened an official source and found it unchanged, changed, unreachable, or needing manual review. Every check is written to `audit_log` in the same database transaction, with the reviewer's account and email.

It cannot publish answers, approve eligibility rules, or edit source text. Those stay offline (`scripts/seed_corpus.py`, with human review).

## Roles

| Role | Can |
|---|---|
| `viewer` | Open the overview, recent checks and the audit log |
| `reviewer` | Everything a viewer can, plus record source checks |
| `maintainer` | Same as reviewer today; reserved for role management and publishing |

An account that signs in but has no row in `admin_roles` gets nothing: the API answers 404 as if the area did not exist.

## Production sign-in: Supabase Auth

Needs `DATABASE_URL`, `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` on the API (Render dashboard secrets, or `backend/.env` locally) and migration `0005`.

1. In the Supabase dashboard, **Authentication → Sign In / Providers**: turn off **Allow new users to sign up**. Keep the email provider on.
2. **Authentication → Users → Add user**: create each maintainer with a strong password (or send an invite). Use multi-factor authentication on the Supabase dashboard account itself.
3. **Project Settings → API Keys**: copy the project URL and the **publishable** key (`sb_publishable_…`, or the legacy `anon` key). Never use the `service_role`/secret key here.
4. Grant a role from `backend/`:

   ```powershell
   .\.venv\Scripts\python.exe scripts\grant_role.py reviewer@example.org reviewer
   .\.venv\Scripts\python.exe scripts\grant_role.py reviewer@example.org --revoke
   ```

   Both actions are written to `audit_log`.

How it works:

- The browser sends the email and password straight to Supabase Auth (`/auth/v1/token`). CivicLens never receives or stores the password. This is maintainer sign-in only; citizens are never asked to sign in or for passwords.
- The access token is kept in page memory only (not `localStorage`); reloading or closing the tab signs out of the page, and **Sign out** also revokes the session at Supabase.
- The API checks each token by asking Supabase (`/auth/v1/user`), so revoked or expired tokens stop working, then looks up the role in `admin_roles`. Results are cached for 60 seconds, keyed by a hash of the token. Tokens are never logged.
- If Supabase or the database is unreachable, access is refused (fail closed); public answers are unaffected.
- The publishable key and URL are returned by `/api/health` so the page can sign in. They are public by design; RLS on every table (migrations `0003` and `0005`) means they cannot read any data.

## Local development: static token

`CIVICLENS_ADMIN_TOKEN` in `backend/.env` still opens the overview, but **only as `viewer`**: it can never record a check or change anything. Use a long random value and do not set it on public hosting. When Supabase sign-in is configured, the page shows the email/password form instead of the token field.

## What the API exposes

- `GET /api/admin/overview` (viewer): sources, review counts, provider state, your role, the last 20 checks and audit entries. Never returns keys.
- `POST /api/admin/sources/{id}/checks` (reviewer, Supabase sign-in only): body `{"outcome": "reachable|changed|unreachable|manual_review", "note": "3–500 chars"}`.

No access → 404. Signed in but the role is too low → 403.

## Weekly source monitor

The `Source monitor` GitHub Action (`.github/workflows/source-monitor.yml`) runs every Monday at 03:30 UTC, and you can also start it from the Actions tab. It uses the `DATABASE_URL` repository secret. For each official source it records a check in `source_checks` (shown in the maintainer overview), with a note starting `automated:`:

- `reachable`: the page loaded and its visible text is the same as last time.
- `changed`: the visible text differs. A reviewer should open the page and decide whether the record needs updating.
- `unreachable`: the fetch failed or timed out.
- `manual_review`: the page loaded but has no readable text (for example, a script-only page).

It never changes answers or source text.

**Known behaviour (11 Nov 2026):** GitHub's runners are outside India, and two Tamil Nadu government sites (`cra.tn.gov.in` and `tnesevai.tn.gov.in`) time out from them. Both load in a few seconds from India. Treat `unreachable` for those two as "not checked this week", not as the site being down. To check them, run `python scripts/monitor_sources.py` from `backend/` on a machine in India; it records to the same database.
