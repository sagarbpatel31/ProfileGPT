"""
Ultra-minimal FastAPI test for Railway deployment
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

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

@app.post("/ask")
def ask_question(request: dict):
    logger.info(f"Ask endpoint called with: {request}")
    question = request.get("question", "")
    mode = request.get("mode", "detailed")
    tenant_id = request.get("tenant_id", "demo")

    # Simple test response for now
    return {
        "answer": f"Thank you for asking: '{question}'. This is a test response in {mode} mode for tenant {tenant_id}. Backend is successfully connected! 🎉",
        "citations": [],
        "sources": []
    }

@app.post("/tenant")
def create_tenant(request: dict):
    logger.info(f"Create tenant called with: {request}")
    name = request.get("name", "")
    email = request.get("email", "")
    password = request.get("password", "")
    profession = request.get("profession", "")
    bio = request.get("bio", "")

    # Generate a simple tenant ID for testing
    import uuid
    tenant_id = str(uuid.uuid4())[:8]
    api_key = f"pk_test_{tenant_id}"

    # Simple test response for now
    return {
        "tenant_id": tenant_id,
        "name": name,
        "email": email,
        "api_key": api_key,
        "embed_code": f'<script src="https://profile-gpt-sagarbpatel31s-projects.vercel.app/widget.js" data-tenant="{tenant_id}"></script>',
        "chat_url": f"https://profile-gpt-sagarbpatel31s-projects.vercel.app?tenant={tenant_id}",
        "message": "Account created successfully! This is a test implementation."
    }

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