-- Ask Greece for Business — database schema (MVP)
-- Single core table + PostgreSQL full-text search.

CREATE EXTENSION IF NOT EXISTS unaccent;

DROP TABLE IF EXISTS decisions;

CREATE TABLE decisions (
    id              BIGSERIAL PRIMARY KEY,
    ada             TEXT UNIQUE NOT NULL,      -- Diavgeia unique id (used as citation)
    subject         TEXT NOT NULL,             -- "θέμα" / decision subject
    organization    TEXT NOT NULL,             -- issuing body (municipality)
    decision_type   TEXT,                      -- e.g. ΠΡΟΜΗΘΕΙΑ / ΑΝΑΘΕΣΗ
    issue_date      DATE,
    amount          NUMERIC,                   -- nullable
    currency        TEXT DEFAULT 'EUR',
    document_url    TEXT,                      -- link to original decision
    raw             JSONB,                     -- full payload (backup)
    search_vector   tsvector
);

-- Indexes
CREATE INDEX idx_decisions_search ON decisions USING GIN (search_vector);
CREATE INDEX idx_decisions_org    ON decisions (organization);
CREATE INDEX idx_decisions_date   ON decisions (issue_date DESC);
CREATE INDEX idx_decisions_amount ON decisions (amount DESC NULLS LAST);

-- Keep search_vector in sync automatically.
-- 'simple' config + unaccent gives accent-insensitive matching without a
-- Greek stemmer dependency (simplest reliable option for the demo).
CREATE OR REPLACE FUNCTION decisions_search_vector_update()
RETURNS trigger AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('simple', unaccent(coalesce(NEW.subject, ''))), 'A') ||
        setweight(to_tsvector('simple', unaccent(coalesce(NEW.organization, ''))), 'B') ||
        setweight(to_tsvector('simple', unaccent(coalesce(NEW.decision_type, ''))), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_decisions_search_vector
BEFORE INSERT OR UPDATE ON decisions
FOR EACH ROW EXECUTE FUNCTION decisions_search_vector_update();
