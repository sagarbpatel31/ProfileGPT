"""
Supabase Database Manager for ProfileGPT
Replaces local SQLite with cloud Postgres + pgvector
"""
import os
import uuid
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import json
import numpy as np
from supabase import create_client, Client

@dataclass
class Document:
    id: str
    tenant_id: str
    source_type: str
    title: str
    url: Optional[str]
    content: str
    status: str
    created_at: float
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class Chunk:
    id: str
    tenant_id: str
    doc_id: str
    source_type: str
    title: str
    section: Optional[str]
    url: Optional[str]
    text: str
    embedding: Optional[np.ndarray]
    tags: Optional[Dict[str, Any]] = None
    visibility: str = "public"

class SupabaseDatabaseManager:
    def __init__(self):
        supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

        if not supabase_url or not supabase_key:
            raise ValueError("Missing Supabase environment variables")

        self.client: Client = create_client(supabase_url, supabase_key)
        self.default_tenant_id = "550e8400-e29b-41d4-a716-446655440000"  # Demo tenant

    def ensure_tenant(self, tenant_id: str = None) -> str:
        """Ensure tenant exists, create if not, return tenant_id"""
        if not tenant_id:
            tenant_id = self.default_tenant_id

        result = self.client.table("tenants").select("id").eq("id", tenant_id).execute()

        if not result.data:
            # Create tenant
            tenant_data = {
                "id": tenant_id,
                "name": "Demo Tenant" if tenant_id == self.default_tenant_id else f"Tenant {tenant_id[:8]}",
                "settings": {}
            }
            self.client.table("tenants").insert(tenant_data).execute()

        return tenant_id

    def add_document(self, doc: Document):
        """Add a document to Supabase"""
        self.ensure_tenant(doc.tenant_id)

        doc_data = {
            "id": doc.id,
            "tenant_id": doc.tenant_id,
            "source_type": doc.source_type,
            "title": doc.title,
            "url": doc.url,
            "content": doc.content,
            "status": doc.status,
            "metadata": doc.metadata or {}
        }

        result = self.client.table("documents").insert(doc_data).execute()
        if result.data:
            print(f"✅ Document {doc.id} added to Supabase")

    def add_chunk(self, chunk: Chunk):
        """Add a chunk with embedding to Supabase"""
        self.ensure_tenant(chunk.tenant_id)

        # Convert numpy array to list for JSON serialization
        embedding_list = chunk.embedding.tolist() if chunk.embedding is not None else None

        chunk_data = {
            "id": chunk.id,
            "tenant_id": chunk.tenant_id,
            "doc_id": chunk.doc_id,
            "source_type": chunk.source_type,
            "title": chunk.title,
            "section": chunk.section,
            "url": chunk.url,
            "text": chunk.text,
            "embedding": embedding_list,
            "tags": chunk.tags or {},
            "visibility": chunk.visibility
        }

        result = self.client.table("chunks").insert(chunk_data).execute()
        if result.data:
            print(f"✅ Chunk {chunk.id} added to Supabase")

    def get_tenant_documents(self, tenant_id: str) -> List[Document]:
        """Get all documents for a tenant"""
        result = self.client.table("documents").select("*").eq("tenant_id", tenant_id).execute()

        documents = []
        for row in result.data:
            doc = Document(
                id=row["id"],
                tenant_id=row["tenant_id"],
                source_type=row["source_type"],
                title=row["title"],
                url=row["url"],
                content=row["content"],
                status=row["status"],
                created_at=time.time(),  # Approximate
                metadata=row.get("metadata", {})
            )
            documents.append(doc)

        return documents

    def get_document_chunks(self, doc_id: str) -> List[Chunk]:
        """Get all chunks for a document"""
        result = self.client.table("chunks").select("*").eq("doc_id", doc_id).execute()

        chunks = []
        for row in result.data:
            # Convert embedding back to numpy array
            embedding = np.array(row["embedding"]) if row["embedding"] else None

            chunk = Chunk(
                id=row["id"],
                tenant_id=row["tenant_id"],
                doc_id=row["doc_id"],
                source_type=row["source_type"],
                title=row["title"],
                section=row["section"],
                url=row["url"],
                text=row["text"],
                embedding=embedding,
                tags=row.get("tags", {}),
                visibility=row.get("visibility", "public")
            )
            chunks.append(chunk)

        return chunks

    def search_chunks_by_embedding(self, query_embedding: np.ndarray, tenant_id: str, top_k: int = 5) -> List[Tuple[Chunk, float]]:
        """Vector similarity search using Supabase function"""
        try:
            # Call the match_chunks function
            result = self.client.rpc(
                'match_chunks',
                {
                    'query_embedding': query_embedding.tolist(),
                    'match_tenant_id': tenant_id,
                    'match_count': top_k
                }
            ).execute()

            scored_chunks = []
            for row in result.data:
                embedding = np.array(row["embedding"]) if row.get("embedding") else None

                chunk = Chunk(
                    id=row["id"],
                    tenant_id=row["tenant_id"],
                    doc_id=row["doc_id"],
                    source_type=row["source_type"],
                    title=row["title"],
                    section=row["section"],
                    url=row["url"],
                    text=row["text"],
                    embedding=embedding,
                    tags=row.get("tags", {}),
                    visibility=row.get("visibility", "public")
                )

                similarity = row.get("similarity", 0.0)
                scored_chunks.append((chunk, similarity))

            return scored_chunks

        except Exception as e:
            print(f"⚠️ Vector search failed: {e}")
            return []

    def search_chunks_by_text(self, query: str, tenant_id: str, top_k: int = 10) -> List[Chunk]:
        """Text-based search using Supabase full-text search"""
        try:
            # Use the text search function
            result = self.client.rpc(
                'search_chunks_text',
                {
                    'search_query': query,
                    'match_tenant_id': tenant_id,
                    'match_count': top_k
                }
            ).execute()

            chunks = []
            for row in result.data:
                embedding = np.array(row["embedding"]) if row.get("embedding") else None

                chunk = Chunk(
                    id=row["id"],
                    tenant_id=row["tenant_id"],
                    doc_id=row["doc_id"],
                    source_type=row["source_type"],
                    title=row["title"],
                    section=row["section"],
                    url=row["url"],
                    text=row["text"],
                    embedding=embedding,
                    tags=row.get("tags", {}),
                    visibility=row.get("visibility", "public")
                )
                chunks.append(chunk)

            return chunks

        except Exception as e:
            print(f"⚠️ Text search failed: {e}")
            # Fallback to simple text matching
            result = self.client.table("chunks").select("*").eq("tenant_id", tenant_id).ilike("text", f"%{query}%").limit(top_k).execute()

            chunks = []
            for row in result.data:
                embedding = np.array(row["embedding"]) if row.get("embedding") else None

                chunk = Chunk(
                    id=row["id"],
                    tenant_id=row["tenant_id"],
                    doc_id=row["doc_id"],
                    source_type=row["source_type"],
                    title=row["title"],
                    section=row["section"],
                    url=row["url"],
                    text=row["text"],
                    embedding=embedding,
                    tags=row.get("tags", {}),
                    visibility=row.get("visibility", "public")
                )
                chunks.append(chunk)

            return chunks

    def get_skill_evidence(self, skill_name: str, tenant_id: str) -> Dict[str, Any]:
        """Get evidence for a specific skill"""
        # Search for chunks containing the skill
        chunks = self.search_chunks_by_text(skill_name, tenant_id, 5)

        if not chunks:
            return {"has_skill": False, "confidence": 0.0, "evidence": []}

        evidence = []
        total_confidence = 0.0

        for chunk in chunks:
            # Calculate confidence based on mentions
            text_lower = chunk.text.lower()
            skill_lower = skill_name.lower()

            if skill_lower in text_lower:
                confidence = 0.7  # Base confidence

                # Boost for experience indicators
                if any(phrase in text_lower for phrase in ['experience', 'expert', 'proficient', 'years']):
                    confidence += 0.2

                # Boost for project context
                if any(phrase in text_lower for phrase in ['built', 'developed', 'project', 'implemented']):
                    confidence += 0.1

                confidence = min(confidence, 1.0)
                total_confidence += confidence

                evidence.append({
                    "chunk_id": chunk.id,
                    "title": chunk.title,
                    "section": chunk.section,
                    "source_type": chunk.source_type,
                    "text": chunk.text,
                    "url": chunk.url,
                    "confidence": confidence
                })

        avg_confidence = total_confidence / len(evidence) if evidence else 0.0

        return {
            "has_skill": len(evidence) > 0,
            "confidence": avg_confidence,
            "evidence": evidence[:3]  # Top 3 pieces of evidence
        }

    def get_tenant_skill_names(self, tenant_id: str) -> List[str]:
        """Get all skill names for a tenant"""
        result = self.client.table("skills").select("name").eq("tenant_id", tenant_id).execute()
        return [row["name"] for row in result.data]

    def log_query(self, tenant_id: str, question: str, answer: str, mode: str, latency_ms: int):
        """Log a query for analytics"""
        self.ensure_tenant(tenant_id)

        log_data = {
            "tenant_id": tenant_id,
            "question": question,
            "answer": answer,
            "mode": mode,
            "latency_ms": latency_ms,
            "sources_count": 0,  # Could be calculated from citations
            "metadata": {}
        }

        self.client.table("query_logs").insert(log_data).execute()

    def get_chunk_by_id(self, chunk_id: str) -> Optional[Chunk]:
        """Get a specific chunk by ID"""
        result = self.client.table("chunks").select("*").eq("id", chunk_id).execute()

        if not result.data:
            return None

        row = result.data[0]
        embedding = np.array(row["embedding"]) if row["embedding"] else None

        return Chunk(
            id=row["id"],
            tenant_id=row["tenant_id"],
            doc_id=row["doc_id"],
            source_type=row["source_type"],
            title=row["title"],
            section=row["section"],
            url=row["url"],
            text=row["text"],
            embedding=embedding,
            tags=row.get("tags", {}),
            visibility=row.get("visibility", "public")
        )

    def update_document_status(self, doc_id: str, status: str):
        """Update document processing status"""
        self.client.table("documents").update({"status": status}).eq("id", doc_id).execute()

    def delete_document(self, doc_id: str):
        """Delete a document and its chunks"""
        # Delete chunks first (cascade should handle this, but being explicit)
        self.client.table("chunks").delete().eq("doc_id", doc_id).execute()
        # Delete document
        self.client.table("documents").delete().eq("id", doc_id).execute()

    def get_tenant_stats(self, tenant_id: str) -> Dict[str, Any]:
        """Get statistics for a tenant"""
        docs_result = self.client.table("documents").select("id", count="exact").eq("tenant_id", tenant_id).execute()
        chunks_result = self.client.table("chunks").select("id", count="exact").eq("tenant_id", tenant_id).execute()
        queries_result = self.client.table("query_logs").select("id", count="exact").eq("tenant_id", tenant_id).execute()

        return {
            "documents": docs_result.count or 0,
            "chunks": chunks_result.count or 0,
            "queries": queries_result.count or 0
        }