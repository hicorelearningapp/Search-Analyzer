# api.py
import os
from datetime import datetime
from fastapi.responses import FileResponse, JSONResponse
from fastapi import APIRouter, UploadFile, Form

from sources.pdf_loader import PDFManager
from sources.video_transcript import YouTubeTranscriptFetcher as TranscriptFetcher
from sources.web_search import WebSearchManager
from sources.retriever import VectorRetriever
from summarizer.llm_summarizer import LLMSummarizer
from summarizer.docx_generator import SummaryDocxBuilder  # ⬅ use your formatter
from config import Config


router = APIRouter()
retriever = VectorRetriever()
summarizer = LLMSummarizer()


def save_docx(summary: dict, prefix: str, doc_type: str) -> str:
    """Save summary as DOCX under reports directory with timestamped filename."""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_doc_type = doc_type.replace(" ", "_")
    filename = f"{prefix}_summary_{safe_doc_type}_{timestamp}.docx"
    file_path = os.path.join(Config.REPORTS_DIR, filename)

    builder = SummaryDocxBuilder(summary, file_path)
    builder.build()
    return filename


@router.post("/pdf")
async def summarize_pdf(file: UploadFile, doc_type: str = Form(...), pages: int = Form(2)):
    try:
        text = await PDFManager().extract_text(file=file)
        retriever.process_text(
            text,
            metadata={"source":"pdf","query": file.filename, "doc_type": doc_type}
        )
        summary = summarizer.summarize_with_structure(text, doc_type, pages)

        filename = save_docx(summary, "pdf", doc_type)
        return {"raw_text": text, "summary": summary, "download_link": f"/download/{filename}"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/youtube")
async def summarize_youtube(url: str = Form(...), doc_type: str = Form(...), pages: int = Form(2)):
    try:
        text = TranscriptFetcher().fetch(url)
        retriever.process_text(
            text,
            metadata={"source":"video","query": url, "doc_type": doc_type}
        )
        summary = summarizer.summarize_with_structure(text, doc_type, pages)

        filename = save_docx(summary, "youtube", doc_type)
        return {"raw_text": text, "summary": summary, "download_link": f"/download/{filename}"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/web")
async def summarize_web(query: str = Form(...), doc_type: str = Form(...), pages: int = Form(2)):
    try:
        search_manager = WebSearchManager()
        text = search_manager.run(query)
        retriever.process_text(
            text,
            metadata={"source": "web", "query": query, "doc_type": doc_type}
        )
        summary = summarizer.summarize_with_structure(text, doc_type, pages)

        filename = save_docx(summary, "web", doc_type)
        return {
            "query": query,
            "raw_text": text[:1000] + "..." if len(text) > 1000 else text,
            "summary": summary,
            "download_link": f"/download/{filename}"
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/text")
async def summarize_text(text: str = Form(...), doc_type: str = Form(...), pages: int = Form(2)):
    try:
        retriever.process_text(     
            text,
            metadata={"source":"text","query": text, "doc_type": doc_type}
        )
        summary = summarizer.summarize_with_structure(text, doc_type, pages)

        filename = save_docx(summary, "text", doc_type)
        return {"raw_text": text, "summary": summary, "download_link": f"/download/{filename}"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.get("/download/{filename}")
async def download_file(filename: str):
    """Serve generated DOCX files with the correct MIME type."""
    file_path = os.path.join(Config.REPORTS_DIR, filename)
    if not os.path.exists(file_path):
        return {"error": "File not found"}

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
