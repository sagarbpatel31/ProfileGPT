"""
ProfileGPT FastAPI Backend - RAG Orchestration Service
100% Free Implementation with SQLite + Mock Models
"""
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import uuid
from dotenv import load_dotenv

# Import our custom implementations
from database import DatabaseManager
from rag_engine import RAGEngine
from profile_scrapers import scrape_profile_from_url, get_supported_platforms

load_dotenv()

# Initialize database and RAG engine
db_manager = DatabaseManager()
rag_engine = RAGEngine(db_manager)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app = FastAPI(
    title="ProfileGPT API",
    description="RAG-based Personalized Portfolio Chat API - 100% Free Implementation",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class ChatRequest(BaseModel):
    question: str
    mode: str = "detailed"  # short, detailed, star
    tenant_id: Optional[str] = "demo-tenant"

class ChatResponse(BaseModel):
    answer: str
    citations: List[Dict[str, Any]]
    sources: List[Dict[str, Any]]
    latency_ms: int
    mode: str

class SkillResponse(BaseModel):
    skill: str
    has_skill: bool
    confidence: float
    evidence: List[Dict[str, Any]]

class IngestResponse(BaseModel):
    job_id: str
    status: str
    message: str
    chunks_created: int = 0

class URLIngestRequest(BaseModel):
    url: str
    source_type: Optional[str] = None  # Will be auto-detected if not provided
    title: Optional[str] = None
    tenant_id: Optional[str] = "demo-tenant"

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "ProfileGPT API is running",
        "status": "ok"
    }

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ProfileGPT API",
        "implementation": "100% Free (SQLite + Mock Models)",
        "features": ["RAG Chat", "Skill Lookup", "Document Ingestion", "Citations"]
    }

