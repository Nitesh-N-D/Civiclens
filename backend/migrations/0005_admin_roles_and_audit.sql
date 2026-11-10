-- CivicLens migration 0005: maintainer roles and an audit log (TD-09).
-- Additive only. Sign-in is Supabase Auth; this table decides what a signed-in account may do.
-- An account with no row here has no admin access at all, so leaving public sign-up open
-- grants nothing (it should still be disabled in the Supabase dashboard).

BEGIN;

CREATE TABLE admin_roles (
    user_id UUID PRIMARY KEY,               -- auth.users.id from Supabase Auth
    email TEXT NOT NULL,                    -- for people reading the audit log; not used to authorise
    role TEXT NOT NULL CHECK (role IN ('viewer', 'reviewer', 'maintainer')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Every admin change, with who made it and why. Rows are only ever inserted.
CREATE TABLE audit_log (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    actor_user_id UUID NOT NULL,
    actor_email TEXT NOT NULL,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    detail JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX audit_log_recent_idx ON audit_log (created_at DESC);

-- Same rule as 0003: nothing is readable through Supabase's public Data API.
ALTER TABLE admin_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

INSERT INTO schema_migrations (migration_version) VALUES ('0005_admin_roles_and_audit');

COMMIT;
