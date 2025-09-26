#app_state.py
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime

class SessionState(BaseModel):
    search_results: List[Dict[str, Any]] = []
    selected_indices: List[int] = []
    synthesis_storage: Dict[str, str] = {}
    created_at: Optional[str] = None
    last_activity: str = datetime.isoformat(datetime.now())

class AppState:
    _instance = None
    sessions: Dict[str, SessionState] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppState, cls).__new__(cls)
            cls._instance.state = SessionState()
        return cls._instance
    
    @classmethod
    def get_app_state(cls) -> 'AppState':
        return cls()
    
    @property
    def sessions(self) -> Dict[str, SessionState]:
        return self.state.sessions
    
    @property
    def search_results(self) -> List[Dict[str, Any]]:
        return self.state.search_results
    
    @property
    def selected_indices(self) -> List[int]:
        return self.state.selected_indices
    
    @property
    def synthesis_storage(self) -> Dict[str, str]:
        return self.state.synthesis_storage
    
    def clear(self):
        """Reset all state to initial values"""
        self.state = SessionState()

    def get_user_state(self, session_id: str) -> SessionState:
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionState()
        return self.sessions[session_id]

