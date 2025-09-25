from typing import Dict, List, Any, Optional
from pydantic import BaseModel

class SessionState(BaseModel):
    sessions: Dict[str, Dict[str, Any]] = {}
    search_results: List[Dict[str, Any]] = []
    selected_indices: List[int] = []
    synthesis_storage: Dict[str, str] = {}

class AppState:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppState, cls).__new__(cls)
            cls._instance.state = SessionState()
        return cls._instance
    
    @classmethod
    def get_app_state(cls) -> 'AppState':
        return cls()
    
    @property
    def sessions(self) -> Dict[str, Dict[str, Any]]:
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
