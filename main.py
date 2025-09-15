import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

require('dotenv').config();

from dotenv import load_dotenv
import os

# Load variables from .env into environment
load_dotenv()

# Access the API key
api_key = os.getenv("API_KEY")

print(api_key)  # just to confirm it works

# Import config first to ensure environment variables are loaded
from config import Config

from api import app as api_app

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Verify configuration is loaded
    Config.verify_config()
    
    app = FastAPI(
        title="Summarizer API",
        version="1.0",
        description="API for summarizing various types of content including web pages, PDFs, and YouTube videos"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(api_app, prefix="/summarize")
    
    return app

if __name__ == "__main__":
    # Create and run the application
    app = create_app()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )
