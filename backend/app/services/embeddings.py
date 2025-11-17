"""
Embedding service for text vectorization
"""
import openai
from sentence_transformers import SentenceTransformer
from typing import List, Optional
from app.core.config import settings
import asyncio
import numpy as np

class EmbeddingService:
    def __init__(self):
        self.openai_client = None
        self.local_model = None
        self.use_openai = bool(settings.openai_api_key)

        if self.use_openai:
            self.openai_client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        else:
            # Load local sentence transformer model
            self.local_model = SentenceTransformer(settings.embedding_model_name)

    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        """
        if self.use_openai:
            return await self._openai_embed([text])
        else:
            return await self._local_embed([text])

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        """
        if self.use_openai:
            return await self._openai_embed(texts)
        else:
            return await self._local_embed(texts)

    async def _openai_embed(self, texts: List[str]) -> List[List[float]]:
        """
        Use OpenAI embedding API
        """
        try:
            response = await self.openai_client.embeddings.create(
                model=settings.openai_embedding_model,
                input=texts
            )

            embeddings = []
            for item in response.data:
                embeddings.append(item.embedding)

            return embeddings if len(embeddings) > 1 else embeddings[0]

        except Exception as e:
            raise Exception(f"OpenAI embedding failed: {str(e)}")

    async def _local_embed(self, texts: List[str]) -> List[List[float]]:
        """
        Use local sentence transformer model
        """
        try:
            # Run embedding in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                lambda: self.local_model.encode(texts, convert_to_numpy=True)
            )

            # Convert to list format
            if len(texts) == 1:
                return embeddings[0].tolist()
            else:
                return [emb.tolist() for emb in embeddings]

        except Exception as e:
            raise Exception(f"Local embedding failed: {str(e)}")

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings
        """
        if self.use_openai:
            # OpenAI text-embedding-3-large has 3072 dims, but can be reduced
            return 1536  # Using reduced dimension for better performance
        else:
            # BGE-large has 1024 dimensions
            return 1024

# Global instance
embedding_service = EmbeddingService()