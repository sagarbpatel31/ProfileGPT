"""
Database models and operations for ProfileGPT
"""
import sqlite3
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import os

@dataclass
class Chunk:
    id: str
    tenant_id: str
    doc_id: str
    source_type: str
    title: str
    section: str
    url: Optional[str]
    text: str
    embedding: Optional[np.ndarray]
    tags: Dict[str, Any]
    visibility: str = "public"

@dataclass
class Document:
    id: str
    tenant_id: str
    source_type: str
    title: str
    url: Optional[str]
    content: str
    status: str
    created_at: datetime

class DatabaseManager:
    def __init__(self, db_path: str = "profilegpt.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize SQLite database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Tenants table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tenants (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            api_key TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Documents table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            source_type TEXT NOT NULL,
            title TEXT NOT NULL,
            url TEXT,
            content TEXT,
            status TEXT DEFAULT 'processing',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        )
        ''')

        # Chunks table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chunks (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            doc_id TEXT NOT NULL,
            source_type TEXT NOT NULL,
            title TEXT NOT NULL,
            section TEXT,
            url TEXT,
            text TEXT NOT NULL,
            embedding BLOB,
            tags TEXT,
            visibility TEXT DEFAULT 'public',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tenant_id) REFERENCES tenants (id),
            FOREIGN KEY (doc_id) REFERENCES documents (id)
        )
        ''')

        # Skills table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS skills (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            name TEXT NOT NULL,
            synonyms TEXT,
            category TEXT,
            FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        )
        ''')

        # Skills evidence table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS skill_evidence (
            skill_id TEXT NOT NULL,
            chunk_id TEXT NOT NULL,
            confidence REAL DEFAULT 0.5,
            evidence_text TEXT,
            PRIMARY KEY (skill_id, chunk_id),
            FOREIGN KEY (skill_id) REFERENCES skills (id),
            FOREIGN KEY (chunk_id) REFERENCES chunks (id)
        )
        ''')

        # Query logs table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS queries (
            id TEXT PRIMARY KEY,
            tenant_id TEXT,
            question TEXT NOT NULL,
            answer TEXT,
            mode TEXT,
            latency_ms INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        )
        ''')

        # Create default tenant for demo
        cursor.execute('''
        INSERT OR IGNORE INTO tenants (id, name, email, api_key)
        VALUES ('demo-tenant', 'Demo User', 'demo@profilegpt.com', 'pk_demo_123')
        ''')

        conn.commit()
        conn.close()

    def add_document(self, doc: Document) -> str:
        """Add a new document to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
        INSERT INTO documents (id, tenant_id, source_type, title, url, content, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (doc.id, doc.tenant_id, doc.source_type, doc.title, doc.url, doc.content, doc.status))

        conn.commit()
        conn.close()
        return doc.id

    def add_chunk(self, chunk: Chunk) -> str:
        """Add a new text chunk to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()

        embedding_blob = None
        if chunk.embedding is not None:
            embedding_blob = chunk.embedding.tobytes()

        cursor.execute('''
        INSERT INTO chunks (id, tenant_id, doc_id, source_type, title, section, url, text, embedding, tags, visibility)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (chunk.id, chunk.tenant_id, chunk.doc_id, chunk.source_type, chunk.title,
              chunk.section, chunk.url, chunk.text, embedding_blob, json.dumps(chunk.tags), chunk.visibility))

        conn.commit()
        conn.close()
        return chunk.id

    def search_chunks_by_text(self, query: str, tenant_id: str, limit: int = 5) -> List[Chunk]:
        """Simple text search for chunks (BM25-like)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Simple LIKE search - in production would use FTS5
        cursor.execute('''
        SELECT * FROM chunks
        WHERE tenant_id = ? AND text LIKE ?
        ORDER BY length(text) DESC
        LIMIT ?
        ''', (tenant_id, f'%{query}%', limit))

        rows = cursor.fetchall()
        chunks = []

        for row in rows:
            embedding = None
            if row['embedding']:
                embedding = np.frombuffer(row['embedding'], dtype=np.float32)

            chunks.append(Chunk(
                id=row['id'],
                tenant_id=row['tenant_id'],
                doc_id=row['doc_id'],
                source_type=row['source_type'],
                title=row['title'],
                section=row['section'],
                url=row['url'],
                text=row['text'],
                embedding=embedding,
                tags=json.loads(row['tags'] or '{}'),
                visibility=row['visibility']
            ))

        conn.close()
        return chunks

    def get_tenant_documents(self, tenant_id: str) -> List[Document]:
        """Get all documents for a tenant"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM documents WHERE tenant_id = ? ORDER BY created_at DESC', (tenant_id,))
        rows = cursor.fetchall()

        documents = []
        for row in rows:
            documents.append(Document(
                id=row['id'],
                tenant_id=row['tenant_id'],
                title=row['title'],
                source_type=row['source_type'],
                url=row['url'],
                content=row['content'],
                status=row['status'],
                created_at=datetime.fromisoformat(row['created_at'])
            ))

        conn.close()
        return documents

    def get_document_chunks(self, doc_id: str) -> List[Chunk]:
        """Get all chunks for a document"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM chunks WHERE doc_id = ?', (doc_id,))
        rows = cursor.fetchall()

        chunks = []
        for row in rows:
            embedding = None
            if row['embedding']:
                embedding = np.frombuffer(row['embedding'], dtype=np.float32)

            chunks.append(Chunk(
                id=row['id'],
                tenant_id=row['tenant_id'],
                doc_id=row['doc_id'],
                source_type=row['source_type'],
                title=row['title'],
                section=row['section'],
                url=row['url'],
                text=row['text'],
                embedding=embedding,
                tags=json.loads(row['tags'] or '{}'),
                visibility=row['visibility']
            ))

        conn.close()
        return chunks

    def delete_document(self, document_id: str):
        """Delete a document"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM documents WHERE id = ?', (document_id,))
        conn.commit()
        conn.close()

    def delete_document_chunks(self, document_id: str):
        """Delete all chunks for a document"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM chunks WHERE doc_id = ?', (document_id,))
        conn.commit()
        conn.close()

    def get_skill_evidence(self, skill_name: str, tenant_id: str) -> Dict[str, Any]:
        """Get evidence for a specific skill"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Find skill by name (case insensitive)
        cursor.execute('''
        SELECT s.id, se.chunk_id, se.confidence, se.evidence_text, c.text, c.title, c.section, c.url
        FROM skills s
        JOIN skill_evidence se ON s.id = se.skill_id
        JOIN chunks c ON se.chunk_id = c.id
        WHERE s.tenant_id = ? AND LOWER(s.name) = LOWER(?)
        ORDER BY se.confidence DESC
        ''', (tenant_id, skill_name))

        rows = cursor.fetchall()

        if not rows:
            # Check if skill exists in text (fallback)
            chunks = self.search_chunks_by_text(skill_name, tenant_id, 3)
            evidence = []
            for chunk in chunks:
                if skill_name.lower() in chunk.text.lower():
                    evidence.append({
                        'text': chunk.text[:200] + '...',
                        'title': chunk.title,
                        'section': chunk.section,
                        'url': chunk.url
                    })

            conn.close()
            return {
                'has_skill': len(evidence) > 0,
                'confidence': 0.6 if evidence else 0.0,
                'evidence': evidence
            }

        evidence = []
        total_confidence = 0

        for row in rows:
            evidence.append({
                'text': row['evidence_text'] or row['text'][:200] + '...',
                'title': row['title'],
                'section': row['section'],
                'url': row['url']
            })
            total_confidence += row['confidence']

        conn.close()

        avg_confidence = total_confidence / len(rows) if rows else 0

        return {
            'has_skill': avg_confidence > 0.3,
            'confidence': avg_confidence,
            'evidence': evidence[:3]  # Top 3 pieces of evidence
        }

    def log_query(self, tenant_id: str, question: str, answer: str, mode: str, latency_ms: int) -> str:
        """Log a query for analytics"""
        import uuid
        query_id = str(uuid.uuid4())

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
        INSERT INTO queries (id, tenant_id, question, answer, mode, latency_ms)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (query_id, tenant_id, question, answer, mode, latency_ms))

        conn.commit()
        conn.close()
        return query_id