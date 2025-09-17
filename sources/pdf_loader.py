# sources/pdf_loader.py
import io
import os
from typing import Optional
from fastapi import UploadFile
from PyPDF2 import PdfReader
from .retriever import VectorRetriever


class PDFExtractor:
    @staticmethod
    def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
        """Extract plain text from PDF bytes and return as a string."""
        text_parts = []
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                try:
                    t = page.extract_text() or ""
                    if t.strip():
                        text_parts.append(t)
                except Exception:
                    # skip pages we cannot parse
                    continue
        except Exception as e:
            raise RuntimeError(f"Error reading PDF: {e}")
        return "\n".join(text_parts)


class PDFManager:
    def __init__(self, chunk_size: int = 500, retriever: Optional[VectorRetriever] = None):
      
        self.chunk_size = chunk_size
        self.retriever = retriever or VectorRetriever()

    async def get_text_from_pdf(self, file: UploadFile) -> str:

        file_bytes = await file.read()
        text = PDFExtractor.extract_text_from_pdf_bytes(file_bytes)

        if text.strip():
            self.retriever.build_index(text, chunk_size=self.chunk_size)

        return text
