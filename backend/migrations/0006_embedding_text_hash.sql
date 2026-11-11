-- CivicLens migration 0006: record which text each stored embedding was made from.
-- Additive only. The API uses a stored vector only when this hash matches the chunk's current
-- text and embedding_model matches GEMINI_EMBEDDING_MODEL, so an edited chunk is never matched
-- against a stale vector. Filled by scripts/embed_corpus.py.

BEGIN;

ALTER TABLE evidence_chunks ADD COLUMN embedding_text_hash TEXT;

INSERT INTO schema_migrations (migration_version) VALUES ('0006_embedding_text_hash');

COMMIT;
