-- ProfileGPT Database Schema for Supabase
-- Run this in your Supabase SQL Editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Tenants table (for multi-tenant support)
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    settings JSONB DEFAULT '{}'::jsonb
);

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    source_type TEXT NOT NULL, -- 'resume', 'cover_letter', 'linkedin', 'github', 'portfolio', 'paper', 'misc'
    title TEXT NOT NULL,
    url TEXT,
    content TEXT,
    status TEXT DEFAULT 'processing', -- 'processing', 'completed', 'failed'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Chunks table with vector embeddings
CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    doc_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    source_type TEXT NOT NULL,
    title TEXT NOT NULL,
    section TEXT,
    url TEXT,
    text TEXT NOT NULL,
    embedding vector(384), -- Adjust dimension based on your embedding model
    tags JSONB DEFAULT '{}'::jsonb,
    visibility TEXT DEFAULT 'public', -- 'public', 'private'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Skills table
CREATE TABLE IF NOT EXISTS skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    synonyms TEXT[],
    category TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, name)
);

-- Skill evidence linking table
CREATE TABLE IF NOT EXISTS skill_evidence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    chunk_id UUID NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
    confidence FLOAT NOT NULL DEFAULT 0.0,
    evidence_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Query logs for analytics
CREATE TABLE IF NOT EXISTS query_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    mode TEXT DEFAULT 'detailed',
    latency_ms INTEGER,
    sources_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_feedback INTEGER, -- 1 for positive, -1 for negative, null for no feedback
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_chunks_tenant_id ON chunks(tenant_id);
CREATE INDEX IF NOT EXISTS idx_chunks_doc_id ON chunks(doc_id);
CREATE INDEX IF NOT EXISTS idx_chunks_source_type ON chunks(source_type);
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON chunks USING ivfflat (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_documents_tenant_id ON documents(tenant_id);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);

CREATE INDEX IF NOT EXISTS idx_skills_tenant_id ON skills(tenant_id);
CREATE INDEX IF NOT EXISTS idx_skill_evidence_tenant_id ON skill_evidence(tenant_id);
CREATE INDEX IF NOT EXISTS idx_skill_evidence_skill_id ON skill_evidence(skill_id);

CREATE INDEX IF NOT EXISTS idx_query_logs_tenant_id ON query_logs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_query_logs_created_at ON query_logs(created_at);

-- Enable Row Level Security
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE query_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies (Basic - customize based on your auth needs)
-- Allow users to access their own tenant data

CREATE POLICY "Tenant access policy" ON tenants FOR ALL USING (true); -- Adjust based on your auth
CREATE POLICY "Document access policy" ON documents FOR ALL USING (true);
CREATE POLICY "Chunk access policy" ON chunks FOR ALL USING (true);
CREATE POLICY "Skill access policy" ON skills FOR ALL USING (true);
CREATE POLICY "Skill evidence access policy" ON skill_evidence FOR ALL USING (true);
CREATE POLICY "Query log access policy" ON query_logs FOR ALL USING (true);

-- Create a default demo tenant
INSERT INTO tenants (id, name)
VALUES ('550e8400-e29b-41d4-a716-446655440000', 'Demo Tenant')
ON CONFLICT DO NOTHING;

-- Vector similarity search function
CREATE OR REPLACE FUNCTION match_chunks(
    query_embedding vector(384),
    match_tenant_id UUID,
    match_count int DEFAULT 5,
    filter jsonb DEFAULT '{}'
)
RETURNS TABLE (
    id UUID,
    tenant_id UUID,
    doc_id UUID,
    source_type TEXT,
    title TEXT,
    section TEXT,
    url TEXT,
    text TEXT,
    tags JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.tenant_id,
        c.doc_id,
        c.source_type,
        c.title,
        c.section,
        c.url,
        c.text,
        c.tags,
        1 - (c.embedding <=> query_embedding) AS similarity
    FROM chunks c
    WHERE c.tenant_id = match_tenant_id
    ORDER BY c.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Text search function for hybrid search
CREATE OR REPLACE FUNCTION search_chunks_text(
    search_query TEXT,
    match_tenant_id UUID,
    match_count int DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    tenant_id UUID,
    doc_id UUID,
    source_type TEXT,
    title TEXT,
    section TEXT,
    url TEXT,
    text TEXT,
    tags JSONB,
    rank FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.tenant_id,
        c.doc_id,
        c.source_type,
        c.title,
        c.section,
        c.url,
        c.text,
        c.tags,
        ts_rank_cd(to_tsvector('english', c.text), plainto_tsquery('english', search_query)) AS rank
    FROM chunks c
    WHERE c.tenant_id = match_tenant_id
    AND to_tsvector('english', c.text) @@ plainto_tsquery('english', search_query)
    ORDER BY rank DESC
    LIMIT match_count;
END;
$$;