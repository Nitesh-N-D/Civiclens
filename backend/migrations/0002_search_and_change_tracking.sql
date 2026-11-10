-- CivicLens migration 0002: full-text search, vector search and scheme change tracking (TD-17).
-- Applied by scripts/migrate.py after 0001 (never by the API at runtime).
-- Additive only: no existing table or column is dropped or rewritten.

BEGIN;

-- pgvector is available on Supabase and most managed PostgreSQL services.
CREATE EXTENSION IF NOT EXISTS vector;

-- Full-text search. PostgreSQL has no Tamil dictionary, so Tamil uses the 'simple'
-- configuration (lower-casing, no stemming); the application keeps its own prefix matching.
ALTER TABLE evidence_chunks
    ADD COLUMN keywords TEXT NOT NULL DEFAULT '',
    ADD COLUMN search_en TSVECTOR GENERATED ALWAYS AS (
        to_tsvector('english', coalesce(text_en, '') || ' ' || keywords)
    ) STORED,
    ADD COLUMN search_ta TSVECTOR GENERATED ALWAYS AS (
        to_tsvector('simple', coalesce(text_ta, '') || ' ' || keywords)
    ) STORED,
    -- gemini-embedding-001 called with outputDimensionality 768 (see app/gemini.py).
    ADD COLUMN embedding_768 VECTOR(768),
    ADD COLUMN embedding_model TEXT,
    ADD CONSTRAINT embedding_has_model CHECK (embedding_768 IS NULL OR embedding_model IS NOT NULL);

CREATE INDEX evidence_chunks_search_en_idx ON evidence_chunks USING GIN (search_en);
CREATE INDEX evidence_chunks_search_ta_idx ON evidence_chunks USING GIN (search_ta);
CREATE INDEX evidence_chunks_embedding_idx ON evidence_chunks
    USING hnsw (embedding_768 vector_cosine_ops) WHERE active = TRUE;

-- Old and new names people use for a scheme (renames after the 2026 change of government).
CREATE TABLE scheme_aliases (
    scheme_id TEXT NOT NULL REFERENCES schemes(id),
    alias TEXT NOT NULL,
    language_code TEXT NOT NULL CHECK (language_code IN ('en', 'ta')),
    alias_type TEXT NOT NULL CHECK (alias_type IN ('official', 'former', 'reported', 'spelling')),
    PRIMARY KEY (scheme_id, alias)
);

CREATE INDEX scheme_aliases_lookup_idx ON scheme_aliases (lower(alias));

-- Mirrors app/changes.py. A 'reported' change (news only) must never be published as official.
CREATE TABLE scheme_changes (
    id TEXT PRIMARY KEY,
    scheme_id TEXT REFERENCES schemes(id),
    change_type TEXT NOT NULL CHECK (change_type IN ('rename', 'continuation', 'rate_revision', 'withdrawal', 'new')),
    evidence_status TEXT NOT NULL CHECK (evidence_status IN ('official', 'reported')),
    summary_en TEXT NOT NULL,
    summary_ta TEXT NOT NULL,
    source_title TEXT NOT NULL,
    source_url TEXT NOT NULL CHECK (source_url LIKE 'https://%'),
    government_order TEXT,
    checked_at DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX scheme_changes_recent_idx ON scheme_changes (checked_at DESC);

INSERT INTO schema_migrations (migration_version) VALUES ('0002_search_and_change_tracking');

COMMIT;
