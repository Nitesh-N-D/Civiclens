# Production readiness checklist

## Product and content

- [ ] Conduct 10–20 consent-based citizen interviews and task tests; record no unnecessary personal data.
- [ ] Choose a bounded pilot scope from user evidence.
- [ ] Verify current controlling scheme orders, amendments, deadlines, and official application routes.
- [ ] Confirm source access/reuse terms and permitted storage per source.
- [ ] Obtain fluent Tamil review for all published explanations and checklists.
- [ ] Provide passage-level citations, human verification dates, and clear abstention on conflict/staleness.
- [ ] Validate accessibility, low-bandwidth behavior, mobile layouts, and assisted pathways.

## Engineering and security

- [ ] Replace the static corpus with reviewed database records through a tested migration process.
- [ ] Configure production authentication/authorization for maintainer operations.
- [ ] Replace process-local quotas with shared distributed limits and abuse protection.
- [ ] Confirm free/paid Gemini terms for the actual account tier; do not submit personal data to unpaid services.
- [ ] Store keys in a production secret manager; rotate test keys; verify no secrets in builds/logs.
- [ ] Add timeouts, TLS, origin allowlist, request limits, dependency/security checks, and safe error reporting.
- [ ] Review prompt injection and data-exfiltration risks; test claim grounding beyond citation-ID validation.
- [ ] Define data retention/deletion and anonymous feedback handling.
- [ ] Configure database backups, restoration tests, source-version recovery, and monitoring.
- [ ] Define incident response and escalation owner.

## Release and operations

- [ ] Verify provider plan permits the expected use and check all quotas/overages.
- [ ] Check monthly cost for hosting, database, bandwidth, domain, logs, backups, and AI requests.
- [ ] Pass bilingual factual/citation evaluation thresholds set with reviewers.
- [ ] Test outage, quota exhaustion, stale/conflicting source, and rollback behavior.
- [ ] Complete staging review and obtain explicit authorization before public deployment.

**Current status:** Not production-ready. No source rules have human sign-off, no database is connected, no citizen testing has been conducted, and no production deployment exists.
