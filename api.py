# api.py
from fastapi import APIRouter, UploadFile, Form, HTTPException
from datetime import datetime

from sources.pdf_loader import PDFSummarizer
from sources.video_transcript import YouTubeTranscriptManager
from sources.web_search import WebSearchManager
from summarizer.common import SummarizerPipeline

# Create router
router = APIRouter()

# Instantiate services once
pdf_summarizer = PDFSummarizer()
youtube_manager = YouTubeTranscriptManager(max_results=10)
web_search_manager = WebSearchManager(max_results=10, max_snippet_length=600)
summarizer_pipeline = SummarizerPipeline()


@router.get("/")
async def root():
    """Root route for quick check"""
    return {"message": "Search Analyzer API is running", "docs": "/docs"}


@router.get("/health")
async def health_check():
    """Simple health check"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@router.get("/web")
def summarize_web(
    topic: str,
    doc_type: str = "Executive Summary",
    pages: int = 2,
    download: bool = False
):
    """Summarize information from a web search"""
    try:
        llm_input = web_search_manager.run(topic)
        return summarizer_pipeline.run(
            text=llm_input,
            doc_type=doc_type,
            pages=pages,
            label=topic,
            outfile_name=topic,
            download=download
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pdf")
async def summarize_pdf_route(
    file: UploadFile,
    doc_type: str = Form(...),
    pages: int = Form(2),
    download: bool = Form(False)
):
    """Summarize an uploaded PDF file"""
    try:
        return await pdf_summarizer.summarize_pdf(file, doc_type, pages, download)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/youtube")
def summarize_youtube(
    query: str = Form(...),
    doc_type: str = Form("Executive Summary"),
    pages: int = Form(2),
    download: bool = Form(False)
):
    """Summarize transcripts from YouTube search results"""
    try:
        text = youtube_manager.get_transcripts_from_search(query)
        return summarizer_pipeline.run(
            text=text,
            doc_type=doc_type,
            pages=pages,
            label="YouTube Videos",
            outfile_name="youtube",
            download=download
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/text")
def summarize_text(
    content: str = Form(...),
    doc_type: str = Form("Executive Summary"),
    pages: int = Form(2),
    download: bool = Form(False)
):
    """Summarize raw text provided by the user"""
    try:
        return summarizer_pipeline.run(
            text=content,
            doc_type=doc_type,
            pages=pages,
            label="User Text",
            outfile_name="text",
            download=download
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
