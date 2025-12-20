"""
ProfileGPT - Clean, Working Backend
Focuses on core functionality: tenant creation, document upload, and Q&A
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import io
import re
from typing import List, Dict, Any
from openai import OpenAI
import PyPDF2
from docx import Document
import tiktoken
import uuid
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="ProfileGPT API", version="2.0-Clean")

# Initialize OpenAI (will fail gracefully if no API key)
openai_client = None
try:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        openai_client = OpenAI(api_key=openai_api_key)
        logger.info("✅ OpenAI client initialized")
    else:
        logger.warning("⚠️ No OPENAI_API_KEY found - will return mock responses")
except Exception as e:
    logger.error(f"❌ OpenAI initialization failed: {e}")

# In-memory storage (simple and clean)
tenants = {}
documents = {}
chunks = {}

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://profile-gpt-sagarbpatel31s-projects.vercel.app",
        "http://localhost:3000",
        "https://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """Root endpoint with clear status"""
    return {
        "service": "ProfileGPT",
        "version": "2.0-Clean",
        "status": "running",
        "openai_available": openai_client is not None,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/tenant")
def create_tenant(request: dict):
    """Create a new tenant/user"""
    logger.info(f"Creating tenant: {request}")

    name = request.get("name", "").strip()
    email = request.get("email", "").strip()

    if not name or not email:
        raise HTTPException(status_code=400, detail="Name and email are required")

    # Generate tenant ID
    tenant_id = str(uuid.uuid4())[:8]
    api_key = f"pk_{tenant_id}"

    # Store tenant data
    tenant_data = {
        "tenant_id": tenant_id,
        "name": name,
        "email": email,
        "profession": request.get("profession", ""),
        "bio": request.get("bio", ""),
        "api_key": api_key,
        "created_at": datetime.utcnow().isoformat()
    }

    tenants[tenant_id] = tenant_data
    documents[tenant_id] = []
    chunks[tenant_id] = []

    logger.info(f"✅ Created tenant: {tenant_id}")

    return {
        "tenant_id": tenant_id,
        "name": name,
        "email": email,
        "api_key": api_key,
        "embed_code": f'<script src="https://profile-gpt-sagarbpatel31s-projects.vercel.app/widget.js" data-tenant="{tenant_id}"></script>',
        "chat_url": f"https://profile-gpt-sagarbpatel31s-projects.vercel.app?tenant={tenant_id}",
        "message": "Account created successfully!"
    }

def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """Extract text from uploaded file"""
    text = ""

    try:
        if filename.lower().endswith('.pdf'):
            # Extract from PDF
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"

        elif filename.lower().endswith('.docx'):
            # Extract from DOCX
            doc = Document(io.BytesIO(file_content))
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"

        elif filename.lower().endswith('.txt'):
            # Extract from TXT
            text = file_content.decode('utf-8', errors='ignore')

        else:
            # Try to decode as text
            text = file_content.decode('utf-8', errors='ignore')

    except Exception as e:
        logger.error(f"Error extracting text from {filename}: {e}")
        raise HTTPException(status_code=400, detail=f"Could not process file: {str(e)}")

    if len(text.strip()) < 10:
        raise HTTPException(status_code=400, detail="File contains too little text content")

    return text.strip()

def simple_chunk_text(text: str, chunk_size: int = 1000) -> List[str]:
    """Simple text chunking"""
    if not text:
        return []

    # Split by paragraphs first
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) < chunk_size:
            current_chunk += paragraph + "\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = paragraph + "\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

@app.post("/ingest")
async def upload_document(
    file: UploadFile = File(...),
    source_type: str = Form(...),
    tenant_id: str = Form(...),
    title: str = Form(None)
):
    """Upload and process a document"""
    logger.info(f"📄 Processing upload: {file.filename} for tenant {tenant_id}")

    # Validate tenant exists
    if tenant_id not in tenants:
        raise HTTPException(status_code=404, detail="Tenant not found")

    try:
        # Read file content
        content = await file.read()

        # Extract text
        text = extract_text_from_file(content, file.filename)

        # Create document record
        document_id = f"doc_{tenant_id}_{str(uuid.uuid4())[:8]}"
        document_data = {
            "id": document_id,
            "title": title or file.filename,
            "filename": file.filename,
            "source_type": source_type,
            "status": "processing",
            "size": len(content),
            "created_at": datetime.utcnow().isoformat()
        }

        # Chunk the text
        text_chunks = simple_chunk_text(text)

        # Store chunks
        for i, chunk_text in enumerate(text_chunks):
            chunk_data = {
                "id": f"{document_id}_chunk_{i}",
                "document_id": document_id,
                "text": chunk_text,
                "index": i
            }
            chunks[tenant_id].append(chunk_data)

        # Update document status
        document_data["status"] = "completed"
        document_data["chunk_count"] = len(text_chunks)

        # Store document
        documents[tenant_id].append(document_data)

        logger.info(f"✅ Processed document {document_id}: {len(text_chunks)} chunks")

        return {
            "job_id": f"job_{document_id}",
            "status": "completed",
            "message": f"Document processed successfully! Created {len(text_chunks)} chunks.",
            "document_id": document_id,
            "filename": file.filename,
            "source_type": source_type,
            "chunk_count": len(text_chunks)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error processing document: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

def find_relevant_chunks(question: str, tenant_id: str, max_chunks: int = 5) -> List[Dict]:
    """Find relevant chunks for the question"""
    if tenant_id not in chunks:
        return []

    tenant_chunks = chunks[tenant_id]
    question_lower = question.lower()

    # Score chunks by keyword relevance
    scored_chunks = []
    for chunk in tenant_chunks:
        text_lower = chunk["text"].lower()

        # Simple keyword scoring
        score = 0
        for word in question_lower.split():
            if len(word) > 3:  # Only meaningful words
                score += text_lower.count(word)

        if score > 0:
            chunk["relevance_score"] = score
            scored_chunks.append(chunk)

    # Sort by relevance
    scored_chunks.sort(key=lambda x: x["relevance_score"], reverse=True)
    return scored_chunks[:max_chunks]

@app.post("/ask")
def ask_question(request: dict):
    """Answer questions about uploaded documents"""
    logger.info(f"💬 Question: {request}")

    question = request.get("question", "").strip()
    tenant_id = request.get("tenant_id", "")
    mode = request.get("mode", "detailed")

    if not question:
        raise HTTPException(status_code=400, detail="Question is required")

    if tenant_id not in tenants:
        raise HTTPException(status_code=404, detail="Tenant not found")

    tenant_name = tenants[tenant_id]["name"]

    # Find relevant content
    relevant_chunks = find_relevant_chunks(question, tenant_id)

    if not relevant_chunks:
        return {
            "answer": f"I don't have any documents uploaded for {tenant_name} yet. Please upload a resume, CV, or other documents first.",
            "citations": [],
            "sources": [],
            "context_used": 0
        }

    # Build context
    context = "\n\n".join([f"Document section {i+1}:\n{chunk['text']}"
                          for i, chunk in enumerate(relevant_chunks)])

    citations = [{"id": chunk["id"], "document_id": chunk["document_id"]}
                for chunk in relevant_chunks]

    # Generate response
    if openai_client:
        try:
            # Create appropriate prompt based on mode
            if mode == "short":
                style_instruction = "Provide a concise, direct answer in 1-2 sentences."
            elif mode == "star":
                style_instruction = """Structure your response using the STAR method:
                - Situation: What was the context or challenge?
                - Task: What needed to be accomplished?
                - Action: What specific actions were taken?
                - Result: What was the outcome or impact?"""
            else:
                style_instruction = "Provide a comprehensive, detailed response."

            system_prompt = f"""You are an AI assistant for {tenant_name}'s professional profile. Answer questions about their background based on the provided documents.

