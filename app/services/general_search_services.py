from enum import Enum
from fastapi import UploadFile, HTTPException, Form
from typing import Dict, List, Any, Optional
import os
from datetime import datetime
import tempfile

from utils.vector_retriever import VectorRetriever
from utils.youtube_transcript import YouTubeTranscriptManager
from utils.web_search import WebSearchManager
from utils.pdf_loader import PDFManager
from utils.llm_summarizer import LLMSummarizer

# Document Type Enum
DocumentTypeEnum = Enum(
    'DocumentTypeEnum', 
    'RESEARCH_PAPER TECHNICAL_DOCUMENTATION BLOG_POST TUTORIAL OTHER'
)

def get_doc_type_str(doc_type: DocumentTypeEnum) -> str:
    """Convert DocumentTypeEnum to string representation."""
    return doc_type.name.lower()

def generate_temp_filename(extension: str = '.txt') -> str:
    """Generate a temporary filename with the given extension."""
    with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as temp_file:
        return temp_file.name

class BaseAPIManager:
    """Base class for all document processing services."""
    def __init__(self):
        self.retriever = VectorRetriever()
        self.summarizer = LLMSummarizer()
        self.document_types = DocumentTypeEnum

    async def _process_content(self, content: str, doc_type: str, pages: int = 2) -> Dict[str, Any]:
        """Common processing logic for all content types."""
        try:
            # Save content to a temporary file
            temp_file = generate_temp_filename()
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(content)

            # Process the content
            summary = await self.summarizer.summarize(
                content=content,
                doc_type=doc_type,
                max_pages=pages
            )

            # Clean up
            if os.path.exists(temp_file):
                os.unlink(temp_file)

            return {
                "summary": summary,
                "doc_type": doc_type,
                "processed_at": datetime.now().isoformat()
            }
        except Exception as e:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
            raise HTTPException(status_code=500, detail=str(e))

class PDFService(BaseAPIManager):
    """Service for processing PDF documents."""
    async def process_pdf(
        self,
        file: UploadFile,
        doc_type: DocumentTypeEnum = Form(...),
        pages: int = 2
    ) -> Dict[str, Any]:
        try:
            text = await PDFManager().extract_text(file=file)
            result = await self._process_content(text, get_doc_type_str(doc_type), pages)
            
            return {
                "result": {
                    **result,
                    "source": "pdf",
                    "file_name": file.filename
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

class YouTubeService(BaseAPIManager):
    """Service for processing YouTube videos."""
    async def process_youtube(
        self,
        query: str,
        doc_type: DocumentTypeEnum = Form(...),
        pages: int = 2
    ) -> Dict[str, Any]:
        try:
            transcript = await YouTubeTranscriptManager().get_transcript(query)
            result = await self._process_content(transcript, get_doc_type_str(doc_type), pages)
            
            return {
                "result": {
                    **result,
                    "source": "youtube",
                    "video_id": query
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

class WebService(BaseAPIManager):
    """Service for processing web content."""
    async def process_web(
        self,
        query: str,
        doc_type: DocumentTypeEnum = Form(...),
        pages: int = 2
    ) -> Dict[str, Any]:
        try:
            content = await WebSearchManager().search(query, max_results=pages)
            result = await self._process_content(content, get_doc_type_str(doc_type), pages)
            
            return {
                "result": {
                    **result,
                    "source": "web",
                    "query": query
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

class TextService(BaseAPIManager):
    """Service for processing plain text."""
    async def process_text(
        self,
        text: str,
        doc_type: DocumentTypeEnum = Form(...),
        pages: int = 2
    ) -> Dict[str, Any]:
        try:
            result = await self._process_content(text, get_doc_type_str(doc_type), pages)
            
            return {
                "result": {
                    **result,
                    "source": "text",
                    "content_preview": text[:100] + "..." if len(text) > 100 else text
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))