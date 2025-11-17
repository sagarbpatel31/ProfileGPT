"""
Configuration settings for ProfileGPT API
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_key: str = ""
    database_url: str = ""

    # LLM APIs
    openai_api_key: str = ""

    # Embedding Models
    openai_embedding_model: str = "text-embedding-3-large"
    embedding_model_name: str = "BAAI/bge-large-en-v1.5"

    # Vector Database
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None

    # Observability
    langfuse_secret_key: str = ""
    langfuse_public_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Application
    environment: str = "development"
    log_level: str = "INFO"
    max_upload_size: int = 10485760  # 10MB

    # RAG Settings
    chunk_size: int = 800
    chunk_overlap: int = 200
    max_retrieval_chunks: int = 8
    enable_reranking: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()