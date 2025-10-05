# api/methodology_routes.py
from fastapi import APIRouter, Form, HTTPException, Request
from services.methodology_service import MethodologyService
from app_state import SessionStateManager  # Session manager for per-user tracking
from typing import Optional

router = APIRouter()
manager = SessionStateManager.get_instance()


@router.post("/methodology_search")
async def methodology_search(request: Request, paper_indices: str = Form(...)):
    """
    Extract methodology sections from the specified papers.
    Tracks session per user via X-Session-ID header.

    Args:
        paper_indices: Comma-separated string of paper indices (e.g., "0,1,2")
    """
    try:
        session_id = request.headers.get("X-Session-ID")
        if not session_id:
            session_id = manager.create_session()
        session = manager.get_or_create_session(session_id)

        indices = [int(x.strip()) for x in paper_indices.split(",") if x.strip().isdigit()]
        if not indices:
            raise HTTPException(status_code=400, detail="No valid paper indices provided")

        service = MethodologyService()
        result = await service.extract_methodology_snippets(indices=indices)

        # Update session activity
        session.last_activity = manager.timestamp()
        session.methodology_search = {
            "paper_indices": indices,
            "result_count": len(result)
        }
        manager.update_session(session_id, session)

        return {"session_id": session_id, "methodology_result": result}

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting methodology: {str(e)}")


@router.post("/compare_methodologies")
async def compare_methodologies(request: Request, paper_indices: str = Form("")):
    """
    Compare methodologies across multiple papers.
    Tracks session per user via X-Session-ID header.

    Args:
        paper_indices: Optional comma-separated string of paper indices (e.g., "0,1,2")
                      If not provided, will use all available papers
    """
    try:
        session_id = request.headers.get("X-Session-ID")
        if not session_id:
            session_id = manager.create_session()
        session = manager.get_or_create_session(session_id)

        indices = None
        if paper_indices:
            indices = [int(x.strip()) for x in paper_indices.split(",") if x.strip().isdigit()]
            if len(indices) < 2:
                raise ValueError("At least 2 papers are required for comparison")

        service = MethodologyService()
        result = await service.compare_methodologies(paper_indices=indices)

        # Update session activity
        session.last_activity = manager.timestamp()
        session.methodology_comparison = {
            "paper_indices": indices,
            "comparison_result": result
        }
        manager.update_session(session_id, session)

        return {"session_id": session_id, "comparison_result": result}

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing methodologies: {str(e)}")
