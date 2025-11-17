"""
ProfileGPT FastAPI Backend - Simplified version for testing
This version works without Supabase setup for initial testing
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import time

app = FastAPI(
    title="ProfileGPT API (Simple)",
    description="RAG-based Personalized Portfolio Chat API - Test Version",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage for testing
test_data = {
    "skills": [
        {"name": "Python", "confidence": 0.95, "evidence": ["Built multiple Python web applications", "5+ years of Python development"]},
        {"name": "JavaScript", "confidence": 0.90, "evidence": ["React frontend development", "Node.js backend services"]},
        {"name": "Machine Learning", "confidence": 0.85, "evidence": ["Implemented neural networks", "Data analysis projects"]},
        {"name": "Docker", "confidence": 0.80, "evidence": ["Containerized applications", "Docker Compose orchestration"]},
    ],
    "profile_context": """
    Experienced Software Engineer with expertise in Python, JavaScript, and Machine Learning.
    Built scalable web applications using FastAPI, React, and PostgreSQL.
    Strong background in containerization with Docker and cloud deployment on AWS.
    Passionate about AI/ML and building intelligent systems that solve real-world problems.
    """
}

# Pydantic models
class ChatRequest(BaseModel):
    question: str
    mode: str = "detailed"

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
    evidence: List[str]

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ProfileGPT API (Simple)",
        "message": "Backend is running! Ready for Supabase integration."
    }

# Main chat endpoint (mock implementation)
@app.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest):
    """
    Mock RAG endpoint for testing
    """
    start_time = time.time()

    question = request.question.lower()

    # Simple keyword matching for demo
    if "skill" in question or "technology" in question:
        answer = "I have expertise in several technologies including Python, JavaScript, Machine Learning, and Docker. Here are the details:\n\n"
        for skill in test_data["skills"][:3]:
            answer += f"• **{skill['name']}** (Confidence: {skill['confidence']*100:.0f}%): {skill['evidence'][0]}\n"

    elif any(skill in question for skill in ["python", "javascript", "machine learning", "docker", "ml", "ai"]):
        # Find specific skill
        found_skill = None
        for skill in test_data["skills"]:
            if skill["name"].lower() in question:
                found_skill = skill
                break

        if found_skill:
            answer = f"Yes, I have strong experience with {found_skill['name']} (Confidence: {found_skill['confidence']*100:.0f}%). Evidence includes:\n\n"
            for evidence in found_skill["evidence"]:
                answer += f"• {evidence}\n"
        else:
            answer = "I have experience with various technologies. Please ask about specific skills like Python, JavaScript, Machine Learning, or Docker."

    elif "experience" in question or "background" in question:
        answer = test_data["profile_context"]

    else:
        answer = f"This is a test response for the question: '{request.question}'. The RAG system will provide detailed, cited answers once connected to your document database."

    # Mock citations and sources
    citations = [
        {"index": 1, "title": "Software Engineer Resume", "section": "Experience", "chunk_id": "mock-chunk-1"},
        {"index": 2, "title": "GitHub Portfolio", "section": "Projects", "chunk_id": "mock-chunk-2"}
    ]

    sources = [
        {"chunk_id": "mock-chunk-1", "title": "Resume", "section": "Experience", "text_preview": "Sample experience text..."},
        {"chunk_id": "mock-chunk-2", "title": "GitHub", "section": "Projects", "text_preview": "Sample project description..."}
    ]

    latency_ms = int((time.time() - start_time) * 1000)

    return ChatResponse(
        answer=answer,
        citations=citations,
        sources=sources,
        latency_ms=latency_ms,
        mode=request.mode
    )

# Skills lookup endpoint
@app.get("/skills", response_model=SkillResponse)
async def check_skill(name: str):
    """
    Fast skill lookup from test data
    """
    skill_name = name.lower()

    for skill in test_data["skills"]:
        if skill["name"].lower() == skill_name:
            return SkillResponse(
                skill=skill["name"],
                has_skill=True,
                confidence=skill["confidence"],
                evidence=skill["evidence"]
            )

    return SkillResponse(
        skill=name,
        has_skill=False,
        confidence=0.0,
        evidence=[]
    )

# List available skills
@app.get("/skills/list")
async def list_skills():
    """
    Get all available skills for testing
    """
    return {
        "skills": [skill["name"] for skill in test_data["skills"]],
        "total": len(test_data["skills"])
    }

# Mock ingestion endpoint
@app.post("/ingest")
async def mock_ingest():
    """
    Mock document ingestion for testing
    """
    return {
        "job_id": "mock-job-123",
        "status": "completed",
        "message": "Mock ingestion successful. Connect Supabase for real document processing."
    }

# Configuration info
@app.get("/config")
async def get_config():
    """
    Show current configuration status
    """
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_supabase = bool(os.getenv("SUPABASE_URL"))

    return {
        "mode": "simple_test",
        "openai_configured": has_openai,
        "supabase_configured": has_supabase,
        "ready_for_production": has_openai and has_supabase,
        "next_steps": [
            "Set up Supabase project",
            "Configure environment variables in .env",
            "Run database setup script",
            "Switch to main.py for full functionality"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting ProfileGPT Simple Test Server...")
    print("📋 Available endpoints:")
    print("  • GET  /health - Health check")
    print("  • POST /ask - Chat with profile (mock data)")
    print("  • GET  /skills?name=Python - Check specific skill")
    print("  • GET  /skills/list - List all skills")
    print("  • GET  /config - Configuration status")
    print("  • GET  /docs - Interactive API documentation")
    print("\n🌐 Server will be available at: http://localhost:8000")
    print("📖 API Docs at: http://localhost:8000/docs")

    uvicorn.run(app, host="0.0.0.0", port=8000)