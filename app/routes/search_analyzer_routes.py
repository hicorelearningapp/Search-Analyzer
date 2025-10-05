# app/api/search_analyzer_routes.py
from fastapi import APIRouter, UploadFile, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from enum import Enum
import os
import sys
from typing import Optional

# Add the Search-Analyzer directory to the path
search_analyzer_path = os.path.join(os.path.dirname(__file__), "..", "..", "Search-Analyzer")
sys.path.append(search_analyzer_path)

from utils.document_system_utils import document_system
from services.general_search_services import (
    PDFService, YouTubeService, WebService, TextService,
)
from app_state import SessionStateManager

router = APIRouter(prefix="/search-analyzer", tags=["Search Analyzer"])

# Create DocumentTypeEnum for API documentation
DocumentTypeEnum = Enum("DocumentTypeEnum", {t.replace(" ", "_"): t for t in document_system.list_document_types()})


# ---------------------------------------------------------------------------
# 🧾 PDF Summarization
# ---------------------------------------------------------------------------
@router.post("/pdf")
async def summarize_pdf(
    request: Request,
    file: UploadFile,
    doc_type: DocumentTypeEnum = Form(...),
    pages: int = Form(2)
):
    """
    Process and summarize a PDF document.
    Session-aware — tracks user uploads and document types processed.
    """
    try:
        # 1️⃣ Manage session
        manager = SessionStateManager.get_instance()
        session_id = request.headers.get("X-Session-ID")
        session_id = manager.get_or_create_session(session_id)
        session = manager.get_session(session_id)

        # 2️⃣ Process PDF
        service = PDFService()
        result = await service.process_pdf(file, doc_type, pages)

        # 3️⃣ Update session (record analyzed document type)
        analyzed_docs = getattr(session, "suggested_topics", [])
        analyzed_docs.append({"type": "PDF", "doc_type": doc_type.value})
        manager.update_session(session_id, {"suggested_topics": analyzed_docs})

        # 4️⃣ Return session-aware response
        return JSONResponse({
            "session_id": session_id,
            "result": result,
            "analyzed_docs": analyzed_docs
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "Failed to summarize PDF", "details": str(e)})


# ---------------------------------------------------------------------------
# 🎥 YouTube Summarization
# ---------------------------------------------------------------------------
@router.post("/youtube")
async def summarize_youtube(
    request: Request,
    query: str = Form(...),
    doc_type: DocumentTypeEnum = Form(...),
    pages: int = Form(2)
):
    """
    Process and summarize a YouTube video.
    Session-aware — remembers past YouTube analyses.
    """
    try:
        # 1️⃣ Manage session
        manager = SessionStateManager.get_instance()
        session_id = request.headers.get("X-Session-ID")
        session_id = manager.get_or_create_session(session_id)
        session = manager.get_session(session_id)

        # 2️⃣ Process YouTube video
        service = YouTubeService()
        result = await service.process_youtube(query, doc_type, pages)

        # 3️⃣ Update session (record analyzed videos)
        history = getattr(session, "suggested_topics", [])
        history.append({"type": "YouTube", "query": query, "doc_type": doc_type.value})
        manager.update_session(session_id, {"suggested_topics": history})

        # 4️⃣ Return response
        return JSONResponse({
            "session_id": session_id,
            "result": result,
            "session_history": history
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "Failed to summarize YouTube video", "details": str(e)})


# ---------------------------------------------------------------------------
# 🌐 Web Summarization
# ---------------------------------------------------------------------------
@router.post("/web")
async def summarize_web(
    request: Request,
    query: str = Form(...),
    doc_type: DocumentTypeEnum = Form(...),
    pages: int = Form(2)
):
    """
    Process and summarize web content.
    Session-aware — tracks user’s web queries.
    """
    try:
        # 1️⃣ Manage session
        manager = SessionStateManager.get_instance()
        session_id = request.headers.get("X-Session-ID")
        session_id = manager.get_or_create_session(session_id)
        session = manager.get_session(session_id)

        # 2️⃣ Process web content
        service = WebService()
        result = await service.process_web(query, doc_type, pages)

        # 3️⃣ Update session
        history = getattr(session, "suggested_topics", [])
        history.append({"type": "Web", "query": query, "doc_type": doc_type.value})
        manager.update_session(session_id, {"suggested_topics": history})

        # 4️⃣ Return session-aware response
        return JSONResponse({
            "session_id": session_id,
            "result": result,
            "session_history": history
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "Failed to summarize web content", "details": str(e)})


# ---------------------------------------------------------------------------
# 📝 Text Summarization
# ---------------------------------------------------------------------------
@router.post("/text")
async def summarize_text(
    request: Request,
    text: str = Form(...),
    doc_type: DocumentTypeEnum = Form(...),
    pages: int = Form(2)
):
    """
    Process and summarize plain text.
    Session-aware — remembers text processing history per user.
    """
    try:
        # 1️⃣ Manage session
        manager = SessionStateManager.get_instance()
        session_id = request.headers.get("X-Session-ID")
        session_id = manager.get_or_create_session(session_id)
        session = manager.get_session(session_id)

        # 2️⃣ Process text
        service = TextService()
        result = await service.process_text(text, doc_type, pages)

        # 3️⃣ Update session (record processed text)
        text_history = getattr(session, "suggested_topics", [])
        text_history.append({"type": "Text", "length": len(text), "doc_type": doc_type.value})
        manager.update_session(session_id, {"suggested_topics": text_history})

        # 4️⃣ Return response
        return JSONResponse({
            "session_id": session_id,
            "result": result,
            "session_texts": text_history
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "Failed to summarize text", "details": str(e)})
