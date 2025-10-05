# app/api/routers.py
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
from app_state import SessionStateManager

router = APIRouter(prefix="/papers", tags=["Paper Operations"])


# ---------------------------------------------------------------------------
# 🔍 Paper Search
# ---------------------------------------------------------------------------
@router.post("/search_papers")
async def search_papers(
    request: Request,
    query: str = Form(...),
    source: str = Form("all"),
    papers: List[Dict[str, Any]] = Form(...)
):
    """
    Search for papers based on query and source.
    Session-aware — stores search queries and sources per user.
    """
    try:
        # Manage session
        manager = SessionStateManager.get_instance()
        session_id = request.headers.get("X-Session-ID")
        session_id = manager.get_or_create_session(session_id)
        session = manager.get_session(session_id)

        # Perform mock search
        result = {
            "query": query,
            "source": source,
            "result_count": len(papers),
            "results": papers
        }

        # Update session history
        search_history = getattr(session, "keywords", [])
        search_history.append({"query": query, "source": source, "count": len(papers)})
        manager.update_session(session_id, {"keywords": search_history})

        # Return session-aware response
        return JSONResponse({
            "session_id": session_id,
            "search_summary": result,
            "search_history": search_history
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "Search failed", "details": str(e)})


# ---------------------------------------------------------------------------
# 📑 Select Papers
# ---------------------------------------------------------------------------
@router.post("/select_papers")
async def select_papers(
    request: Request,
    paper_indices: str = Form(...),
    papers: List[Dict[str, Any]] = Form(...)
):
    """
    Select papers from the provided list based on indices.
    Session-aware — remembers user’s selected papers.
    """
    try:
        #   Manage session
        manager = SessionStateManager.get_instance()
        session_id = request.headers.get("X-Session-ID")
        session_id = manager.get_or_create_session(session_id)
        session = manager.get_session(session_id)

        # Process selections
        indices = [int(idx.strip()) for idx in paper_indices.split(",") if idx.strip().isdigit()]
        valid_indices = [i for i in indices if 0 <= i < len(papers)]
        selected_papers = [papers[i] for i in valid_indices]

        # Update session with selected papers
        selected_history = getattr(session, "suggested_topics", [])
        selected_history.append({
            "type": "selection",
            "count": len(valid_indices),
            "indices": valid_indices
        })
        manager.update_session(session_id, {"suggested_topics": selected_history})

        # Return session-aware response
        return JSONResponse({
            "session_id": session_id,
            "selected_count": len(valid_indices),
            "selected_indices": valid_indices,
            "selected_papers": selected_papers,
            "selection_history": selected_history
        })

    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": "Invalid paper indices", "details": str(e)})


# ---------------------------------------------------------------------------
# 🧩 Analyze Methodology
# ---------------------------------------------------------------------------
@router.post("/analyze_methodology")
async def analyze_methodology(
    request: Request,
    papers: List[Dict[str, Any]] = Form(...)
):
    """
    Analyze methodology of selected papers.
    Session-aware — logs analysis activity.
    """
    try:
        if not papers:
            raise HTTPException(status_code=400, detail="No papers provided")

        # Manage session
        manager = SessionStateManager.get_instance()
        session_id = request.headers.get("X-Session-ID")
        session_id = manager.get_or_create_session(session_id)
        session = manager.get_session(session_id)

        # Perform mock analysis
        analysis_result = {
            "paper_count": len(papers),
            "analysis": "Methodology analysis would go here"
        }

        # Update session (record analysis)
        analysis_log = getattr(session, "suggested_topics", [])
        analysis_log.append({"type": "analysis", "count": len(papers)})
        manager.update_session(session_id, {"suggested_topics": analysis_log})

        # Return response
        return JSONResponse({
            "session_id": session_id,
            "analysis_result": analysis_result,
            "analysis_log": analysis_log
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "Analysis failed", "details": str(e)})


# ---------------------------------------------------------------------------
# 🧱 Generate Proposal
# ---------------------------------------------------------------------------
@router.post("/generate_proposal")
async def create_proposal(
    request: Request,
    requirements: str = Form(...),
    papers: List[Dict[str, Any]] = Form(...)
):
    """
    Generate a proposal based on requirements and selected papers.
    Session-aware — tracks generated proposals.
    """
    try:
        if not papers:
            raise HTTPException(status_code=400, detail="No papers provided")

        # Manage session
        manager = SessionStateManager.get_instance()
        session_id = request.headers.get("X-Session-ID")
        session_id = manager.get_or_create_session(session_id)
        session = manager.get_session(session_id)

        # Generate mock proposal
        proposal = {
            "requirements": requirements,
            "paper_count": len(papers),
            "proposal": "Generated proposal would go here"
        }

        # Update session with proposal metadata
        proposal_history = getattr(session, "suggested_topics", [])
        proposal_history.append({"type": "proposal", "requirements": requirements})
        manager.update_session(session_id, {"suggested_topics": proposal_history})

        # Return response
        return JSONResponse({
            "session_id": session_id,
            "proposal": proposal,
            "proposal_history": proposal_history
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "Proposal generation failed", "details": str(e)})
