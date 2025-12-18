"""
ProfileGPT - AI-Powered Portfolio Assistant
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import io
from typing import List, Dict, Any
import openai
from openai import OpenAI
import PyPDF2
from docx import Document
import tiktoken
import uuid
from datetime import datetime
import json

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ProfileGPT API", version="1.0.0")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# In-memory storage for demo (replace with real database in production)
documents_store = {}
chunks_store = {}
tenant_store = {}

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://profile-gpt-sagarbpatel31s-projects.vercel.app",
        "http://localhost:3000",  # For local development
        "https://localhost:3000", # For local development with HTTPS
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    logger.info("Root endpoint called")
    return {"Hello": "World", "PORT": os.getenv("PORT", "unknown")}

@app.get("/health")
def health():
    logger.info("Health endpoint called")
    return {"status": "ok", "port": os.getenv("PORT", "unknown")}

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file content"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        return ""

def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file content"""
    try:
        doc = Document(io.BytesIO(file_content))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting DOCX text: {e}")
        return ""

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks"""
    if not text:
        return []

    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)

    chunks = []
    start = 0
    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
        start = end - overlap
        if start >= len(tokens):
            break

    return chunks

def find_relevant_chunks(question: str, tenant_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Find relevant document chunks for the question (simplified similarity)"""
    relevant_chunks = []
    question_lower = question.lower()

    # Get chunks for this tenant
    tenant_chunks = chunks_store.get(tenant_id, [])

    # Simple keyword matching (replace with vector similarity in production)
    for chunk_data in tenant_chunks:
        chunk_text_lower = chunk_data["text"].lower()
        # Basic relevance scoring based on keyword matches
        score = 0
        question_words = question_lower.split()
        for word in question_words:
            if len(word) > 3:  # Only count meaningful words
                score += chunk_text_lower.count(word)

        if score > 0:
            chunk_data["relevance_score"] = score
            relevant_chunks.append(chunk_data)

    # Sort by relevance and return top chunks
    relevant_chunks.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    return relevant_chunks[:limit]

@app.post("/ask")
def ask_question(request: dict):
    logger.info(f"Ask endpoint called with: {request}")
    question = request.get("question", "")
    mode = request.get("mode", "detailed")
    tenant_id = request.get("tenant_id", "demo")

    if not question:
        raise HTTPException(status_code=400, detail="Question is required")

    # Get tenant info
    tenant_info = tenant_store.get(tenant_id, {})
    tenant_name = tenant_info.get("name", "User")

    # Find relevant document chunks
    relevant_chunks = find_relevant_chunks(question, tenant_id)

    # Build context from relevant chunks
    context_parts = []
    citations = []
    sources = []

    for i, chunk in enumerate(relevant_chunks):
        context_parts.append(f"Source {i+1}: {chunk['text']}")
        citations.append({
            "id": chunk["id"],
            "source": chunk["source_type"],
            "title": chunk["title"],
            "relevance_score": chunk.get("relevance_score", 0)
        })
        sources.append({
            "id": chunk["id"],
            "title": chunk["title"],
            "source_type": chunk["source_type"],
            "filename": chunk.get("filename", "")
        })

    context = "\n\n".join(context_parts) if context_parts else "No relevant documents found."

    # Determine response style based on mode
    if mode == "short":
        style_instruction = "Provide a concise, direct answer in 1-2 sentences."
    elif mode == "star":
        style_instruction = "Structure your response using the STAR method (Situation, Task, Action, Result) when describing experiences."
    else:  # detailed
        style_instruction = "Provide a comprehensive, detailed response."

    # Create system prompt
    system_prompt = f"""You are an AI assistant representing {tenant_name}'s professional profile. Your role is to answer questions about their background, experience, and qualifications based solely on the provided documents.

Key guidelines:
1. Only answer based on information in the provided context
2. If the context doesn't contain enough information, politely say you don't have that information
3. Be professional and knowledgeable about {tenant_name}'s background
4. {style_instruction}
5. When possible, reference specific experiences or achievements
6. If asked about skills, provide specific examples from their experience

Context from {tenant_name}'s documents:
{context}"""

    user_prompt = f"Question: {question}"

    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        answer = response.choices[0].message.content

        return {
            "answer": answer,
            "citations": citations,
            "sources": sources,
            "context_used": len(relevant_chunks),
            "mode": mode
        }

    except Exception as e:
        logger.error(f"Error calling OpenAI API: {e}")
        return {
            "answer": f"I apologize, but I encountered an error while processing your question about {tenant_name}'s background. Please try again later.",
            "citations": citations,
            "sources": sources,
            "error": "AI_API_ERROR"
        }

