# app/api/search_routes.py
from fastapi import APIRouter, Form, HTTPException, Depends
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from services.search_service import SearchService
from services.models import SearchResponse, SelectPapersRequest, Paper, SelectPapersResponse, SearchServiceError
from app_state import AppStateManager

router = APIRouter()

# Endpoints
@router.post("/project_start", response_model=SearchResponse)
async def project_start(topic: str = Form(...), limit: int = Form(5, ge=1, le=10)):
    """
    Start a new research project by searching for papers on the given topic.
    """
    try:
        # Use all available sources for initial search
        sources = ["semantic", "arxiv", "openalex"]
        results = await SearchService.search_multiple_sources(
            query=topic,
            sources=sources,
            limit=limit
        )
        return {
            "query": topic,
            "papers": results[:limit],
            "total_results": len(results)
        }
    except SearchServiceError as e:
        raise HTTPException(
            status_code=400,
            detail={"error": "Search failed", "details": str(e)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to perform search", "details": str(e)}
        )

@router.post("/search_papers", response_model=SearchResponse)
async def search_papers(
    topic: str = Form(...),
    sources: str = Form("semantic,arxiv,openalex"),
    limit: int = Form(6, ge=1, le=20)
):
    """
    Search for papers across multiple academic sources.
    """
    try:
        source_list = [s.strip() for s in sources.split(",") if s.strip()]
        results = await SearchService.search_multiple_sources(
            query=topic,
            sources=source_list,
            limit=limit
        )
        return {
            "query": topic,
            "papers": results[:limit],
            "total_results": len(results)
        }
    except SearchServiceError as e:
        raise HTTPException(
            status_code=400,
            detail={"error": "Search failed", "details": str(e)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Search failed", "details": str(e)}
        )

@router.post("/select_papers", response_model=SelectPapersResponse)
async def select_papers(request: SelectPapersRequest):
    """
    Select specific papers from search results for further analysis.
    """
    try:
        # In a real implementation, you would validate paper IDs and fetch the actual paper objects
        # For now, we'll just return the count of selected papers
        return {
            "selected_count": len(request.paper_ids),
            "selected_papers": [],  # You would fetch the actual paper objects here
            "session_id": request.session_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={"error": "Failed to select papers", "details": str(e)}
        )

@router.get("/top_researchers", response_model=List[Dict[str, Any]])
async def top_researchers(topic: str, limit: int = 5):
    """
    Find top researchers in a given field.
    """
    try:
        return await SearchService.find_top_researchers(query=topic, limit=limit)
    except SearchError as e:
        raise HTTPException(
            status_code=400,
            detail={"error": "Failed to fetch researchers", "details": str(e)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to fetch researchers", "details": str(e)}
        )