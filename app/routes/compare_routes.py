# api/compare_routes.py
from fastapi import APIRouter, HTTPException, Header
from typing import Dict, Any
from services.researcher_service import ResearcherService
from app_state import SessionStateManager
from datetime import datetime

router = APIRouter(prefix="/compare", tags=["Comparison"])
manager = SessionStateManager.get_instance()


@router.get("/papers")
async def compare_papers(
    session_id: str = Header(..., alias="X-Session-ID")
) -> Dict[str, Any]:
    """
    Compare selected papers for a user session.
    
    Args:
        session_id: User session ID from header
    """
    session = manager.get_or_create_session(session_id)
    try:
        service = ResearcherService()
        comparison_result = await service.compare_selected_papers()
        
        session.last_activity = datetime.now().isoformat()
        
        return {"comparison": comparison_result, "timestamp": datetime.now().isoformat()}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing papers: {str(e)}")


@router.get("/methodologies")
async def compare_methodologies(
    session_id: str = Header(..., alias="X-Session-ID")
) -> Dict[str, Any]:
    """
    Compare methodologies across papers for a user session.
    
    Args:
        session_id: User session ID from header
    """
    session = manager.get_or_create_session(session_id)
    try:
        service = ResearcherService()
        comparison_result = await service.compare_methodologies()
        
        session.last_activity = datetime.now().isoformat()
        
        return {"comparison": comparison_result, "timestamp": datetime.now().isoformat()}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing methodologies: {str(e)}")