@app.post("/tenant")
def create_tenant(request: dict):
    logger.info(f"=== TENANT CREATION REQUEST ===")
    logger.info(f"Request data: {request}")

    name = request.get("name", "")
    email = request.get("email", "")
    password = request.get("password", "")
    profession = request.get("profession", "")
    bio = request.get("bio", "")

    if not name or not email:
        raise HTTPException(status_code=400, detail="Name and email are required")

    # Generate tenant ID and API key
    tenant_id = str(uuid.uuid4())[:8]
    api_key = f"pk_test_{tenant_id}"

    # Store tenant data
    tenant_data = {
        "tenant_id": tenant_id,
        "name": name,
        "email": email,
        "profession": profession,
        "bio": bio,
        "api_key": api_key,
        "created_at": datetime.utcnow().isoformat(),
        "document_count": 0
    }
    tenant_store[tenant_id] = tenant_data

    # Initialize empty document and chunk stores for this tenant
    if tenant_id not in documents_store:
        documents_store[tenant_id] = []
    if tenant_id not in chunks_store:
        chunks_store[tenant_id] = []

    logger.info(f"Created tenant: {tenant_id} for {name}")

    return {
        "tenant_id": tenant_id,
        "name": name,
        "email": email,
        "api_key": api_key,
        "embed_code": f'<script src="https://profile-gpt-sagarbpatel31s-projects.vercel.app/widget.js" data-tenant="{tenant_id}"></script>',
        "chat_url": f"https://profile-gpt-sagarbpatel31s-projects.vercel.app?tenant={tenant_id}",
        "message": "Account created successfully! You can now upload documents to build your AI assistant."
    }

@app.post("/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    source_type: str = Form(...),
    tenant_id: str = Form(...),
    title: str = Form(None)
):
    logger.info(f"=== DOCUMENT INGEST REQUEST ===")
    logger.info(f"File: {file.filename}, Size: {file.size}, Type: {file.content_type}")
    logger.info(f"Source Type: {source_type}, Tenant: {tenant_id}, Title: {title}")

    # Check if tenant exists
    if tenant_id not in tenant_store:
        raise HTTPException(status_code=404, detail="Tenant not found")

    try:
        # Read file content
        content = await file.read()
        logger.info(f"File content length: {len(content)} bytes")

        # Extract text based on file type
        text = ""
        if file.content_type == "application/pdf" or file.filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(content)
        elif (file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              or file.filename.lower().endswith('.docx')):
            text = extract_text_from_docx(content)
        elif file.content_type == "text/plain" or file.filename.lower().endswith('.txt'):
            text = content.decode('utf-8', errors='ignore')
        else:
            # Try to decode as text anyway
            try:
                text = content.decode('utf-8', errors='ignore')
            except Exception:
                raise HTTPException(status_code=400, detail="Unsupported file type")

        if not text or len(text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Could not extract meaningful text from document")

        # Generate document ID
        document_id = f"doc_{tenant_id}_{str(uuid.uuid4())[:8]}"

        # Create document record
        document_data = {
            "id": document_id,
            "tenant_id": tenant_id,
            "filename": file.filename,
            "title": title or file.filename,
            "source_type": source_type,
            "content_type": file.content_type,
            "size": len(content),
            "text_length": len(text),
            "created_at": datetime.utcnow().isoformat(),
            "status": "processing"
        }

        # Store document
        if tenant_id not in documents_store:
            documents_store[tenant_id] = []
        documents_store[tenant_id].append(document_data)

        # Process text into chunks
        chunks = chunk_text(text)
        logger.info(f"Created {len(chunks)} chunks from document")

        # Store chunks
        if tenant_id not in chunks_store:
            chunks_store[tenant_id] = []

        for i, chunk_text in enumerate(chunks):
            chunk_data = {
                "id": f"{document_id}_chunk_{i}",
                "tenant_id": tenant_id,
                "document_id": document_id,
                "filename": file.filename,
                "title": title or file.filename,
                "source_type": source_type,
                "text": chunk_text,
                "chunk_index": i,
                "created_at": datetime.utcnow().isoformat()
            }
            chunks_store[tenant_id].append(chunk_data)

        # Update document status
        document_data["status"] = "completed"
        document_data["chunk_count"] = len(chunks)

        # Update tenant document count
        tenant_store[tenant_id]["document_count"] += 1

        logger.info(f"Successfully processed document {document_id} with {len(chunks)} chunks")

        return {
            "job_id": f"job_{document_id}",
            "status": "completed",
            "message": f"Document '{file.filename}' processed successfully! Created {len(chunks)} searchable chunks.",
            "document_id": document_id,
            "filename": file.filename,
            "source_type": source_type,
            "chunk_count": len(chunks),
            "text_length": len(text)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.get("/documents/{tenant_id}")
def get_documents(tenant_id: str):
    logger.info(f"=== GET DOCUMENTS FOR TENANT: {tenant_id} ===")

    # Check if tenant exists
    if tenant_id not in tenant_store:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Get documents for this tenant
    tenant_documents = documents_store.get(tenant_id, [])

    # Return document list
    return {
        "documents": tenant_documents,
        "total_count": len(tenant_documents),
        "tenant_id": tenant_id
    }

# Add middleware to log all requests
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"=== REQUEST: {request.method} {request.url} ===")
    logger.info(f"Headers: {dict(request.headers)}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# Add startup event for debugging
@app.on_event("startup")
async def startup_event():
    port = os.getenv("PORT", "unknown")
    logger.info(f"=== FastAPI starting up on PORT: {port} ===")
    logger.info(f"=== Environment variables: PORT={port} ===")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"=== STARTING UVICORN ON PORT {port} ===")
    logger.info(f"=== ALL ENV VARS: {dict(os.environ)} ===")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")