"""
OpenForge Backend - FastAPI Application
Main entry point for the backend API server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI(
    title="OpenForge API",
    description="Backend API for OpenForge - AI-Assisted Open Source Collaboration Platform",
    version="0.1.0",
)

# CORS middleware configuration
# Update allowed_origins in production to match your frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "OpenForge API is running", "status": "healthy"}


@app.get("/api/health")
async def health():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "service": "openforge-backend",
        "version": "0.1.0",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
