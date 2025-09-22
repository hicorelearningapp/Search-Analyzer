# api.py
from fastapi import APIRouter, UploadFile, Form
from fastapi.responses import FileResponse
from enum import Enum
from document_system import document_system
from APIManager import PDFClass, YouTubeClass, WebClass, TextClass, api_manager

router = APIRouter()
pdf_manager = PDFClass()
youtube_manager = YouTubeClass()
web_manager = WebClass()
text_manager = TextClass()

# Create DocumentTypeEnum for API documentation
DocumentTypeEnum = Enum(
    "DocumentTypeEnum",
    {t.replace(" ", "_"): t for t in document_system.list_document_types()}
)

@router.post("/pdf")
async def summarize_pdf(file: UploadFile, doc_type: DocumentTypeEnum = Form(...), pages: int = Form(2)):
    return await pdf_manager.process(file, doc_type.value, pages)

@router.post("/youtube")
async def summarize_youtube(url: str = Form(...), doc_type: DocumentTypeEnum = Form(...), pages: int = Form(2)):
    return await youtube_manager.process(url, doc_type.value, pages)

@router.post("/web")
async def summarize_web(query: str = Form(...), doc_type: DocumentTypeEnum = Form(...), pages: int = Form(2)):
    return await web_manager.process(query, doc_type.value, pages)

@router.post("/text")
async def summarize_text(text: str = Form(...), doc_type: DocumentTypeEnum = Form(...), pages: int = Form(2)):
    return await text_manager.process(text, doc_type.value, pages)

@router.get("/download/{filename}")
async def download_file(filename: str):
    """Serve generated DOCX files with the correct MIME type."""
    return await api_manager.download_file(filename)