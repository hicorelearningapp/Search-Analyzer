# api/search_analyzer_routes.py
from fastapi import APIRouter, UploadFile, Form, HTTPException, Header, Depends
from fastapi.responses import JSONResponse
from enum import Enum
import os
import sys
from typing import Optional
from datetime import datetime

# Add the Search-Analyzer directory to the path
search_analyzer_path = os.path.join(os.path.dirname(__file__), "..", "..", "Search-Analyzer")
sys.path.append(search_analyzer_path)

from document_system import document_system
from services.general_search_services import (
    PDFService, YouTubeService, WebService, TextService,
    pdf_service, youtube_service, web_service, text_service
)
from app_state import AppState

router = APIRouter(prefix="/search-analyzer", tags=["Search Analyzer"])

# Create DocumentTypeEnum for API documentation
DocumentTypeEnum = Enum(
    "DocumentTypeEnum",
    {t.replace(" ", "_"): t for t in document_system.list_document_types()}
)

def get_app_state():
    return AppState()

@router.post("/pdf")
async def summarize_pdf(
    file: UploadFile,
    doc_type: DocumentTypeEnum = Form(...),
    pages: int = Form(2),
    session_id: str = Header(..., alias="X-Session-Id"),
    app_state: AppState = Depends(get_app_state)
):
    """Process and summarize a PDF document."""
    try:
        service = PDFService(app_state=app_state)
        return await service.process_pdf(file, doc_type, pages, session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/youtube")
async def summarize_youtube(
    query: str = Form(...),
    doc_type: DocumentTypeEnum = Form(...),
    pages: int = Form(2),
    session_id: str = Header(..., alias="X-Session-Id"),
    app_state: AppState = Depends(get_app_state)
):
    """Process and summarize a YouTube video."""
    try:
        service = YouTubeService(app_state=app_state)
        return await service.process_youtube(query, doc_type, pages, session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/web")
async def summarize_web(
    query: str = Form(...),
    doc_type: DocumentTypeEnum = Form(...),
    pages: int = Form(2),
    session_id: str = Header(..., alias="X-Session-Id"),
    app_state: AppState = Depends(get_app_state)
):
    """Process and summarize web content."""
    try:
        service = WebService(app_state=app_state)
        return await service.process_web(query, doc_type, pages, session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/text")
async def summarize_text(
    text: str = Form(...),
    doc_type: DocumentTypeEnum = Form(...),
    pages: int = Form(2),
    session_id: str = Header(..., alias="X-Session-Id"),
    app_state: AppState = Depends(get_app_state)
):
    """Process and summarize plain text."""
    try:
        service = TextService(app_state=app_state)
        return await service.process_text(text, doc_type, pages, session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}")
async def get_session_results(
    session_id: str,
    app_state: AppState = Depends(get_app_state)
):
    """Retrieve all search results for a session."""
    try:
        session_data = app_state.get_user_state(session_id)
        if "search_results" not in session_data.synthesis_storage:
            raise HTTPException(
                status_code=404,
                detail="No search results found for this session"
            )
            
        return {
            "session_id": session_id,
            "created_at": session_data.synthesis_storage.get("created_at"),
            "last_activity": session_data.synthesis_storage.get("last_activity"),
            "results": session_data.synthesis_storage.get("search_results", [])
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving session results: {str(e)}"
        )