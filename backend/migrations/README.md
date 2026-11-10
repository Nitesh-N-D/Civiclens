# Database migration status

| File | Adds |
|---|---|
| `0001_initial_schema.sql` | Source registry, versions, evidence chunks, schemes, claims, eligibility rules, review events |
| `0002_search_and_change_tracking.sql` | pgvector + `VECTOR(768)` HNSW index, English and Tamil (`simple`) full-text GIN indexes, `scheme_aliases`, `scheme_changes` |
| `0003_usage_counters.sql` | `api_usage_daily` (one aggregate counter per UTC day; no visitor data) and RLS on every table so Supabase's public Data API can read nothing |
| `0004_corpus_runtime_fields.sql` | Runtime fields for serving the corpus (source status label and order, Tamil scheme fields, scheme `source_id`, change-notice names) and a unique `(source_id, content_hash)` index for idempotent seeding |

Apply with `python scripts/migrate.py` from `backend/` (`--status` to list). The runner applies pending files in filename order; each file opens and commits its own transaction and inserts its row into `schema_migrations`, so a failure leaves nothing behind and re-running is safe. The API never runs migrations.

The application writes `api_usage_daily` (the persistent daily Gemini budget) and reads the corpus: `sources`, `source_versions`, `documents`, `evidence_chunks`, `schemes` and `scheme_changes`, populated by `python scripts/seed_corpus.py`. Versions that are `retired` or `contested` are not served. The `VECTOR` column and the claim/eligibility tables are not used yet.

Before applying this migration to any database, validate SQL against the selected PostgreSQL version, review source-content retention and provider terms, prepare a verified backup and restore procedure, then apply it to an empty non-production database. Do not point it at existing or production data without a reviewed, non-destructive migration plan.

No user profiles, chat history, uploaded documents, Aadhaar/bank fields, or raw prompt storage are part of the schema. Embeddings (over public source text only) go in the `VECTOR(768)` column from `0002`; a model or dimension change needs its own migration.
