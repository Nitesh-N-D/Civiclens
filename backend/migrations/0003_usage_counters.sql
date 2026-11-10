-- CivicLens migration 0003: persistent daily Gemini budget.
-- Stores one aggregate counter per UTC day and bucket. No IP address, question text or any
-- other visitor data is stored. Additive only.

BEGIN;

CREATE TABLE api_usage_daily (
    usage_day DATE NOT NULL,
    bucket TEXT NOT NULL CHECK (bucket IN ('gemini')),
    request_count INTEGER NOT NULL DEFAULT 0 CHECK (request_count >= 0),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (usage_day, bucket)
);

-- Supabase exposes the public schema through its Data API (anon/authenticated roles). CivicLens
-- only connects as the database owner from the server, so enable RLS with no policies: the Data
-- API can then read or write nothing, while the server connection is unaffected.
DO $$
DECLARE t TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY[
        'schema_migrations', 'sources', 'source_versions', 'documents', 'evidence_chunks', 'schemes',
        'scheme_claims', 'claim_evidence', 'eligibility_rules', 'source_checks', 'feedback_reports',
        'review_events', 'scheme_aliases', 'scheme_changes', 'api_usage_daily'
    ] LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', t);
    END LOOP;
END $$;

INSERT INTO schema_migrations (migration_version) VALUES ('0003_usage_counters');

COMMIT;
