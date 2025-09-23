from fastapi import APIRouter, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from enum import Enum
import os

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

router = APIRouter()

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

@router.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join("reports", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
