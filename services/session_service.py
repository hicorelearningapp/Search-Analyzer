from typing import Dict, Any, Optional
from datetime import datetime
from ..app_state import AppState

class SessionService:

    @staticmethod
    def create_session(
        app_state: AppState,
        intent: str,
        user_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Create a new session and add it to the app state.
        
        Args:
            app_state: The application state
            intent: User's research intent
            user_id: Optional user identifier
            
        Returns:
            Dictionary with session ID and creation status
        """
        session_id = f"{user_id}_{int(datetime.now().timestamp())}"
        app_state.sessions[session_id] = {
            "intent": intent,
            "created_at": datetime.now().isoformat(),
            "selected_papers": [],
            "suggested_topics": [],
            "metadata": {}
        }
        return {"session_id": session_id, "message": "Session created"}

    @staticmethod
    def get_session(
        app_state: AppState,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a session by ID.
        
        Args:
            app_state: The application state
            session_id: The session ID to retrieve
            
        Returns:
            The session data if found, None otherwise
        """
        return app_state.sessions.get(session_id)

    @staticmethod
    def update_session(
        app_state: AppState,
        session_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update session data.
        
        Args:
            app_state: The application state
            session_id: The session ID to update
            updates: Dictionary of fields to update
            
        Returns:
            True if update was successful, False otherwise
        """
        if session_id not in app_state.sessions:
            return False
            
        app_state.sessions[session_id].update(updates)
        return True

    @staticmethod
    def delete_session(
        app_state: AppState,
        session_id: str
    ) -> bool:
        """
        Delete a session.
        
        Args:
            app_state: The application state
            session_id: The session ID to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        if session_id in app_state.sessions:
            del app_state.sessions[session_id]
            return True
        return False

    @staticmethod
    def suggest_topics(keywords: str, limit: int = 6, session_id: str = None):
        words = [w.strip() for w in re.split(r'[,\n;]+', keywords) if w.strip()]
        base_templates = [
            "{kw}: a systematic review of techniques and gaps",
            "Novel approaches to {kw} in {kw2}",
            "Comparative study of algorithms for {kw}",
            "Application of {kw} to healthcare / industry",
            "Benchmarking {kw} datasets and metrics",
        ]
        candidates = []
        for i, w in enumerate(words):
            for t in base_templates:
                kw2 = words[(i+1) % len(words)] if len(words) > 1 else "related domains"
                candidates.append(t.format(kw=w, kw2=kw2))
                if len(candidates) >= limit:
                    break
        return {"keywords": words, "suggested_topics": candidates[:limit]}
