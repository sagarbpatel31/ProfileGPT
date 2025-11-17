"""
Supabase client configuration and utilities
"""
from supabase import create_client, Client
from app.core.config import settings
import asyncio
from typing import Optional, List, Dict, Any

class SupabaseService:
    def __init__(self):
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key
        )

    async def create_tables(self):
        """
        Create the necessary tables and enable pgvector extension
        """
        # Enable pgvector extension
        await self._execute_sql("CREATE EXTENSION IF NOT EXISTS vector;")

        # Create tenants table
        tenants_sql = """
        CREATE TABLE IF NOT EXISTS tenants (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) NOT NULL,
            plan VARCHAR(50) DEFAULT 'free',
            theme JSONB DEFAULT '{}',
            api_key VARCHAR(255) UNIQUE NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        await self._execute_sql(tenants_sql)

        # Create documents table
        documents_sql = """
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
        """
        await self._execute_sql(documents_sql)

        # Create chunks table with vector embedding
        chunks_sql = """
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
        """
        await self._execute_sql(chunks_sql)

        # Create vector index for similarity search
        vector_index_sql = """
        CREATE INDEX IF NOT EXISTS chunks_embedding_idx
        ON chunks USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
        """
        await self._execute_sql(vector_index_sql)

        # Create skills table
        skills_sql = """
        CREATE TABLE IF NOT EXISTS skills (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            synonyms JSONB DEFAULT '[]',
            category VARCHAR(100),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        await self._execute_sql(skills_sql)

        # Create skill_evidence table
        skill_evidence_sql = """
        CREATE TABLE IF NOT EXISTS skill_evidence (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
            skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
            chunk_id UUID NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
            confidence FLOAT NOT NULL,
            context TEXT,
            last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        await self._execute_sql(skill_evidence_sql)

        # Create queries table
        queries_sql = """
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
        """
        await self._execute_sql(queries_sql)

        # Enable Row Level Security
        rls_sql = """
        ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
        ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
        ALTER TABLE chunks ENABLE ROW LEVEL SECURITY;
        ALTER TABLE skills ENABLE ROW LEVEL SECURITY;
        ALTER TABLE skill_evidence ENABLE ROW LEVEL SECURITY;
        ALTER TABLE queries ENABLE ROW LEVEL SECURITY;
        """
        await self._execute_sql(rls_sql)

    async def _execute_sql(self, sql: str):
        """Execute raw SQL"""
        result = self.client.rpc('exec_sql', {'sql': sql}).execute()
        return result

    async def similarity_search(
        self,
        embedding: List[float],
        tenant_id: str,
        limit: int = 8,
        threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search
        """
        result = self.client.rpc(
            'similarity_search',
            {
                'query_embedding': embedding,
                'match_tenant_id': tenant_id,
                'match_threshold': threshold,
                'match_count': limit
            }
        ).execute()

        return result.data

    async def create_tenant(self, name: str, api_key: str) -> str:
        """
        Create a new tenant
        """
        result = self.client.table('tenants').insert({
            'name': name,
            'api_key': api_key
        }).execute()

        return result.data[0]['id']

    async def store_chunk(
        self,
        tenant_id: str,
        doc_id: str,
        text: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> str:
        """
        Store a text chunk with its embedding
        """
        chunk_data = {
            'tenant_id': tenant_id,
            'doc_id': doc_id,
            'text': text,
            'embedding': embedding,
            'title': metadata.get('title'),
            'section': metadata.get('section'),
            'url_path': metadata.get('url_path'),
            'tags': metadata.get('tags', {}),
            'visibility': metadata.get('visibility', 'public')
        }

        result = self.client.table('chunks').insert(chunk_data).execute()
        return result.data[0]['id']

# Global instance
supabase_service = SupabaseService()