# api.py
import os
from fastapi.responses import FileResponse
from fastapi import APIRouter, UploadFile, Form
from fastapi.responses import JSONResponse

from sources.pdf_loader import PDFManager
from sources.video_transcript import YouTubeTranscriptFetcher as TranscriptFetcher
from sources.web_search import WebSearchManager
from sources.retriever import VectorRetriever
from summarizer.llm_summarizer import LLMSummarizer
from config import Config


router = APIRouter()
retriever = VectorRetriever()
summarizer = LLMSummarizer()


@router.post("/pdf")
async def summarize_pdf(file: UploadFile, doc_type: str = Form(...), pages: int = Form(2)):
    try:
        text = await PDFManager().extract_text(file=file)
        retriever.process_text(text, source="pdf")
        summary = summarizer.summarize_with_structure(text, doc_type, pages)

        return {"raw_text": text, "summary": summary}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/youtube")
async def summarize_youtube(url: str = Form(...), doc_type: str = Form(...), pages: int = Form(2)):
    try:
        text = TranscriptFetcher().fetch(url)
        retriever.process_text(text, source="video")
        summary = summarizer.summarize_with_structure(text, doc_type, pages)

        return {"raw_text": text, "summary": summary}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/web")
async def summarize_web(query: str = Form(...), doc_type: str = Form(...), pages: int = Form(2)):
    try:
        text = WebSearchManager().run(query)
        retriever.process_text(text, metadata={"source": "web", "query": query, "doc_type": doc_type})
        summary = summarizer.summarize_with_structure(text, doc_type, pages)

        return {"raw_text": text, "summary": summary}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/text")
async def summarize_text(text: str = Form(...), doc_type: str = Form(...), pages: int = Form(2)):
    try:
        retriever.process_text(text, source="text")
        summary = summarizer.summarize_with_structure(text, doc_type, pages)

        return {"raw_text": text, "summary": summary}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.get("/download/{filename}")
async def download_file(filename: str):
    """
    Serve a generated .docx file with the correct MIME type
    so Word doesn't mark it as corrupted on Azure.
    """
    file_path = os.path.join(Config.REPORTS_DIR, filename)

    if not os.path.exists(file_path):
        return {"error": "File not found"}

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
