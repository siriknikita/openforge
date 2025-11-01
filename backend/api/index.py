"""
Vercel serverless function entry point for FastAPI

This file is the entry point for Vercel's Python serverless functions.
Vercel will automatically route requests to this handler.
"""
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Export the FastAPI app
# Vercel's Python runtime will automatically handle ASGI apps
from mangum import Mangum

handler = Mangum(app, lifespan="off")

