# Security and privacy

## Current safeguards

- API keys are read by the backend only from project-local environment configuration.
- Requests are bounded to 1,200 characters; common identifiers and personal-detail patterns are blocked before retrieval or Gemini calls.
- The API does not store chat prompts, generated answers, user profiles, or documents.
- The Gemini adapter uses a bounded timeout, limited retry for transient failures, a quota-aware refusal on HTTP 429, and credential fallback only on key-specific 401/403. It never rotates keys to evade shared project quota.
- Gemini output is schema-validated and citations are restricted to source IDs actually retrieved. Uncited or invalid output falls back to a non-generative response.
- Retrieved source text is treated as untrusted data and cannot override the system instructions.
- CORS allows only the configured local origins by default; local servers bind to loopback.
- The optional maintainer overview is disabled without `CIVICLENS_ADMIN_TOKEN`, read-only, and compares a bearer token without returning it. The client keeps the entered token in memory only.
- No production credentials, real citizen data, or deployment are configured.

## Important limits

- The personal-information filter uses patterns and is not comprehensive. Do not enter personal or sensitive details. On Gemini's unpaid services, user content may be used to improve products and could be reviewed by humans; the backend must never be presented as safe for private case details.
- Citation membership does not prove a generated sentence is entailed by a cited passage. Human review and an evaluation set are required before public eligibility answers.
- The quota cap is in-memory and resets on process restart; it is not sufficient protection for a public multi-instance deployment.
- No production user authentication or edit-capable admin interface exists. The optional overview uses one shared local token and is unsuitable for a public service. Do not expose the development server publicly.
- Government source URLs, access terms, and current rules have not all been verified.

## Before a public pilot

Complete a threat model and privacy review; verify current provider terms and regional handling; implement distributed quotas, abuse protection, secret management, monitoring that excludes raw prompts, content review/access control, backup and recovery; verify all source licenses and documents; and test citation correctness, injection resistance, and deletion/retention behavior. Any paid service or public deployment requires appropriate project authorization.
