# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ProfileGPT (SagarGPT) is a Personalized GPT Portfolio system that enables recruiters and collaborators to chat with a professional profile using Retrieval-Augmented Generation (RAG). The system provides grounded, cited answers from resume, cover letters, LinkedIn, GitHub, portfolio pages, and work documents.

## Architecture

**Tech Stack:**
- **Frontend**: Next.js + Tailwind + shadcn/ui
- **Backend**: FastAPI (Python) for RAG orchestration
- **Database**: Postgres with pgvector extension (via Supabase)
- **Vector Store**: Supabase pgvector or Qdrant
- **Storage**: Supabase Storage or AWS S3
- **LLM**: Hosted APIs (recommended) or local Ollama
- **Embedding Models**: bge-large/e5-large or hosted embeddings
- **Observability**: Langfuse for tracing

**System Flow:**
```
User (Recruiter) ↔ Portfolio Site (Next.js) ↔ RAG API (FastAPI) ↔ Vector DB (pgvector/Qdrant)
                                                                  ↕ Object/Doc Store (S3/Supabase)
                                                                  ↕ Relational DB (Postgres/Supabase)
                                                                  ↕ Reranker Model (cross-encoder)
                                                                  ↕ LLM API / Local LLM (Ollama)
```

## Core Components

### 1. RAG Pipeline
- **Hybrid Search**: BM25 + semantic embeddings + cross-encoder reranker
- **Chunking**: 800 tokens with 200 token overlap
- **Skills Matrix**: Precomputed skill → evidence chunk mappings for fast lookups
- **Citations**: All answers include source links and evidence

### 2. Data Model

**Vector Store Schema:**
- `id`, `tenant_id`, `doc_id`, `source_type` (resume|cover_letter|linkedin|github|portfolio|paper|misc)
- `title`, `section`, `url/path`, `text`, `embedding`
- `tags` (JSONB: skills[], metrics[], roles[], dates:{from,to})
- `visibility` (public|private)

**Key Tables:**
- `tenants` - Multi-tenant workspaces
- `documents` - Source document metadata
- `chunks` - Text chunks with embeddings
- `skills` - Skill taxonomy with synonyms
- `skill_evidence` - Precomputed skill-to-evidence mappings
- `queries` - Query logs with performance metrics

### 3. API Endpoints
- `POST /ingest` - Upload/process documents
- `GET /ingest/:jobId` - Check processing status
- `POST /ask` - Main chat endpoint with citations
- `GET /skills?name=CUDA` - Fast skill lookups
- `GET /sources/:chunkId` - Raw source content
- `POST /tenant` - Create workspace

## Development Commands

Since this is a design document without implemented code yet, here are the planned commands based on the tech stack:

### Frontend (Next.js)
```bash
npm run dev          # Start development server
npm run build        # Production build
npm run lint         # ESLint
npm run type-check   # TypeScript checking
```

### Backend (FastAPI)
```bash
pip install -r requirements.txt  # Install dependencies
uvicorn main:app --reload        # Start development server
python -m pytest                # Run tests
alembic upgrade head             # Run database migrations
```

### Database
```bash
# Supabase local development
supabase start
supabase db reset
supabase gen types typescript --local > types/database.ts
```

### Docker (Alternative deployment)
```bash
docker-compose up -d          # Start all services
docker-compose logs -f api    # View API logs
docker-compose down           # Stop services
```

## Implementation Roadmap

**Week 1**: Ingest pipeline + vector store + /ask endpoint with citations
**Week 2**: Skills matrix + Next.js widget + hosted deployment
**Week 3**: Multi-tenant onboarding + embed script + admin console
**Week 4**: Observability, rate limits, polish, documentation

## Deployment Options

### Option A: Vercel + Supabase (Current Deployment)
- **Frontend**: Vercel (Next.js)
- **Backend**: Vercel Serverless Functions (Python API routes)
- **Database**: Supabase (Postgres + pgvector + Storage)
- **LLM/Embeddings**: Hosted APIs (OpenAI)
- **Observability**: Langfuse cloud

### Option B: Local/Private
- **Stack**: Docker Compose with FastAPI, Qdrant, Postgres, Ollama, MinIO
- **GPU**: Runpod/Lambda for local models

### Option C: Cloud-Native (AWS)
- **Frontend**: Vercel or Amplify
- **Backend**: ECS Fargate or Lambda
- **Database**: RDS Postgres with pgvector or Aurora + Qdrant
- **Storage**: S3 + CloudFront

## Security & Privacy

- **Transport**: TLS everywhere
- **At Rest**: Encrypted DB volumes and object storage
- **Access**: Row-level security (RLS), per-tenant RBAC
- **PII**: Email/phone redaction before indexing
- **Secrets**: Managed vault (Vercel/AWS Secrets Manager)

## Multi-Tenant Configuration

Each tenant workspace includes:
- Separate vector indices and storage namespacing
- Custom themes, tones, and skill taxonomies
- Document connectors (LinkedIn, GitHub, Google Drive)
- Embeddable widget with tenant-scoped API keys

## Key Features

1. **Truthful Q&A**: Answers strictly from verified documents with citations
2. **Fast Skill Checks**: Precomputed yes/no answers with evidence links
3. **Chat Modes**: Short/Detailed/STAR story formats
4. **Multi-tenant**: Anyone can create their own Personal GPT
5. **Embeddable**: JS snippet for portfolio websites
6. **Admin Console**: Document management, skill taxonomy, analytics

## Ingestion Pipeline

1. **Upload/Fetch** → 2. **Parse** (PDF/DOCX/HTML/Markdown) → 3. **Clean** → 4. **Chunk** (800/200) → 5. **Embed** → 6. **Persist** vectors+metadata → 7. **Skill extraction** (NER/keyword → evidence links)

## Observability

- **Tracing**: Langfuse for prompts, retrieval context, latencies
- **Logging**: Structured app logs for debugging
- **Monitoring**: Query logs, unanswered questions, performance metrics
- **Feedback**: User ratings to improve retrieval quality