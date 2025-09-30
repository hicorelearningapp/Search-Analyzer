# api/routers.py
from fastapi import APIRouter, Request, Form, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from datetime import datetime
import time
from typing import List, Dict, Any, Optional

from app_state import AppState, SessionState

router = APIRouter()

def get_app_state():
    return AppState()

# Session Management
@router.post("/start_session")
async def start_session(request: Request,intent: str = Form(...),user_id: str = Form("default"),app_state: AppState = Depends(get_app_state)):

    try:
        session_id = f"{user_id}_{int(time.time())}"
        session_data = SessionState(synthesis_storage={"intent": intent,"created_at": datetime.now().isoformat(),"selected_papers": [],"suggested_topics": []})
        app_state.sessions[session_id] = session_data
        return {"session_id": session_id,"message": "Session started","created_at": session_data.synthesis_storage["created_at"],"intent": intent}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")

@router.get("/session/{session_id}")
async def get_session(session_id: str,app_state: AppState = Depends(get_app_state)):
    
    try:
        if session_id not in app_state.sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        session_data = app_state.sessions[session_id]
        return {"session_id": session_id,"created_at": session_data.synthesis_storage.get("created_at"),"last_activity": session_data.last_activity,"intent": session_data.synthesis_storage.get("intent"),"selected_papers_count": len(session_data.selected_indices),"search_results_count": len(session_data.search_results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session: {str(e)}")

@router.post("/end_session/{session_id}")
async def end_session(session_id: str,app_state: AppState = Depends(get_app_state)):
    try:
        if session_id in app_state.sessions:
            del app_state.sessions[session_id]
            return {"message": f"Session {session_id} ended successfully"}
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end session: {str(e)}")

# Search and Selection
@router.post("/search_papers")
async def search_papers(query: str = Form(...),source: str = Form("all"),session_id: str = Header(..., alias="X-Session-Id"),app_state: AppState = Depends(get_app_state)):
    try:
        session_data = app_state.get_user_state(session_id)
        return {"session_id": session_id,"query": query,"source": source,"result_count": len(session_data.search_results),"timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/select_papers")
async def select_papers(paper_indices: str = Form(...),session_id: str = Header(..., alias="X-Session-Id"),app_state: AppState = Depends(get_app_state)):
    try:
        session_data = app_state.get_user_state(session_id)
        indices = [int(idx.strip()) for idx in paper_indices.split(",") if idx.strip().isdigit()]
        
        valid_indices = [i for i in indices if 0 <= i < len(session_data.search_results)]
        session_data.selected_indices = valid_indices
        
        session_data.last_activity = datetime.now().isoformat()
        
        return {"session_id": session_id,"selected_count": len(valid_indices),"selected_indices": valid_indices,"timestamp": session_data.last_activity}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid paper indices: {str(e)}")

# Analysis Endpoints
@router.post("/analyze_methodology")
async def analyze_methodology(session_id: str = Header(..., alias="X-Session-Id"),app_state: AppState = Depends(get_app_state)):
    try:
        session_data = app_state.get_user_state(session_id)
        if not session_data.selected_indices:
            raise HTTPException(status_code=400, detail="No papers selected")
        return {"session_id": session_id,"paper_count": len(session_data.selected_indices),"timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/generate_proposal")
async def create_proposal(requirements: str = Form(...),session_id: str = Header(..., alias="X-Session-Id"),app_state: AppState = Depends(get_app_state)):
    try:
        session_data = app_state.get_user_state(session_id)
        if not session_data.selected_indices:
            raise HTTPException(status_code=400, detail="No papers selected")
            
        return {"session_id": session_id,"requirements": requirements,"timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proposal generation failed: {str(e)}")