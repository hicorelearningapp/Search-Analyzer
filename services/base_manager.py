from fastapi.responses import JSONResponse
from fastapi import UploadFile, Form
from datetime import datetime
import os
from enum import Enum
from typing import Optional
from services.types import DocumentTypeEnum
from fastapi import Form
from services.types import DocumentTypeEnum

from config import Config
from document_system import document_system
from docx_generator import SummaryDocxBuilder

class BaseAPIManager:
    def __init__(self):
        from retriever import VectorRetriever
        from llm_summarizer import LLMSummarizer
        
        self.retriever = VectorRetriever()
        self.summarizer = LLMSummarizer()
        self.document_types = DocumentTypeEnum

    def save_docx(self, summary: dict, prefix: str, doc_type: str) -> str:
        """Save summary as DOCX under reports directory with timestamped filename."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_doc_type = doc_type.replace(" ", "_")
        filename = f"{prefix}_summary_{safe_doc_type}_{timestamp}.docx"
        file_path = os.path.join(Config.REPORTS_DIR, filename)

        builder = SummaryDocxBuilder(summary, file_path)
        builder.build()
        return filename
