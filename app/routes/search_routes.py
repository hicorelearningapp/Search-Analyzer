# app/api/search_routes.py
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from services.search_service import SearchService
from services.models import SearchResponse, Paper, SearchServiceError
from app_state import SessionStateManager

router = APIRouter(prefix="/search", tags=["Search API"])

# -------------------- Pydantic Models --------------------

class SelectPapersRequest(BaseModel):
    """Request model for selecting papers."""
    paper_ids: List[str] = Field(..., description="List of paper IDs to select")

class SelectPapersResponse(BaseModel):
    """Response model for selected papers."""
    selected_count: int
    selected_papers: List[Dict[str, Any]]

# -------------------- Endpoints --------------------

@router.post("/project_start")
async def project_start(request: Request,topic: str = Form(...),limit: int = Form(5, ge=1, le=10)):
    """
    Start a new research project by searching for papers on the given topic.
    Includes session handling so each user's searches are isolated.
    """
    try:
        # Manage session
        manager = SessionStateManager.get_instance()
        session_id = request.headers.get("X-Session-ID")
        session_id = manager.get_or_create_session(session_id)
        session = manager.get_session(session_id)

        # Run the search
        sources = ["semantic", "arxiv", "openalex"]
        results = await SearchService.search_multiple_sources(query=topic,sources=sources,limit=limit)

        # Update session (record query)
        keywords = getattr(session, "keywords", [])
        keywords.append(topic)
        manager.update_session(session_id, {"keywords": keywords})

        # Build response
        response = {"session_id": session_id,"query": topic,"papers": results[:limit],"total_results": len(results),"session_keywords": keywords}
        return JSONResponse(response)

    except SearchServiceError as e:
        raise HTTPException(status_code=400, detail={"error": "Search failed", "details": str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "Failed to perform search", "details": str(e)})

# -----------------------------------------------------------

@router.post("/search_papers")
async def search_papers(request: Request,topic: str = Form(...),sources: str = Form("semantic,arxiv,openalex"),limit: int = Form(6, ge=1, le=20)):
    """
    Search for papers across multiple academic sources.
    Session-aware — remembers user's queries for later recall.
    """
    try:
        # Manage session
        manager = SessionStateManager.get_instance()
        session_id = request.headers.get("X-Session-ID")
        session_id = manager.get_or_create_session(session_id)
        session = manager.get_session(session_id)

        # Parse & search
        source_list = [s.strip() for s in sources.split(",") if s.strip()]
        results = await SearchService.search_multiple_sources(
            query=topic,
            sources=source_list,
            limit=limit
        )

        # Update session keywords
        keywords = getattr(session, "keywords", [])
        if topic not in keywords:
            keywords.append(topic)
        manager.update_session(session_id, {"keywords": keywords})

        # Return structured response
        return JSONResponse({
            "session_id": session_id,
            "query": topic,
            "papers": results[:limit],
            "total_results": len(results),
            "session_keywords": keywords
        })

    except SearchServiceError as e:
        raise HTTPException(status_code=400, detail={"error": "Search failed", "details": str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "Search failed", "details": str(e)})

# -----------------------------------------------------------

@router.post("/select_papers")
async def select_papers(
    request: Request,
    select_request: SelectPapersRequest
):
    """
    Select specific papers from search results for further analysis.
    Each selection is recorded per-session.
    """
    try:
        # Manage session
        manager = SessionStateManager.get_instance()
        session_id = request.headers.get("X-Session-ID")
        session_id = manager.get_or_create_session(session_id)
        session = manager.get_session(session_id)

        # Record selections
        history = getattr(session, "suggested_topics", [])
        selection_entry = {
            "action": "select_papers",
            "paper_ids": select_request.paper_ids,
            "timestamp": session.last_activity
        }
        history.append(selection_entry)
        manager.update_session(session_id, {"suggested_topics": history})

        # Return result
        return JSONResponse({
            "session_id": session_id,
            "selected_count": len(select_request.paper_ids),
            "selected_papers": [],  # Placeholder for fetched paper objects
            "session_history": history
        })

    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": "Failed to select papers", "details": str(e)})

# -----------------------------------------------------------

@router.get("/top_researchers")
async def top_researchers(
    request: Request,
    topic: str,
    limit: int = 5
):
    """
    Find top researchers in a given field.
    Session-tracked — stores what topic user explored.
    """
    try:
        # Manage session
        manager = SessionStateManager.get_instance()
        session_id = request.headers.get("X-Session-ID")
        session_id = manager.get_or_create_session(session_id)
        session = manager.get_session(session_id)

        # Fetch data
        researchers = await SearchService.find_top_researchers(query=topic, limit=limit)

        # Log activity
        keywords = getattr(session, "keywords", [])
        if topic not in keywords:
            keywords.append(topic)
        manager.update_session(session_id, {"keywords": keywords})

        # Return response
        return JSONResponse({
            "session_id": session_id,
            "topic": topic,
            "top_researchers": researchers,
            "session_keywords": keywords
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "Failed to fetch researchers", "details": str(e)})