Guidelines:
- Only use information from the provided context
- Be specific about experience, skills, and achievements
- {style_instruction}
- If information isn't available, say so politely

Context from {tenant_name}'s documents:
{context}"""

            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Question: {question}"}
                ],
                temperature=0.7,
                max_tokens=500
            )

            answer = response.choices[0].message.content

        except Exception as e:
            logger.error(f"❌ OpenAI error: {e}")
            answer = f"Based on {tenant_name}'s documents, I found relevant information but encountered an issue generating the response. Please try again."

    else:
        # Fallback response when OpenAI is not available
        answer = f"Based on {tenant_name}'s uploaded documents, I found {len(relevant_chunks)} relevant sections related to your question: '{question}'. [OpenAI integration would provide detailed response here]"

    return {
        "answer": answer,
        "citations": citations,
        "sources": [{"id": chunk["document_id"], "title": "Uploaded Document"} for chunk in relevant_chunks],
        "context_used": len(relevant_chunks),
        "mode": mode
    }

@app.get("/documents/{tenant_id}")
def get_documents(tenant_id: str):
    """Get documents for a tenant"""
    logger.info(f"📋 Getting documents for tenant: {tenant_id}")

    if tenant_id not in tenants:
        raise HTTPException(status_code=404, detail="Tenant not found")

    tenant_documents = documents.get(tenant_id, [])

    return {
        "documents": tenant_documents,
        "total_count": len(tenant_documents),
        "tenant_id": tenant_id
    }

@app.delete("/documents/{document_id}")
def delete_document(document_id: str):
    """Delete a document"""
    logger.info(f"🗑️ Deleting document: {document_id}")

    # Find and remove document
    for tenant_id in documents:
        documents[tenant_id] = [doc for doc in documents[tenant_id] if doc["id"] != document_id]

    # Remove associated chunks
    for tenant_id in chunks:
        chunks[tenant_id] = [chunk for chunk in chunks[tenant_id] if chunk["document_id"] != document_id]

    return {"message": "Document deleted successfully"}

# Request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = datetime.utcnow()
    response = await call_next(request)
    duration = (datetime.utcnow() - start_time).total_seconds()
    logger.info(f"📊 {request.method} {request.url.path} - {response.status_code} ({duration:.2f}s)")
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"🚀 Starting ProfileGPT Clean Backend on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)