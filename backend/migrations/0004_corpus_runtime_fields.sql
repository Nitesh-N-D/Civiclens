-- CivicLens migration 0004: fields the runtime needs to serve the corpus from PostgreSQL.
-- Additive only. Populated by scripts/seed_corpus.py; read by app/corpus_store.py.

BEGIN;

-- Citizen-facing caveat shown with each source (e.g. "Official directory · confirm current rules").
ALTER TABLE sources
    ADD COLUMN status_label TEXT,
    ADD COLUMN display_order INTEGER NOT NULL DEFAULT 0;

-- Bilingual scheme cards and the source each card links to.
ALTER TABLE schemes
    ADD COLUMN department_ta TEXT,
    ADD COLUMN category_ta TEXT,
    ADD COLUMN overview_en TEXT,
    ADD COLUMN overview_ta TEXT,
    ADD COLUMN source_id TEXT REFERENCES sources(id);

-- Change notices are matched against questions by every name people use for the scheme.
ALTER TABLE scheme_changes
    ADD COLUMN scheme_name_en TEXT,
    ADD COLUMN scheme_name_ta TEXT,
    ADD COLUMN match_names TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[];

-- One version row per distinct content of a source, so re-seeding is idempotent and every
-- text change is kept as a new version instead of overwriting history.
CREATE UNIQUE INDEX source_versions_source_hash_idx
    ON source_versions (source_id, content_hash) WHERE content_hash IS NOT NULL;

INSERT INTO schema_migrations (migration_version) VALUES ('0004_corpus_runtime_fields');

COMMIT;
