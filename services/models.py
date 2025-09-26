# services/models.py
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class Paper(BaseModel):
    """Represents a research paper with its metadata."""
    source: str
    title: str
    year: Optional[int] = None
    authors: List[str] = []
    abstract: Optional[str] = None
    url: Optional[str] = None
    doi: Optional[str] = None
    pdf_url: Optional[str] = None
    paperId: Optional[str] = None  # For Semantic Scholar ID

class SearchRequest(BaseModel):
    """Request model for search operations."""
    query: str
    sources: List[str] = ["semantic", "arxiv", "openalex"]
    limit: int = Field(5, ge=1, le=20, description="Number of results to return per source")

class SearchResponse(BaseModel):
    """Response model for search operations."""
    query: str
    papers: List[Paper] = []
    total_results: int = 0

class SelectPapersRequest(BaseModel):
    """Request model for selecting papers from search results."""
    paper_ids: List[str] = Field(..., description="List of paper IDs to select")
    session_id: Optional[str] = Field(None, description="Optional session ID to associate with the selection")

class SelectPapersResponse(BaseModel):
    """Response model for paper selection."""
    selected_count: int
    selected_papers: List[Paper] = []
    session_id: Optional[str] = None

class Researcher(BaseModel):
    """Represents a researcher with their metadata."""
    name: str
    affiliations: List[str] = []
    homepage: Optional[str] = None
    url: Optional[str] = None
    paperCount: Optional[int] = None
    citationCount: Optional[int] = None
    hIndex: Optional[int] = None

class SearchError(BaseModel):
    """Error response model for search operations."""
    error: str
    details: Optional[Dict[str, Any]] = None

class SearchServiceError(Exception):
    """Custom exception for search service failures."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

