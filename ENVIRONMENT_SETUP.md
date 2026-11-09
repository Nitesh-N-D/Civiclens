# Environment setup

## Backend settings

Copy `backend/.env.example` to `backend/.env`. The application reads only that project-local file. It also accepts process environment variables.

| Name | Purpose | Default |
|---|---|---|
| `GEMINI_API_KEY_1` | Primary server-side Gemini API key | Empty; source-search fallback |
| `GEMINI_API_KEY_2` | Secondary credential for credential-specific failover | Empty |
| `GEMINI_MODEL` | Gemini text generation model | `gemini-2.5-flash` |
| `GEMINI_EMBEDDING_MODEL` | Gemini text embedding model | `gemini-embedding-001` |
| `GEMINI_ENABLE_EMBEDDINGS` | Enable optional semantic retrieval in addition to lexical retrieval | `false` |
| `GEMINI_REQUESTS_PER_MINUTE` | Local process request cap for generation | `10` |
| `GEMINI_DAILY_REQUEST_LIMIT` | Local process generation cap per UTC day | `100` |
| `ALLOWED_ORIGINS` | Comma-separated browser origins allowed to call the API | Local Vite origins |
| `CIVICLENS_ADMIN_TOKEN` | Optional shared token for the local read-only maintainer overview | Empty; admin overview disabled |

Gemini usage limits apply at project/model level and change over time. Two keys do not double the project quota. The local cap resets with the process and is only a development safeguard. Do not use free-tier Gemini with personal, sensitive, confidential, or private user information.

Do not enable the shared maintainer token on a public deployment; see [`ADMIN_GUIDE.md`](ADMIN_GUIDE.md).

## Frontend settings

The Vite dev server proxies `/api` to `http://127.0.0.1:8000`. No Gemini key or backend secret belongs in `VITE_*` variables or browser storage.

## Secrets

Do not paste keys into source files, shell output, bug reports, or commits. If a key is exposed, revoke it and replace it. `.env.example` contains blank placeholders only.
