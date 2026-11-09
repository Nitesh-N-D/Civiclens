# Database migration status

`0001_initial_schema.sql` is a proposed PostgreSQL schema for a future curated corpus and source-review workflow. It is **not applied** and the current application does not connect to a database. The runtime still uses the small static Python corpus. The migration runner and version insertion are not implemented.

Before applying this migration to any database, validate SQL against the selected PostgreSQL version, review source-content retention and provider terms, prepare a verified backup and restore procedure, then apply it to an empty non-production database. Do not point it at existing or production data without a reviewed, non-destructive migration plan.

No user profiles, chat history, uploaded documents, Aadhaar/bank fields, or raw prompt storage are part of the schema. Embeddings are optional JSON arrays over public source text; production deployments may choose a reviewed vector extension and a dimension/version migration strategy later.
