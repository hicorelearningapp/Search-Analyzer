from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid


class SessionState(BaseModel):
    search_results: List[Dict[str, Any]] = []
    selected_indices: List[int] = []
    synthesis_storage: Dict[str, str] = {}
    created_at: str = datetime.now().isoformat()
    last_activity: str = datetime.now().isoformat()


class AppState:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppState, cls).__new__(cls)
            cls._instance.sessions: Dict[str, SessionState] = {}
        return cls._instance

    @classmethod
    def get_app_state(cls) -> 'AppState':
        return cls()

    # Create a new session
    def create_session(self, purpose: str = "generic") -> Dict[str, Any]:
        session_id = str(uuid.uuid4())
        session = SessionState()
        self.sessions[session_id] = session
        return {
            "session_id": session_id,
            "purpose": purpose,
            "created_at": session.created_at
        }

    # Get an existing session safely
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        session = self.sessions.get(session_id)
        return session.dict() if session else None

    # Update session data (merges into existing SessionState)
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> None:
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionState()
        session = self.sessions[session_id]
        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)
        session.last_activity = datetime.now().isoformat()
        self.sessions[session_id] = session

    # Helper: get SessionState object (not just dict)
    def get_user_state(self, session_id: str) -> SessionState:
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionState()
        # Update last_activity whenever session is accessed
        self.sessions[session_id].last_activity = datetime.now().isoformat()
        return self.sessions[session_id]

    # Reset all sessions
    def clear(self):
        """Reset all state to initial values"""
        self.sessions = {}

    # Optional helpers for individual session fields
    def get_search_results(self, session_id: str) -> List[Dict[str, Any]]:
        return self.get_user_state(session_id).search_results

    def get_selected_indices(self, session_id: str) -> List[int]:
        return self.get_user_state(session_id).selected_indices

    def get_synthesis_storage(self, session_id: str) -> Dict[str, str]:
        return self.get_user_state(session_id).synthesis_storage
