"""
Ultra-minimal FastAPI test for Railway deployment
"""
from fastapi import FastAPI
import os
import logging

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
def read_root():
    logger.info("Root endpoint called")
    return {"Hello": "World", "PORT": os.getenv("PORT", "unknown")}

@app.get("/health")
def health():
    logger.info("Health endpoint called")
    return {"status": "ok", "port": os.getenv("PORT", "unknown")}

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