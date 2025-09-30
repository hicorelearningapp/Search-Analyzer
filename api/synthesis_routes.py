# api/synthesis_routes.py
from fastapi import APIRouter, HTTPException, Header, Depends, Form
from typing import List, Optional
import io
from fastapi.responses import StreamingResponse
from services.summary_service import SummaryService
from app_state import AppStateManager

router = APIRouter()

def get_app_state():
    return AppStateManager()

@router.post("/generate_structured_summaries")
async def generate_structured_summaries_endpoint(selected_indices: str = Form(""),session_id: str = Header(..., alias="X-Session-Id"),app_state: AppStateManager = Depends(get_app_state)):
    try:
        indices = []
        if selected_indices:
            indices = [int(x.strip()) for x in selected_indices.split(",") if x.strip().isdigit()]
        service = SummaryService(app_state=app_state)
        result = await service.generate_structured_summaries(selected_indices=indices,session_id=session_id)
        return result
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error generating structured summaries: {str(e)}")

@router.post("/generate_overall_synthesis")
async def generate_overall_synthesis(selected_indices: str = Form(""),session_id: str = Header(..., alias="X-Session-Id"),app_state: AppStateManager = Depends(get_app_state)):
    try:
        indices = []
        if selected_indices:
            indices = [int(x.strip()) for x in selected_indices.split(",") if x.strip().isdigit()]
        service = SummaryService(app_state=app_state)
        result = await service.generate_overall_synthesis(selected_indices=indices,session_id=session_id)
        return result
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error generating synthesis: {str(e)}")

@router.get("/synthesis/{session_id}")
async def get_synthesis(session_id: str,app_state: AppStateManager = Depends(get_app_state)):
    try:
        session_data = app_state.get_user_state(session_id)
        
        if "latest_synthesis" in session_data.synthesis_storage:
            return {
                "type": "synthesis",
                "data": session_data.synthesis_storage["latest_synthesis"]
            }
        elif "latest_summaries" in session_data.synthesis_storage:
            return {
                "type": "summaries",
                "data": session_data.synthesis_storage["latest_summaries"]
            }
        else:
            raise HTTPException(
                status_code=404,
                detail="No synthesis or summaries found for this session"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving synthesis: {str(e)}"
        )

@router.get("/download_synthesis/{session_id}")
async def download_synthesis(session_id: str,app_state: AppStateManager = Depends(get_app_state)):
    try:
        session_data = app_state.get_user_state(session_id)
        
        if "latest_synthesis" not in session_data.synthesis_storage:
            raise HTTPException(status_code=404,detail="No synthesis available for download")
            
        synthesis = session_data.synthesis_storage["latest_synthesis"]
        content = synthesis.get("synthesis", "")
        
        file_like = io.StringIO()
        file_like.write(content)
        file_like.seek(0)
        
        return StreamingResponse(iter([file_like.getvalue()]),media_type="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename=synthesis_{session_id}.txt"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error downloading synthesis: {str(e)}")