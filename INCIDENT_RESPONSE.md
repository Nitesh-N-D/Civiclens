# Incident response plan

**Status:** Prepared procedure; no production service exists.

## Severity examples

- **Critical:** exposed API key, private citizen data disclosure, unsafe eligibility guidance causing plausible harm, unauthorized database access.
- **High:** stale/contradictory scheme data presented as current, citation points to unrelated evidence, public service unavailable during a known application period.
- **Moderate:** broken official link, incorrect translation, transient provider or quota outage.

## Response steps

1. Record time, affected route/source/version, observed behavior, and a sanitized example. Do not copy secrets or personal data into an incident ticket.
2. If a harmful source claim is suspected, disable the affected record/claim first; preserve a versioned audit reference and the official source link.
3. If a key is exposed, revoke it with the provider, replace it through secret management, inspect access logs for misuse, and verify the old key no longer works. Never paste the key into the incident record.
4. If user data may have been disclosed, restrict access, preserve necessary evidence, assess legal/contractual notification duties with the responsible owner, and do not make unsupported public claims.
5. For Gemini quota or outage, keep source-search/abstention mode active; do not rotate keys to evade shared quota or enable paid fallback automatically.
6. Verify the fix against a reproducible test case and the source owner; log the reviewer and decision.
7. Review root cause, user impact, duration, mitigations, and preventive actions.

## Contacts and service-specific actions

No on-call owner, provider account, production database, or public endpoint has been configured. Populate the responsible owner, escalation path, provider console links, and notification obligations before a pilot.
