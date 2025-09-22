# APIManager.py
from fastapi import UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi import APIRouter
import os
from datetime import datetime
from enum import Enum
from typing import Optional

from sources.pdf_loader import PDFManager
from sources.video_transcript import YouTubeTranscriptFetcher
from sources.web_search import WebSearchManager
from sources.retriever import VectorRetriever
from summarizer.llm_summarizer import LLMSummarizer
from summarizer.docx_generator import SummaryDocxBuilder
from document_system import document_system
from config import Config

class BaseAPIManager:
    def __init__(self):
        self.retriever = VectorRetriever()
        self.summarizer = LLMSummarizer()
        self.document_types = Enum(
            "DocumentTypeEnum",
            {t.replace(" ", "_"): t for t in document_system.list_document_types()}
        )

    def save_docx(self, summary: dict, prefix: str, doc_type: str) -> str:
        """Save summary as DOCX under reports directory with timestamped filename."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_doc_type = doc_type.replace(" ", "_")
        filename = f"{prefix}_summary_{safe_doc_type}_{timestamp}.docx"
        file_path = os.path.join(Config.REPORTS_DIR, filename)

        builder = SummaryDocxBuilder(summary, file_path)
        builder.build()
        return filename

class PDFClass(BaseAPIManager):
    async def process(self, file: UploadFile, doc_type: str, pages: int = 2):
        try:
            text = await PDFManager().extract_text(file=file)
            self.retriever.process_text(
                text,
                metadata={"source": "pdf", "query": file.filename, "doc_type": doc_type}
            )
            summary = self.summarizer.summarize_with_structure(self.retriever, text, doc_type, pages)
            filename = self.save_docx(summary, "pdf", doc_type)
            return {"raw_text": text, "summary": summary, "download_link": f"/download/{filename}"}
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})

class YouTubeClass(BaseAPIManager):
    async def process(self, url: str, doc_type: str, pages: int = 2):
        try:
            text = YouTubeTranscriptFetcher().fetch(url)
            self.retriever.process_text(
                text,
                metadata={"source": "video", "query": url, "doc_type": doc_type}
            )
            summary = self.summarizer.summarize_with_structure(self.retriever, text, doc_type, pages)
            filename = self.save_docx(summary, "youtube", doc_type)
            return {"raw_text": text, "summary": summary, "download_link": f"/download/{filename}"}
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})

class WebClass(BaseAPIManager):
    async def process(self, query: str, doc_type: str, pages: int = 2):
        try:
            search_manager = WebSearchManager()
            text = search_manager.run(query)
            self.retriever.process_text(
                text,
                metadata={"source": "web", "query": query, "doc_type": doc_type}
            )
            summary = self.summarizer.summarize_with_structure(self.retriever, query, doc_type, pages)
            filename = self.save_docx(summary, "web", doc_type)
            return {
                "query": query,
                "raw_text": text[:1000] + "..." if len(text) > 1000 else text,
                "summary": summary,
                "download_link": f"/download/{filename}"
            }
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})

class TextClass(BaseAPIManager):
    async def process(self, text: str, doc_type: str, pages: int = 2):
        try:
            self.retriever.process_text(     
                text,
                metadata={"source": "text", "query": text, "doc_type": doc_type}
            )
            summary = self.summarizer.summarize_with_structure(self.retriever, text, doc_type, pages)
            filename = self.save_docx(summary, "text", doc_type)
            return {"raw_text": text, "summary": summary, "download_link": f"/download/{filename}"}
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})

# Shared instance for download endpoint
api_manager = BaseAPIManager()