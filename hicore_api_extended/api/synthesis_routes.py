from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
import io
from typing import Dict, Any
from ..services.summary_service import SummaryService
from ..app_state import AppState

router = APIRouter()

@router.post("/generate_structured_summaries")
async def generate_structured_summaries_endpoint(request: Request):
    app_state: AppState = request.app.state.app_state
    results = await SummaryService.generate_structured_summaries(app_state=app_state,selected_idx=app_state.selected_indices)
    return {"structured_summaries": results}

@router.post("/generate_overall_synthesis")
async def generate_overall_synthesis(request: Request):
    app_state: AppState = request.app.state.app_state
    overall = await SummaryService.generate_overall_synthesis(app_state=app_state,selected_idx=app_state.selected_indices)
    return {"synthesis": overall}

@router.get("/download_synthesis")
async def download_synthesis(request: Request):
    app_state: AppState = request.app.state.app_state
    session_id = request.headers.get("session_id")
    
    if not session_id or session_id not in app_state.sessions:
        raise HTTPException(status_code=400, detail="No active session found")
    
    session = app_state.sessions[session_id]
    if "latest_synthesis" not in session:
        raise HTTPException(status_code=400, detail="No synthesis available")
    
    content = session["latest_synthesis"]
    return StreamingResponse(io.BytesIO(content.encode("utf-8")),media_type="text/plain",headers={"Content-Disposition": "attachment; filename=synthesis.txt"})