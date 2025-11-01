"""
OpenForge Backend - FastAPI Application
Main entry point for the backend API server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from app.routers import dashboard, projects
from app.config import settings

# Load environment variables
load_dotenv()

app = FastAPI(
    title="OpenForge API",
    description="Backend API for OpenForge - AI-Assisted Open Source Collaboration Platform",
    version="0.1.0",
)

# CORS middleware configuration
# Allowed origins are dynamically configured based on environment

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(dashboard.router)
app.include_router(projects.router)


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


@app.get("/api/cors-debug")
async def cors_debug():
    """Debug endpoint to check CORS configuration."""
    return {
        "allowed_origins": settings.allowed_origins,
        "environment": settings.environment,
        "frontend_url": settings.frontend_url,
        "is_production": settings.is_production,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
