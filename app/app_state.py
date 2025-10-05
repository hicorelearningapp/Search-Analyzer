# app_state.py
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime
import uuid
import threading


class SessionState(BaseModel):
    """Represents per-user session data."""
    keywords: List[str] = []
    suggested_topics: List[str] = []
    created_at: str = datetime.now().isoformat()
    last_activity: str = datetime.now().isoformat()


class SessionStateManager:
    """Thread-safe singleton that manages all user sessions."""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionStateManager, cls).__new__(cls)
            cls._instance.sessions: Dict[str, SessionState] = {}
        return cls._instance

    @classmethod
    def get_instance(cls) -> "SessionStateManager":
        """Get the global singleton instance."""
        return cls()

    def create_session(self) -> str:
        """Create a new user session and return its ID."""
        with self._lock:
            session_id = str(uuid.uuid4())
            self.sessions[session_id] = SessionState()
            return session_id

    def get_or_create_session(self, session_id: Optional[str]) -> str:
        """Return existing session ID or create a new one if missing."""
        if not session_id or session_id not in self.sessions:
            return self.create_session()
        return session_id

    def get_session(self, session_id: str) -> SessionState:
        """Retrieve the SessionState for the given ID."""
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionState()
        session = self.sessions[session_id]
        session.last_activity = datetime.now().isoformat()
        return session

    def update_session(self, session_id: str, updates: Dict[str, Any]) -> None:
        """Merge updates into an existing session safely."""
        with self._lock:
            session = self.get_session(session_id)
            for key, value in updates.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            session.last_activity = datetime.now().isoformat()

    def clear_all(self):
        """Reset all state."""
        with self._lock:
            self.sessions = {}
