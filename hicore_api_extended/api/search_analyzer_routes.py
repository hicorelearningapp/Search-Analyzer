from fastapi import APIRouter, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from enum import Enum
import os
import sys

# Add the Search-Analyzer directory to the path
search_analyzer_path = os.path.join(os.path.dirname(__file__), "..", "..", "Search-Analyzer")
sys.path.append(search_analyzer_path)

from document_system import document_system
from services.pdf_service import PDFClass
from services.youtube_service import YouTubeClass
from services.web_service import WebClass
from services.text_service import TextClass

# Initialize services
pdf_service = PDFClass()
youtube_service = YouTubeClass()
web_service = WebClass()
text_service = TextClass()

router = APIRouter(prefix="/search-analyzer", tags=["Search Analyzer"])

# Create DocumentTypeEnum for API documentation
DocumentTypeEnum = Enum(
    "DocumentTypeEnum",
    {t.replace(" ", "_"): t for t in document_system.list_document_types()}
)

@router.post("/pdf")
async def summarize_pdf(file: UploadFile, doc_type: DocumentTypeEnum = Form(...), pages: int = Form(2)):
    try:
        return await pdf_service.process_pdf(file, doc_type, pages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/youtube")
async def summarize_youtube(url: str = Form(...), doc_type: DocumentTypeEnum = Form(...), pages: int = Form(2)):
    try:
        return await youtube_service.process_youtube(url, doc_type, pages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/web")
async def summarize_web(query: str = Form(...), doc_type: DocumentTypeEnum = Form(...), pages: int = Form(2)):
    try:
        return await web_service.process_web(query, doc_type, pages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/text")
async def summarize_text(text: str = Form(...), doc_type: DocumentTypeEnum = Form(...), pages: int = Form(2)):
    try:
        return await text_service.process_text(text, doc_type, pages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