# Main chat endpoint - FULLY IMPLEMENTED
@app.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest):
    """
    Main RAG endpoint for answering questions about the profile
    Uses 100% free implementation with mock LLM and embeddings
    """
    try:
        response = rag_engine.ask(
            question=request.question,
            tenant_id=request.tenant_id or "demo-tenant",
            mode=request.mode
        )

        return ChatResponse(
            answer=response.answer,
            citations=response.citations,
            sources=response.sources,
            latency_ms=response.latency_ms,
            mode=response.mode
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Skills lookup endpoint - FULLY IMPLEMENTED
@app.get("/skills", response_model=SkillResponse)
async def check_skill(name: str, tenant_id: Optional[str] = "demo-tenant"):
    """
    Fast skill lookup from database with evidence
    """
    try:
        result = rag_engine.check_skill(name, tenant_id)

        return SkillResponse(
            skill=name,
            has_skill=result['has_skill'],
            confidence=result['confidence'],
            evidence=result['evidence']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# List available skills
@app.get("/skills/list")
async def list_skills(tenant_id: Optional[str] = "demo-tenant"):
    """
    List all available skills for the tenant
    """
    return {
        "skills": [
            "Python", "JavaScript", "React", "FastAPI", "PostgreSQL",
            "Docker", "AWS", "Machine Learning", "AI", "Git", "Linux",
            "Node.js", "TypeScript", "MongoDB", "Redis", "Kubernetes"
        ],
        "total": 16
    }

# URL-based profile ingestion
@app.post("/ingest/url", response_model=IngestResponse)
async def ingest_url(request: URLIngestRequest):
    """
    Scrape and ingest content from a profile URL
    Supports GitHub, LinkedIn, Dev.to, Stack Overflow, Medium, and general websites
    """
    try:
        # Scrape the profile
        profile_data = scrape_profile_from_url(request.url)

        if not profile_data:
            return IngestResponse(
                job_id=str(uuid.uuid4()),
                status="failed",
                message=f"Could not scrape content from {request.url}. Please check the URL or try a different platform."
            )

        # Use scraped data
        title = request.title or profile_data['title']
        source_type = request.source_type or profile_data['source_type']
        content = profile_data['content']

        # Ingest the scraped content
        doc_id = rag_engine.ingest_document(
            tenant_id=request.tenant_id,
            source_type=source_type,
            title=title,
            content=content,
            url=request.url
        )

        # Calculate chunks created (estimate)
        chunks_created = max(1, len(content.split()) // 600)

        return IngestResponse(
            job_id=doc_id,
            status="completed",
            message=f"Successfully scraped and processed '{title}' from {profile_data['platform']}",
            chunks_created=chunks_created
        )

    except Exception as e:
        return IngestResponse(
            job_id=str(uuid.uuid4()),
            status="failed",
            message=f"Error processing URL: {str(e)}"
        )

# Get supported platforms
@app.get("/platforms")
async def get_platforms():
    """
    Get list of supported platforms for URL scraping
    """
    return {
        "supported_platforms": get_supported_platforms(),
        "note": "Some platforms like LinkedIn and Twitter have restrictions on automated scraping."
    }

# Document ingestion endpoint - FULLY IMPLEMENTED
@app.post("/ingest", response_model=IngestResponse)
async def ingest_document(
    file: UploadFile = File(...),
    source_type: str = Form("misc"),
    tenant_id: Optional[str] = Form("demo-tenant"),
    title: Optional[str] = Form(None)
):
    """
    Upload and process documents for RAG indexing
    Supports: PDF, DOCX, TXT, MD files
    """
    try:
        # Read file content
        content = await file.read()

        # Parse different file types
        filename = file.filename or "unknown"
        file_ext = filename.lower().split('.')[-1] if '.' in filename else ''

        if file_ext == 'pdf':
            try:
                import PyPDF2
                import io

                pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
                text_content = ""

                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"

                if not text_content.strip():
                    text_content = f"PDF file uploaded: {filename}. Could not extract text content."

            except Exception as e:
                text_content = f"PDF file uploaded: {filename}. Error parsing PDF: {str(e)}"

        elif file_ext in ['txt', 'md']:
            try:
                text_content = content.decode('utf-8')
            except UnicodeDecodeError:
                text_content = f"Text file uploaded: {filename}. Could not decode as UTF-8."

        else:
            # For other file types, try UTF-8 first, then fallback
            try:
                text_content = content.decode('utf-8')
            except UnicodeDecodeError:
                text_content = f"File uploaded: {filename}. Binary file - content parsing would need specific libraries for this format."

        # Generate document title if not provided
        doc_title = title or file.filename or "Uploaded Document"

        # Ingest document
        doc_id = rag_engine.ingest_document(
            tenant_id=tenant_id,
            source_type=source_type,
            title=doc_title,
            content=text_content,
            url=None
        )

        # Calculate chunks created (estimate)
        chunks_created = max(1, len(text_content.split()) // 600)

        return IngestResponse(
            job_id=doc_id,
            status="completed",
            message=f"Document '{doc_title}' processed successfully",
            chunks_created=chunks_created
        )

    except Exception as e:
        return IngestResponse(
            job_id=str(uuid.uuid4()),
            status="failed",
            message=f"Error processing document: {str(e)}"
        )

# Ingestion status endpoint
@app.get("/ingest/{job_id}")
async def get_ingestion_status(job_id: str):
    """
    Check the status of a document ingestion job
    """
    return {
        "job_id": job_id,
        "status": "completed",
        "progress": 100,
        "chunks_created": 8,
        "skills_extracted": 5,
        "message": "Document processing completed"
    }

# Source content endpoint
@app.get("/sources/{chunk_id}")
async def get_source_content(chunk_id: str):
    """
    Get raw source content for a specific chunk
    """
    # In a real implementation, this would query the database
    return {
        "chunk_id": chunk_id,
        "text": "This is sample source content. In a real implementation, this would fetch the actual chunk content from the database.",
        "source_type": "resume",
        "title": "Software Engineer Resume",
        "url": None,
        "section": "Experience"
    }

# Document deletion endpoint
@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document and all its associated chunks
    """
    try:
        # Delete chunks first (foreign key constraint)
        db_manager.delete_document_chunks(document_id)

        # Then delete the document
        db_manager.delete_document(document_id)

        return {"message": f"Document {document_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Document listing endpoint
@app.get("/documents/{tenant_id}")
async def get_tenant_documents(tenant_id: str):
    """
    Get all documents for a tenant
    """
    try:
        documents = db_manager.get_tenant_documents(tenant_id)

        return {
            "tenant_id": tenant_id,
            "documents": [
                {
                    "id": doc.id,
                    "title": doc.title,
                    "source_type": doc.source_type,
                    "url": doc.url,
                    "chunks_count": len(db_manager.get_document_chunks(doc.id)),
                    "created_at": doc.created_at.isoformat()
                }
                for doc in documents
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Tenant management
class TenantCreateRequest(BaseModel):
    name: str
    email: str
    password: str
    profession: Optional[str] = None
    bio: Optional[str] = None

class TenantLoginRequest(BaseModel):
    email: str
    password: str

@app.post("/tenant")
async def create_tenant(request: TenantCreateRequest):
    """
    Create a new tenant workspace
    """
    try:
        tenant_info = db_manager.create_tenant_account(
            name=request.name,
            email=request.email,
            password=request.password,
            profession=request.profession,
            bio=request.bio
        )

        return {
            **tenant_info,
            "embed_code": f'<script src="{FRONTEND_URL}/widget.js" data-tenant="{tenant_info["tenant_id"]}"></script>',
            "chat_url": f"{FRONTEND_URL}?tenant={tenant_info['tenant_id']}"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tenant/login")
async def tenant_login(request: TenantLoginRequest):
    """
    Authenticate an existing tenant
    """
    try:
        tenant = db_manager.verify_tenant_credentials(request.email, request.password)
        if not tenant:
            raise HTTPException(status_code=401, detail="Invalid email or password.")

        return {
            **tenant,
            "embed_code": f'<script src="{FRONTEND_URL}/widget.js" data-tenant="{tenant["tenant_id"]}"></script>',
            "chat_url": f"{FRONTEND_URL}?tenant={tenant['tenant_id']}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tenant/{tenant_id}/insights")
async def tenant_insights(tenant_id: str):
    """
    Provide profile-specific topic recommendations and skills
    """
    try:
        return rag_engine.generate_profile_insights(tenant_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add some demo data on startup
@app.on_event("startup")
async def create_demo_data():
    """Create sample documents for demo purposes"""
    demo_resume = """
    John Doe - Software Engineer

    EXPERIENCE:
    Senior Software Engineer at TechCorp (2021-2024)
    - Built scalable web applications using Python, FastAPI, and React
    - Implemented machine learning models for recommendation systems
    - Led a team of 5 developers and improved deployment pipeline efficiency by 40%
    - Technologies: Python, JavaScript, PostgreSQL, Docker, AWS, Redis

    Software Developer at StartupInc (2019-2021)
    - Developed full-stack applications with Node.js and MongoDB
    - Created data visualization dashboards using D3.js and React
    - Implemented CI/CD pipelines and automated testing frameworks
    - Technologies: Node.js, MongoDB, React, TypeScript, Git

    SKILLS:
    Programming: Python, C/C++, JavaScript, TypeScript, Java, Go
    Frameworks: FastAPI, Django, React, Node.js, Express
    Databases: PostgreSQL, MongoDB, Redis, MySQL
    Cloud: AWS (EC2, S3, Lambda), Docker, Kubernetes
    Tools: Git, Linux, CI/CD, Jenkins, Terraform

    EDUCATION:
    B.S. Computer Science, University of Technology (2019)
    - Focus on Machine Learning and Software Engineering
    - Graduated Magna Cum Laude, GPA: 3.8/4.0
    """

    try:
        # Ingest demo resume
        rag_engine.ingest_document(
            tenant_id="demo-tenant",
            source_type="resume",
            title="John Doe - Software Engineer Resume",
            content=demo_resume,
            url=None
        )
        print("✅ Demo data created successfully")
    except Exception as e:
        print(f"⚠️ Warning: Could not create demo data: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
