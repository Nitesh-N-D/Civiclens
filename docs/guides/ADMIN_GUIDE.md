# Maintainer overview

The optional `/api/admin/overview` endpoint and UI panel provide a **read-only local overview** of source review status and coarse Gemini provider health. They cannot edit, approve, publish, or fetch sources. Automatic source monitoring is not configured.

## Enable locally

Set `CIVICLENS_ADMIN_TOKEN` in `backend/.env` using a long random value kept in a password manager. Do not commit, print, or share the token. Restart the backend and open **Maintainer overview** in the page footer. Enter the token into the password field; the browser keeps it in memory only for the current view and clears it when closed.

When disabled, the API returns 404 for the overview route. When enabled, authorization uses an exact bearer token and constant-time comparison. The route returns source identifiers, review dates, review counts, and provider status categories; it never returns API keys.

This is a local single-shared-token convenience for the prototype, not a production admin identity system. Do not expose it on a public deployment. Before production, replace it with a maintained authentication/authorization system, rate limiting, audit identity, and role-scoped actions.
