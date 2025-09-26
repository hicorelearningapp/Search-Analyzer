# In compare_routes.py
from fastapi import APIRouter, HTTPException, Request
from services.researcher_service import ResearcherService
from app_state import AppState

router = APIRouter()

@router.get("/compare_papers")
async def compare_selected_papers_endpoint(request: Request):
    app_state: AppState = request.app.state.app_state
    if not app_state.selected_indices:
        raise HTTPException(status_code=400, detail="No papers selected")
    try:
        return await ResearcherService.compare_papers(app_state)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Failed to compare papers: {str(e)}")
