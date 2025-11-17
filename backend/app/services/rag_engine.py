"""
RAG (Retrieval-Augmented Generation) Engine
Implements hybrid search + reranking + LLM generation
"""
import openai
from typing import List, Dict, Any, Optional, Tuple
from app.services.supabase_client import supabase_service
from app.services.embeddings import embedding_service
from app.core.config import settings
import asyncio
import time
from langfuse import Langfuse
from langfuse.decorators import observe

# Initialize Langfuse for observability
langfuse = Langfuse(
    secret_key=settings.langfuse_secret_key,
    public_key=settings.langfuse_public_key,
    host=settings.langfuse_host
) if settings.langfuse_secret_key else None

class RAGEngine:
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

    @observe(name="rag_query")
    async def answer_question(
        self,
        question: str,
        tenant_id: str,
        mode: str = "detailed",
        max_chunks: int = None
    ) -> Dict[str, Any]:
        """
        Main RAG pipeline: retrieve + rerank + generate
        """
        start_time = time.time()

        # Step 1: Retrieve relevant chunks using hybrid search
        chunks = await self._retrieve_chunks(question, tenant_id, max_chunks or settings.max_retrieval_chunks)

        # Step 2: Rerank chunks if enabled
        if settings.enable_reranking and len(chunks) > 3:
            chunks = await self._rerank_chunks(question, chunks)

        # Step 3: Generate answer using LLM
        answer, citations = await self._generate_answer(question, chunks, mode)

        latency_ms = int((time.time() - start_time) * 1000)

        # Log query for analytics
        await self._log_query(tenant_id, question, chunks, answer, mode, latency_ms)

        return {
            "answer": answer,
            "citations": citations,
            "sources": self._format_sources(chunks),
            "latency_ms": latency_ms,
            "mode": mode
        }

    async def _retrieve_chunks(
        self,
        question: str,
        tenant_id: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search: semantic similarity + keyword matching
        """
        # Generate query embedding
        query_embedding = await embedding_service.embed_text(question)

        # Semantic search using vector similarity
        semantic_chunks = await supabase_service.similarity_search(
            embedding=query_embedding,
            tenant_id=tenant_id,
            limit=limit * 2,  # Get more for reranking
            threshold=0.7
        )

        # TODO: Implement BM25 keyword search and combine with semantic results
        # For now, just return semantic results
        return semantic_chunks[:limit]

    async def _rerank_chunks(
        self,
        question: str,
        chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Rerank chunks using cross-encoder model
        TODO: Implement cross-encoder reranking
        """
        # For now, return chunks as-is
        # In production, use sentence-transformers cross-encoder
        return chunks

    async def _generate_answer(
        self,
        question: str,
        chunks: List[Dict[str, Any]],
        mode: str
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Generate answer using LLM with retrieved context
        """
        # Build context from chunks
        context_parts = []
        citations = []

        for i, chunk in enumerate(chunks):
            context_parts.append(f"[{i+1}] {chunk['text']}")
            citations.append({
                "index": i + 1,
                "title": chunk.get('title', 'Unknown'),
                "section": chunk.get('section'),
                "url": chunk.get('url_path'),
                "chunk_id": chunk['id']
            })

        context = "\n\n".join(context_parts)

        # Build prompt based on mode
        system_prompt = self._get_system_prompt(mode)
        user_prompt = f"""Question: {question}

Retrieved Information:
{context}

Please answer the question using ONLY the information provided above. Include citation numbers [1], [2], etc. when referencing specific information."""

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Using cost-effective model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=1000 if mode == "detailed" else 500
            )

            answer = response.choices[0].message.content
            return answer, citations

        except Exception as e:
            return f"I apologize, but I encountered an error generating a response: {str(e)}", []

    def _get_system_prompt(self, mode: str) -> str:
        """
        Get system prompt based on response mode
        """
        base_prompt = """You are ProfileGPT, an AI assistant that helps recruiters and collaborators understand a professional profile. Answer questions truthfully based only on the retrieved information provided.

Rules:
1. Use ONLY the information in the retrieved context
2. If information is not available, say "I don't have that information" or "I'm not sure about that"
3. Always include citation numbers [1], [2], etc. when referencing information
4. Be honest about limitations
5. Don't make up or infer information not explicitly stated"""

        if mode == "short":
            return f"{base_prompt}\n\nProvide concise, direct answers (1-2 sentences maximum)."
        elif mode == "star":
            return f"{base_prompt}\n\nWhen describing experiences or projects, use the STAR method (Situation, Task, Action, Result) when the information is available."
        else:  # detailed
            return f"{base_prompt}\n\nProvide comprehensive, detailed answers with full context and explanations."

    def _format_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format source information for frontend display
        """
        sources = []
        for chunk in chunks:
            sources.append({
                "chunk_id": chunk['id'],
                "title": chunk.get('title', 'Unknown Source'),
                "section": chunk.get('section'),
                "url": chunk.get('url_path'),
                "text_preview": chunk['text'][:200] + "..." if len(chunk['text']) > 200 else chunk['text']
            })
        return sources

    async def _log_query(
        self,
        tenant_id: str,
        question: str,
        chunks: List[Dict[str, Any]],
        answer: str,
        mode: str,
        latency_ms: int
    ):
        """
        Log query for analytics and improvement
        """
        chunk_ids = [chunk['id'] for chunk in chunks]

        query_data = {
            'tenant_id': tenant_id,
            'question': question,
            'top_chunks': chunk_ids,
            'answer': answer,
            'mode': mode,
            'latency_ms': latency_ms
        }

        try:
            supabase_service.client.table('queries').insert(query_data).execute()
        except Exception as e:
            # Don't fail the request if logging fails
            print(f"Failed to log query: {str(e)}")

# Global instance
rag_engine = RAGEngine()