# services/suggestion_service.py
from typing import List, Dict, Optional
import re
from datetime import datetime
from app_state import AppStateManager

class SuggestionService:    
    def __init__(self, app_state: Optional[AppStateManager] = None):
        """Initialize with optional session service injection."""
        self.app_state = app_state or AppStateManager()

    def generate_topic_suggestions(self, keywords: str, limit: int = 6, session_id: Optional[str] = None) -> Dict[str, any]:
        if not session_id:
            session = self.app_state.create_session("topic_suggestion")
            session_id = session["session_id"]
        
        session_data = self.app_state.get_session(session_id) or {}
        words = [w.strip() for w in re.split(r'[,\n;]+', keywords) if w.strip()]
        
        # Topic generation templates
        base_templates = [
            "{kw}: a systematic review of techniques and gaps",
            "Novel approaches to {kw} in {kw2}",
            "Comparative study of algorithms for {kw}",
            "Application of {kw} to healthcare / industry",
            "Benchmarking {kw} datasets and metrics",
        ]
        
        # Generate candidate suggestions
        candidates = []
        for i, w in enumerate(words):
            for t in base_templates:
                kw2 = words[(i+1) % len(words)] if len(words) > 1 else "related domains"
                candidates.append(t.format(kw=w, kw2=kw2))
                if len(candidates) >= limit:
                    break
        
        # Update session with new data
        session_data.update({
            "last_activity": datetime.now().isoformat(),
            "suggested_topics": candidates[:limit],
            "keywords": words
        })
        self.app_state.update_session(session_id, session_data)
        
        return {
            "session_id": session_id,
            "suggested_topics": candidates[:limit]
        }

# Singleton instance for easy import
suggestion_service = SuggestionService()