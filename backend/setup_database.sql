-- ProfileGPT Database Setup Script
-- Run this in your Supabase SQL Editor

-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create tenants table
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    plan VARCHAR(50) DEFAULT 'free',
    theme JSONB DEFAULT '{}',
    api_key VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create documents table
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    source_type VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    url TEXT,
    storage_key VARCHAR(500),
    status VARCHAR(50) DEFAULT 'processing',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create chunks table with vector embeddings
CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    doc_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    title VARCHAR(500),
    section VARCHAR(255),
    url_path TEXT,
    text TEXT NOT NULL,
    embedding vector(1536),  -- OpenAI text-embedding-3-large dimension
    tags JSONB DEFAULT '{}',
    visibility VARCHAR(20) DEFAULT 'public',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create vector similarity search index
CREATE INDEX IF NOT EXISTS chunks_embedding_idx
ON chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create tenant-based index for faster queries
CREATE INDEX IF NOT EXISTS chunks_tenant_idx ON chunks(tenant_id);
CREATE INDEX IF NOT EXISTS documents_tenant_idx ON documents(tenant_id);

-- Create skills table
CREATE TABLE IF NOT EXISTS skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    synonyms JSONB DEFAULT '[]',
    category VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create skill_evidence table for precomputed skill mappings
CREATE TABLE IF NOT EXISTS skill_evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    chunk_id UUID NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
    confidence FLOAT NOT NULL,
    context TEXT,
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create queries table for analytics
CREATE TABLE IF NOT EXISTS queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    top_chunks JSONB DEFAULT '[]',
    answer TEXT,
    mode VARCHAR(20) DEFAULT 'detailed',
    latency_ms INTEGER,
    feedback_score INTEGER CHECK (feedback_score >= 1 AND feedback_score <= 5),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security (RLS)
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE queries ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for tenant isolation
CREATE POLICY "Tenants can only see their own data" ON tenants FOR ALL USING (auth.uid()::text = id::text);
CREATE POLICY "Users can only see their tenant's documents" ON documents FOR ALL USING (tenant_id IN (SELECT id FROM tenants WHERE auth.uid()::text = id::text));
CREATE POLICY "Users can only see their tenant's chunks" ON chunks FOR ALL USING (tenant_id IN (SELECT id FROM tenants WHERE auth.uid()::text = id::text));
CREATE POLICY "Users can only see their tenant's skills" ON skills FOR ALL USING (tenant_id IN (SELECT id FROM tenants WHERE auth.uid()::text = id::text));
CREATE POLICY "Users can only see their tenant's skill_evidence" ON skill_evidence FOR ALL USING (tenant_id IN (SELECT id FROM tenants WHERE auth.uid()::text = id::text));
CREATE POLICY "Users can only see their tenant's queries" ON queries FOR ALL USING (tenant_id IN (SELECT id FROM tenants WHERE auth.uid()::text = id::text));

-- Create a function for vector similarity search
CREATE OR REPLACE FUNCTION similarity_search(
    query_embedding vector(1536),
    match_tenant_id uuid,
    match_threshold float DEFAULT 0.8,
    match_count int DEFAULT 8
)
RETURNS TABLE (
    id uuid,
    tenant_id uuid,
    doc_id uuid,
    title text,
    section text,
    url_path text,
    text text,
    tags jsonb,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        chunks.id,
        chunks.tenant_id,
        chunks.doc_id,
        chunks.title,
        chunks.section,
        chunks.url_path,
        chunks.text,
        chunks.tags,
        1 - (chunks.embedding <=> query_embedding) AS similarity
    FROM chunks
    WHERE chunks.tenant_id = match_tenant_id
        AND 1 - (chunks.embedding <=> query_embedding) > match_threshold
    ORDER BY chunks.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Insert a default tenant for development
INSERT INTO tenants (name, api_key)
VALUES ('Default Tenant', 'default-dev-key-' || gen_random_uuid())
ON CONFLICT (api_key) DO NOTHING;

-- Create some sample skills for the default tenant
INSERT INTO skills (tenant_id, name, synonyms, category)
SELECT
    (SELECT id FROM tenants WHERE api_key LIKE 'default-dev-key-%' LIMIT 1),
    skill_name,
    skill_synonyms::jsonb,
    skill_category
FROM (
    VALUES
        ('Python', '["Python", "py", "python3"]', 'Programming Languages'),
        ('JavaScript', '["JavaScript", "JS", "ECMAScript", "Node.js"]', 'Programming Languages'),
        ('React', '["React", "ReactJS", "React.js"]', 'Frontend Frameworks'),
        ('Machine Learning', '["ML", "Machine Learning", "AI", "Artificial Intelligence"]', 'Technologies'),
        ('PostgreSQL', '["PostgreSQL", "Postgres", "psql"]', 'Databases'),
        ('Docker', '["Docker", "Containerization", "Containers"]', 'DevOps'),
        ('AWS', '["AWS", "Amazon Web Services", "Amazon Cloud"]', 'Cloud Platforms'),
        ('Git', '["Git", "Version Control", "GitHub", "GitLab"]', 'Tools')
) AS skills_data(skill_name, skill_synonyms, skill_category)
ON CONFLICT DO NOTHING;