# api/methodology_routes.py
from fastapi import APIRouter, Form, HTTPException, Header, Depends
from typing import List, Optional
from services.methodology_service import MethodologyService
from app_state import AppState

router = APIRouter()

def get_app_state():
    return AppState()

@router.post("/methodology_search")
async def methodology_search(
    paper_indices: str = Form(...),
    session_id: str = Header(..., alias="X-Session-Id"),
    app_state: AppState = Depends(get_app_state)
):
    try:
        indices = [int(x.strip()) for x in paper_indices.split(",") if x.strip().isdigit()]
        if not indices:
            raise HTTPException(
                status_code=400,
                detail="No valid paper indices provided"
            )

        service = MethodologyService(app_state=app_state)
        result = await service.extract_methodology_snippets(
            indices=indices,
            session_id=session_id
        )
        
        return result
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting methodology: {str(e)}"
        )

@router.post("/compare_methodologies")
async def compare_methodologies(
    paper_indices: str = Form(""),
    session_id: str = Header(..., alias="X-Session-Id"),
    app_state: AppState = Depends(get_app_state)
):
    try:
        indices = None
        if paper_indices:
            indices = [int(x.strip()) for x in paper_indices.split(",") if x.strip().isdigit()]
            if len(indices) < 2:
                raise ValueError("At least 2 papers are required for comparison")

        service = MethodologyService(app_state=app_state)
        result = await service.compare_methodologies(
            paper_indices=indices,
            session_id=session_id
        )
        
        return result
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error comparing methodologies: {str(e)}"
        )

@router.get("/methodology/{session_id}")
async def get_methodology_analysis(
    session_id: str,
    app_state: AppState = Depends(get_app_state)
):

    session_data = app_state.get_user_state(session_id)
    if "latest_methodology" in session_data.synthesis_storage:
        return {
            "type": "methodology_analysis",
            "data": session_data.synthesis_storage["latest_methodology"]
        }
    elif "latest_comparison" in session_data.synthesis_storage:
        return {
            "type": "methodology_comparison",
            "data": session_data.synthesis_storage["latest_comparison"]
        }
    else:
        raise HTTPException(
            status_code=404,
            detail="No methodology analysis found for this session"
        )