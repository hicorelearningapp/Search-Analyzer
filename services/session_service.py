from typing import Dict, Any, Optional
from datetime import datetime
from app_state import AppState
import re

class SessionService:

    def __init__(self, app_state: Optional[AppState] = None):
        self.app_state = app_state or AppState()

    def create_session(self, intent: str, user_id: str = "default") -> Dict[str, Any]:
        session_id = f"{user_id}_{int(datetime.now().timestamp())}"
        self.app_state.sessions[session_id] = {
            "intent": intent,
            "created_at": datetime.now().isoformat(),
            "selected_papers": [],
            "suggested_topics": [],
            "metadata": {}
        }
        return {"session_id": session_id, "message": "Session created"}

    def get_session(self,session_id: str) -> Optional[Dict[str, Any]]:
        return self.app_state.sessions.get(session_id)

    def update_session(self,session_id: str,updates: Dict[str, Any]) -> bool:

        if session_id not in self.app_state.sessions:
            return False
            
        self.app_state.sessions[session_id].update(updates)
        return True

    def delete_session(self,session_id: str) -> bool:
        if session_id in self.app_state.sessions:
            del self.app_state.sessions[session_id]
            return True
        return False

session_service = SessionService()