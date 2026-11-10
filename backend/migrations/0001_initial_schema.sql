-- CivicLens migration 0001: source registry, evidence and review schema.
-- Applied by scripts/migrate.py (never by the API at runtime). Apply to a fresh database.

BEGIN;

CREATE TABLE schema_migrations (
    migration_version TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE sources (
    id TEXT PRIMARY KEY,
    owner TEXT NOT NULL,
    jurisdiction TEXT NOT NULL,
    canonical_url TEXT NOT NULL,
    source_type TEXT NOT NULL,
    language_codes TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    access_method TEXT NOT NULL,
    access_terms_status TEXT NOT NULL DEFAULT 'not_verified',
    active BOOLEAN NOT NULL DEFAULT TRUE,
    review_due_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT sources_url_https CHECK (canonical_url LIKE 'https://%')
);

CREATE TABLE source_versions (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id TEXT NOT NULL REFERENCES sources(id),
    document_number TEXT,
    publication_date DATE,
    effective_from DATE,
    effective_to DATE,
    fetched_at TIMESTAMPTZ,
    content_hash TEXT,
    review_status TEXT NOT NULL DEFAULT 'discovered'
        CHECK (review_status IN ('discovered', 'terms_pending', 'review_pending', 'approved', 'contested', 'retired')),
    human_verified_at TIMESTAMPTZ,
    reviewer TEXT,
    review_note TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT verified_version_has_reviewer CHECK (
        review_status <> 'approved' OR (human_verified_at IS NOT NULL AND reviewer IS NOT NULL)
    )
);

CREATE INDEX source_versions_source_recent_idx ON source_versions(source_id, created_at DESC);
CREATE INDEX source_versions_review_status_idx ON source_versions(review_status, created_at DESC);

CREATE TABLE documents (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    version_id BIGINT NOT NULL REFERENCES source_versions(id),
    title TEXT NOT NULL,
    canonical_url TEXT NOT NULL,
    media_type TEXT NOT NULL,
    language_code TEXT NOT NULL CHECK (language_code IN ('en', 'ta')),
    locator_scheme TEXT NOT NULL DEFAULT 'section_or_page',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE evidence_chunks (
    id TEXT PRIMARY KEY,
    document_id BIGINT NOT NULL REFERENCES documents(id),
    locator TEXT NOT NULL,
    text_en TEXT,
    text_ta TEXT,
    embedding JSONB,
    active BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (text_en IS NOT NULL OR text_ta IS NOT NULL),
    CHECK (embedding IS NULL OR jsonb_typeof(embedding) = 'array')
);

CREATE INDEX evidence_chunks_document_idx ON evidence_chunks(document_id);
CREATE INDEX evidence_chunks_active_idx ON evidence_chunks(active) WHERE active = TRUE;

CREATE TABLE schemes (
    id TEXT PRIMARY KEY,
    name_en TEXT NOT NULL,
    name_ta TEXT,
    department TEXT NOT NULL,
    jurisdiction TEXT NOT NULL,
    category TEXT NOT NULL,
    official_route_url TEXT,
    publication_status TEXT NOT NULL DEFAULT 'discovery_only'
        CHECK (publication_status IN ('discovery_only', 'review_pending', 'published', 'retired')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT scheme_route_https CHECK (official_route_url IS NULL OR official_route_url LIKE 'https://%')
);

CREATE TABLE scheme_claims (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    scheme_id TEXT NOT NULL REFERENCES schemes(id),
    claim_type TEXT NOT NULL CHECK (
        claim_type IN ('summary', 'benefit', 'eligibility', 'document', 'application_step', 'deadline', 'contact')
    ),
    language_code TEXT NOT NULL CHECK (language_code IN ('en', 'ta')),
    claim_text TEXT NOT NULL,
    publication_status TEXT NOT NULL DEFAULT 'review_pending'
        CHECK (publication_status IN ('review_pending', 'published', 'contested', 'retired')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE claim_evidence (
    claim_id BIGINT NOT NULL REFERENCES scheme_claims(id),
    evidence_chunk_id TEXT NOT NULL REFERENCES evidence_chunks(id),
    PRIMARY KEY (claim_id, evidence_chunk_id)
);

CREATE TABLE eligibility_rules (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    scheme_id TEXT NOT NULL REFERENCES schemes(id),
    rule_code TEXT NOT NULL,
    question_code TEXT NOT NULL,
    comparison_operator TEXT NOT NULL CHECK (comparison_operator IN ('eq', 'neq', 'gte', 'lte', 'in', 'not_in', 'exists')),
    expected_value JSONB NOT NULL,
    evidence_chunk_id TEXT NOT NULL REFERENCES evidence_chunks(id),
    review_status TEXT NOT NULL DEFAULT 'draft'
        CHECK (review_status IN ('draft', 'review_pending', 'approved', 'retired')),
    human_verified_at TIMESTAMPTZ,
    reviewer TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (scheme_id, rule_code),
    CONSTRAINT approved_rule_has_review CHECK (
        review_status <> 'approved' OR (human_verified_at IS NOT NULL AND reviewer IS NOT NULL)
    )
);

CREATE TABLE source_checks (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id TEXT NOT NULL REFERENCES sources(id),
    checked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    outcome TEXT NOT NULL CHECK (outcome IN ('reachable', 'changed', 'unreachable', 'manual_review')),
    response_status SMALLINT,
    content_hash TEXT,
    note TEXT
);

CREATE INDEX source_checks_recent_idx ON source_checks(source_id, checked_at DESC);

CREATE TABLE feedback_reports (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    scheme_id TEXT REFERENCES schemes(id),
    source_id TEXT REFERENCES sources(id),
    category TEXT NOT NULL CHECK (category IN ('stale', 'unclear', 'broken_link', 'missing_topic', 'other')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    review_status TEXT NOT NULL DEFAULT 'new'
        CHECK (review_status IN ('new', 'reviewing', 'resolved', 'dismissed')),
    resolution_note TEXT,
    CHECK (scheme_id IS NOT NULL OR source_id IS NOT NULL)
);

CREATE TABLE review_events (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    entity_type TEXT NOT NULL CHECK (entity_type IN ('source', 'source_version', 'scheme', 'claim', 'eligibility_rule')),
    entity_id TEXT NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('created', 'approved', 'contested', 'published', 'retired', 'updated')),
    actor TEXT NOT NULL,
    rationale TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX review_events_entity_idx ON review_events(entity_type, entity_id, created_at DESC);

-- Deliberately no citizen profiles, uploaded-document table, raw chat history, or identity fields.

INSERT INTO schema_migrations (migration_version) VALUES ('0001_initial_schema');

COMMIT;
