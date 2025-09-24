from fastapi import APIRouter, Form, HTTPException, Request
from typing import List
from ..services.methodology_service import MethodologyService
from ..app_state import AppState

router = APIRouter()

@router.post("/methodology_search")
async def methodology_search(request: Request,paper_indices: str = Form(...)):
    try:
        app_state: AppState = request.app.state.app_state
        idxs = [int(x.strip()) for x in paper_indices.split(",") if x.strip().isdigit()]
        if not idxs:
            raise HTTPException(status_code=400,detail="No valid paper indices provided")
        return await MethodologyService.extract_methodology_snippets(app_state=app_state,indices=idxs)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error extracting methodology: {str(e)}")

@router.post("/compare_methodologies")
async def compare_methodologies_endpoint(request: Request):
    try:
        app_state: AppState = request.app.state.app_state
        if len(app_state.selected_indices) < 2:
            raise HTTPException(status_code=400,detail="Need at least 2 papers selected to compare methodologies.")
        comparison = await MethodologyService.compare_selected_methodologies(app_state=app_state,selected_indices=app_state.selected_indices)
        return {"methodology_comparison": comparison}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error comparing methodologies: {str(e)}")