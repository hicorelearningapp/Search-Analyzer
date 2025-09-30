"""
Miscellaneous routes
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Dict, Any
from app_state import AppStateManager
from datetime import datetime

router = APIRouter(prefix="/misc", tags=["Miscellaneous"])

def get_app_state():
    return AppStateManager()

@router.post("/clear_state")
async def clear_state(session_id: str = Header(..., alias="X-Session-Id"),app_state: AppStateManager = Depends(get_app_state)) -> Dict[str, str]:

    try:
        if session_id in app_state.sessions:
            session_data = app_state.get_user_state(session_id)
            session_data.search_results = []
            session_data.selected_indices = []
            session_data.synthesis_storage = {}
            session_data.last_activity = datetime.now().isoformat()
            
            return {"message": f"State cleared for session {session_id}", "status": "success"}
        else:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing state: {str(e)}")

@router.post("/clear_all_sessions")
async def clear_all_sessions(app_state: AppStateManager = Depends(get_app_state)) -> Dict[str, str]:
    try:
        app_state.sessions.clear()
        return {"message": "All sessions cleared", "status": "success"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing all sessions: {str(e)}")

@router.get("/session_info/{session_id}")
async def get_session_info(session_id: str,app_state: AppStateManager = Depends(get_app_state)) -> Dict[str, Any]:
    try:
        if session_id not in app_state.sessions:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
            
        session_data = app_state.get_user_state(session_id)
        
        return {
            "session_id": session_id,
            "created_at": session_data.created_at,
            "last_activity": session_data.last_activity,
            "search_results_count": len(session_data.search_results),
            "selected_indices_count": len(session_data.selected_indices),
            "synthesis_keys": list(session_data.synthesis_storage.keys())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session info: {str(e)}")
