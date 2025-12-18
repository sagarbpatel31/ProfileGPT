"""
ProfileGPT FastAPI Backend - Minimal Railway Deployment Version
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="ProfileGPT API",
    description="RAG-based Personalized Portfolio Chat API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "ProfileGPT API is running",
        "status": "ok",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ProfileGPT API",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "port": os.getenv("PORT", "8000")
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)