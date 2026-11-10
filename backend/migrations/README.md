# Database migration status

| File | Adds |
|---|---|
| `0001_initial_schema.sql` | Source registry, versions, evidence chunks, schemes, claims, eligibility rules, review events |
| `0002_search_and_change_tracking.sql` | pgvector + `VECTOR(768)` HNSW index, English and Tamil (`simple`) full-text GIN indexes, `scheme_aliases`, `scheme_changes` |

| `0003_usage_counters.sql` | `api_usage_daily` (one aggregate counter per UTC day; no visitor data) and RLS on every table so Supabase's public Data API can read nothing |

Apply with `python scripts/migrate.py` from `backend/` (`--status` to list). The runner applies pending files in filename order; each file opens and commits its own transaction and inserts its row into `schema_migrations`, so a failure leaves nothing behind and re-running is safe. The API never runs migrations.

Today the application reads and writes only `api_usage_daily` (the persistent daily Gemini budget). The source, evidence and scheme tables are created but empty; the runtime still answers from the static Python corpus.

Before applying this migration to any database, validate SQL against the selected PostgreSQL version, review source-content retention and provider terms, prepare a verified backup and restore procedure, then apply it to an empty non-production database. Do not point it at existing or production data without a reviewed, non-destructive migration plan.

No user profiles, chat history, uploaded documents, Aadhaar/bank fields, or raw prompt storage are part of the schema. Embeddings are optional JSON arrays over public source text; production deployments may choose a reviewed vector extension and a dimension/version migration strategy later.
