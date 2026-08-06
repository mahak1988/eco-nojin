-- Phase 5: content version history
-- Run once on the application database (PostgreSQL)

CREATE TABLE IF NOT EXISTS content_versions (
    id SERIAL PRIMARY KEY,
    content_type VARCHAR(64) NOT NULL,
    content_id INTEGER NOT NULL,
    version_number INTEGER NOT NULL DEFAULT 1,
    content_data TEXT NOT NULL DEFAULT '{}',
    created_by INTEGER NULL,
    approved_by INTEGER NULL,
    approved_at TIMESTAMPTZ NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_content_versions_type ON content_versions (content_type);
CREATE INDEX IF NOT EXISTS ix_content_versions_content_id ON content_versions (content_id);
CREATE INDEX IF NOT EXISTS ix_content_versions_type_id ON content_versions (content_type, content_id);
