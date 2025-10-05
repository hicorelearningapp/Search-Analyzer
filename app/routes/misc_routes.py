"""
Miscellaneous routes with session-aware example
"""

from fastapi import APIRouter, HTTPException, Header, Request
from typing import Dict, Any, Optional
from datetime import datetime
from app_state import SessionStateManager  # Session manager for per-user state

router = APIRouter(prefix="/misc", tags=["Miscellaneous"])
manager = SessionStateManager.get_instance()


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Basic health check endpoint
    """
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@router.get("/session")
async def get_session(session_id: Optional[str] = Header(None, alias="X-Session-ID")) -> Dict[str, Any]:
    """
    Retrieve current session data for debugging or client resumption.
    Session ID is passed via `X-Session-ID` header.
    """
    if not session_id:
        raise HTTPException(status_code=400, detail="X-Session-ID header missing")

    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "keywords": getattr(session, "keywords", []),
        "suggested_topics": getattr(session, "suggested_topics", []),
        "created_at": session.created_at,
        "last_activity": session.last_activity
    }


@router.post("/clear_sessions")
async def clear_sessions() -> Dict[str, str]:
    """
    Reset all session data (for testing or maintenance purposes)
    """
    manager.clear_all()
    return {"message": "All sessions cleared."}
