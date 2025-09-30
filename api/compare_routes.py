# api/compare_routes.py
from fastapi import APIRouter, Request, HTTPException, Depends, Header
from typing import List, Dict, Any
from services.researcher_service import ResearcherService
from app_state import AppStateManager

router = APIRouter(prefix="/compare", tags=["Comparison"])

def get_app_state():
    return AppStateManager()

@router.get("/papers")
async def compare_papers(
    session_id: str = Header(..., alias="X-Session-Id"),
    app_state: AppStateManager = Depends(get_app_state)
) -> Dict[str, Any]:
    try:
        # Get the session data
        session_data = app_state.get_user_state(session_id)
        
        if not session_data.selected_indices:
            raise HTTPException(status_code=400,detail="No papers selected for comparison")
            
        # Get the researcher service and compare papers
        service = ResearcherService(app_state)
        comparison_result = await service.compare_selected_papers(session_data)
        
        # Update session with comparison results
        if "comparisons" not in session_data.synthesis_storage:
            session_data.synthesis_storage["comparisons"] = []
        
        comparison_data = {"timestamp": session_data.last_activity,"paper_count": len(session_data.selected_indices),"result": comparison_result}
        session_data.synthesis_storage["comparisons"].append(comparison_data)
        session_data.last_activity = datetime.now().isoformat()
        
        return {"session_id": session_id,"comparison": comparison_result,"timestamp": session_data.last_activity}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error comparing papers: {str(e)}")

@router.get("/methodologies")
async def compare_methodologies(session_id: str = Header(..., alias="X-Session-Id"),app_state: AppStateManager = Depends(get_app_state)) -> Dict[str, Any]:
    try:
        session_data = app_state.get_user_state(session_id)
        
        if not session_data.selected_indices:
            raise HTTPException(
                status_code=400,
                detail="No papers selected for methodology comparison"
            )
            
        service = ResearcherService(app_state)
        comparison_result = await service.compare_methodologies(session_data)
        
        # Update session with methodology comparison
        if "methodology_comparisons" not in session_data.synthesis_storage:
            session_data.synthesis_storage["methodology_comparisons"] = []
            
        comparison_data = {
            "timestamp": session_data.last_activity,
            "paper_count": len(session_data.selected_indices),
            "result": comparison_result
        }
        session_data.synthesis_storage["methodology_comparisons"].append(comparison_data)
        session_data.last_activity = datetime.now().isoformat()
        
        return {
            "session_id": session_id,
            "methodology_comparison": comparison_result,
            "timestamp": session_data.last_activity
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error comparing methodologies: {str(e)}"
        )