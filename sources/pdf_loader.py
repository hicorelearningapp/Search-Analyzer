# sources/pdf_loader.py
import io
import tempfile
from enum import Enum
from typing import Optional, Union, List
from fastapi import UploadFile
from PyPDF2 import PdfReader
from langchain_community.document_loaders import PyPDFLoader
from pydantic import BaseModel

# Local imports
from .retriever import RetrievalMethod, VectorRetriever


class PDFExtractionResult(BaseModel):
    """Result of PDF text extraction."""
    text: str
    metadata: dict = {}


class PDFExtractor:
    @staticmethod
    def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> PDFExtractionResult:
        """Extract plain text from PDF bytes using PyPDF2."""
        text_parts = []
        metadata = {
            "source": "bytes",
            "extraction_method": "PyPDF2",
            "page_count": 0
        }
        
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            reader = PdfReader(pdf_file)
            metadata["page_count"] = len(reader.pages)
            
            for i, page in enumerate(reader.pages):
                try:
                    text = page.extract_text() or ""
                    if text.strip():
                        text_parts.append(text)
                except Exception as e:
                    print(f"Error extracting text from page {i+1}: {str(e)}")
                    continue
                    
            return PDFExtractionResult(
                text="\n".join(text_parts),
                metadata=metadata
            )
        except Exception as e:
            raise RuntimeError(f"Error reading PDF: {e}")

    @staticmethod
    def extract_text_with_langchain(file_path: str) -> PDFExtractionResult:
        """Extract text using LangChain's PyPDFLoader."""
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            metadata = {
                "source": file_path,
                "extraction_method": "PyPDFLoader",
                "page_count": len(documents)
            }
            
            text = "\n".join(
                doc.page_content 
                for doc in documents 
                if doc.page_content.strip()
            )
            
            return PDFExtractionResult(
                text=text,
                metadata=metadata
            )
        except Exception as e:
            raise RuntimeError(f"Error extracting text with LangChain: {e}")

class PDFManager:
    def __init__(self, use_langchain: bool = False):
        self.use_langchain = use_langchain

    async def extract_text(
        self, 
        file_path: Optional[str] = None, 
        file: Optional[UploadFile] = None
    ) -> str:   # <-- return string, not model
        if not file_path and not file:
            raise ValueError("Either file_path or file must be provided")

        if file_path:
            if self.use_langchain:
                result = PDFExtractor.extract_text_with_langchain(file_path)
            else:
                with open(file_path, "rb") as f:
                    pdf_bytes = f.read()
                result = PDFExtractor.extract_text_from_pdf_bytes(pdf_bytes)
        else:
            pdf_bytes = await file.read()
            result = PDFExtractor.extract_text_from_pdf_bytes(pdf_bytes)

        return result.text