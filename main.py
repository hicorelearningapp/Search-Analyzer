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
    # Ensure config is valid before app starts
    Config.verify_config()

    app = FastAPI(
        title="Search Analyzer API",
        version="1.0",
        description="Summarizer and document analysis service"
    )

    # ✅ Root route for debugging
    @app.get("/")
    async def root():
        return {
            "message": "App is running on Azure 🚀",
            "status": "ok",
            "docs": "/docs",
            "health": "/summarize/health"
        }

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Restrict later if needed
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True
    )

    # Register API router under /summarize
    app.include_router(api_router, prefix="/summarize")

    # Static reports directory
    if not os.path.exists(Config.REPORTS_DIR):
        os.makedirs(Config.REPORTS_DIR)
    app.mount("/reports", StaticFiles(directory=Config.REPORTS_DIR), name="reports")

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
