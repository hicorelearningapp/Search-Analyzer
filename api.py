# api.py
from fastapi import APIRouter, UploadFile, Form, HTTPException
from datetime import datetime
# <<<<<<< HEAD
from typing import Optional

from sources.pdf_loader import PDFSummarizer, PDFManager
from sources.video_transcript import YouTubeTranscriptManager
from sources.web_search import WebSearchManager
from summarizer.common import SummarizerPipeline

router = APIRouter()

pdf_summarizer = PDFSummarizer()
pdf_manager = PDFManager()
youtube_manager = YouTubeTranscriptManager(max_results=10)
web_search_manager = WebSearchManager(max_results=10, max_snippet_length=600)
summarizer_pipeline = SummarizerPipeline()
# =======
# import traceback

# router = APIRouter()

# # Safe imports (prevent Azure crash if module not found)
# try:
#     from sources.pdf_loader import PDFSummarizer
#     from sources.video_transcript import YouTubeTranscriptManager
#     from sources.web_search import WebSearchManager
#     from summarizer.common import SummarizerPipeline

#     pdf_summarizer = PDFSummarizer()
#     youtube_manager = YouTubeTranscriptManager(max_results=10)
#     web_search_manager = WebSearchManager(max_results=10, max_snippet_length=600)
#     summarizer_pipeline = SummarizerPipeline()

# except Exception as e:
#     print("❌ Import error in api.py:", str(e))
#     print(traceback.format_exc())

#     # Dummy fallbacks so app still runs
#     pdf_summarizer = youtube_manager = web_search_manager = summarizer_pipeline = None

# >>>>>>> 255d039d11e581b6b120a8ee6eeb31377b20dadc

@router.get("/health")
async def health_check():
    """Simple health check"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@router.get("/web")
def summarize_web(topic: str, doc_type: str = "Executive Summary", pages: int = 2, download: bool = False):
    if not web_search_manager or not summarizer_pipeline:
        raise HTTPException(status_code=500, detail="Summarizer not initialized (import error)")
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
async def summarize_pdf_route(file: UploadFile, doc_type: str = Form(...), pages: int = Form(2), download: bool = Form(False)):
    if not pdf_summarizer:
        raise HTTPException(status_code=500, detail="PDF summarizer not initialized (import error)")
    try:
        text = pdf_manager.get_text_from_pdf(file)
        return summarizer_pipeline.run(text=text, doc_type=doc_type, pages=pages, label="PDF", outfile_name="pdf", download=download)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/youtube")
def summarize_youtube(query: str = Form(...), doc_type: str = Form("Executive Summary"), pages: int = Form(2), download: bool = Form(False)):
    if not youtube_manager or not summarizer_pipeline:
        raise HTTPException(status_code=500, detail="YouTube summarizer not initialized (import error)")
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
def summarize_text(content: str = Form(...), doc_type: str = Form("Executive Summary"), pages: int = Form(2), download: bool = Form(False)):
    if not summarizer_pipeline:
        raise HTTPException(status_code=500, detail="Text summarizer not initialized (import error)")
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
