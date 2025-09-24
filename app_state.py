from typing import Dict, List, Any, Optional
from pydantic import BaseModel

class SessionState(BaseModel):
    sessions: Dict[str, Dict[str, Any]] = {}
    search_results: List[Dict[str, Any]] = []
    selected_indices: List[int] = []
    synthesis_storage: Dict[str, str] = {}

class AppState:
    def __init__(self):
        self.state = SessionState()
    
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
