# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from dotenv import load_dotenv

from api import router as api_router
from config import Config

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    Config.verify_config()

    app = FastAPI(
        title="Search Analyzer API",
        version="1.0",
        description="Summarizer and document analysis"
    )

    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    # Simple root route
    @app.get("/")
    async def root():
        return {
            "message": "Welcome to Search Analyzer API",
            "health": "/summarize/health",
            "docs": "/docs"
        }

    # Include summarizer routes
    app.include_router(api_router, prefix="/summarize")

    # Serve reports directory
    app.mount("/reports", StaticFiles(directory=Config.REPORTS_DIR), name="reports")

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
