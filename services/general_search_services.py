# services/general_search_services.py
from fastapi import Form, UploadFile, Header, Depends
from fastapi.responses import JSONResponse
from datetime import datetime
import os
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel

from config import Config
from document_system import document_system
from docx_generator import SummaryDocxBuilder
from sources.retriever import VectorRetriever
from sources.video_transcript import YouTubeTranscriptFetcher, YouTubeTranscriptManager
from sources.web_search import WebSearchManager
from sources.pdf_loader import PDFManager
from llm_summarizer import LLMSummarizer
from app_state import AppStateManager

# Document Type Enum
DocumentTypeEnum = Enum(
    "DocumentTypeEnum",
    {t.replace(" ", "_"): t for t in document_system.list_document_types()}
)

class SearchResult(BaseModel):
    """Model for search results."""
    content: str
    metadata: Dict[str, Any]
    doc_type: str
    source: str
    timestamp: str

def get_doc_type_str(doc_type) -> str:
    """Helper to safely get string value from either enum or string."""
    return doc_type.value if hasattr(doc_type, 'value') else str(doc_type)

class BaseAPIManager:
    """Base class for all document processing services."""
    def __init__(self, app_state: Optional[AppStateManager] = None):
        self.retriever = VectorRetriever()
        self.summarizer = LLMSummarizer()
        self.document_types = DocumentTypeEnum
        self.app_state = app_state or AppStateManager()

    def _init_session(self, session_id: Optional[str] = None) -> str:
        """Initialize or retrieve session."""
        if session_id:
            session_data = self.app_state.get_user_state(session_id)
            if not session_data:
                raise ValueError("Invalid session ID")
        else:
            session_id = f"search_{int(datetime.now().timestamp())}"
            session_data = self.app_state.get_user_state(session_id)
            session_data.synthesis_storage.update({
                "created_at": datetime.now().isoformat(),
                "type": "search_analysis"
            })
        return session_id

    def _update_session(self, session_id: str, result: Dict[str, Any]) -> None:
        """Update session with search results."""
        session_data = self.app_state.get_user_state(session_id)
        if "search_results" not in session_data.synthesis_storage:
            session_data.synthesis_storage["search_results"] = []
        
        search_result = SearchResult(
            content=result.get("summary", ""),
            metadata={
                "doc_type": result.get("doc_type"),
                "source": result.get("source", "unknown"),
                "file_name": result.get("file_name", "")
            },
            doc_type=result.get("doc_type", "unknown"),
            source=result.get("source", "unknown"),
            timestamp=datetime.now().isoformat()
        )
        
        session_data.synthesis_storage["search_results"].append(search_result.dict())
        session_data.synthesis_storage["last_activity"] = datetime.now().isoformat()

    async def _process_content(self, content: str, doc_type: str, pages: int = 2) -> Dict[str, Any]:
        """Common processing logic for all content types."""
        # Your existing processing logic here
        pass

    def save_docx(self, summary: dict, prefix: str, doc_type: str) -> str:
        """Save summary as DOCX under reports directory with timestamped filename."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_doc_type = doc_type.replace(" ", "_")
        filename = f"{prefix}_summary_{safe_doc_type}_{timestamp}.docx"
        file_path = os.path.join(Config.REPORTS_DIR, filename)

        builder = SummaryDocxBuilder(summary, file_path)
        builder.build()
        return filename

class PDFService(BaseAPIManager):
    """Service for processing PDF documents."""
    async def process_pdf(
        self,
        file: UploadFile,
        doc_type: DocumentTypeEnum = Form(...),
        pages: int = 2,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            session_id = self._init_session(session_id)
            text = await PDFManager().extract_text(file=file)
            result = await self._process_content(text, get_doc_type_str(doc_type), pages)
            
            # Save to session
            result.update({
                "source": "pdf",
                "file_name": file.filename
            })
            self._update_session(session_id, result)
            
            return {
                "session_id": session_id,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

class YouTubeService(BaseAPIManager):
    """Service for processing YouTube videos."""
    async def process_youtube(
        self,
        query: str,
        doc_type: DocumentTypeEnum = Form(...),
        pages: int = 2,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            session_id = self._init_session(session_id)
            transcript = await YouTubeTranscriptManager().get_transcript(query)
            result = await self._process_content(transcript, get_doc_type_str(doc_type), pages)
            
            # Save to session
            result.update({
                "source": "youtube",
                "video_id": query
            })
            self._update_session(session_id, result)
            
            return {
                "session_id": session_id,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

class WebService(BaseAPIManager):
    """Service for processing web content."""
    async def process_web(
        self,
        query: str,
        doc_type: DocumentTypeEnum = Form(...),
        pages: int = Form(2),
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            session_id = self._init_session(session_id)
            content = await WebSearchManager().search(query, max_results=pages)
            result = await self._process_content(content, get_doc_type_str(doc_type), pages)
            
            # Save to session
            result.update({
                "source": "web",
                "query": query
            })
            self._update_session(session_id, result)
            
            return {
                "session_id": session_id,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

class TextService(BaseAPIManager):
    """Service for processing plain text."""
    async def process_text(
        self,
        text: str,
        doc_type: DocumentTypeEnum = Form(...),
        pages: int = 2,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            session_id = self._init_session(session_id)
            result = await self._process_content(text, get_doc_type_str(doc_type), pages)
            
            # Save to session
            result.update({
                "source": "text",
                "content_preview": text[:100] + "..." if len(text) > 100 else text
            })
            self._update_session(session_id, result)
            
            return {
                "session_id": session_id,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# Singleton instances for easy import
pdf_service = PDFService()
youtube_service = YouTubeService()
web_service = WebService()
text_service = TextService()