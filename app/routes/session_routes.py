from fastapi import FastAPI, Form, Request, HTTPException
from typing import Optional
from services.suggestion_service import suggestion_service
from app_state import SessionStateManager  # Your session manager

app = FastAPI(title="Topic Suggestion API with Session Handling")

@app.post("/suggest_topics")
async def suggest_topics(
    request: Request,
    keywords: str = Form(..., description="Comma-separated list of keywords"),
    limit: int = Form(5, ge=1, le=20, description="Maximum number of suggestions")
):
    """
    Generate topic suggestions and track them per session.
    The session ID is extracted from the request JSON input.
    """
    try:
        body = await request.form()
        session_id: Optional[str] = body.get("session_id")

        manager = SessionStateManager.get_instance()

        # Get or create session
        session_id = manager.get_or_create_session(session_id)
        session = manager.get_session(session_id)

        # Generate suggestions
        suggestions = await suggestion_service.generate_topic_suggestions(keywords, limit)

        # Update session data
        if not hasattr(session, "keywords"):
            session.keywords = []
        if not hasattr(session, "suggested_topics"):
            session.suggested_topics = []

        session.keywords.extend([k.strip() for k in keywords.split(",") if k.strip()])
        session.suggested_topics.extend(suggestions)
        session.last_activity = manager.timestamp()
        manager.update_session(session_id, session)

        return {
            "session_id": session_id,
            "keywords": session.keywords,
            "suggested_topics": session.suggested_topics,
            "new_suggestions": suggestions,
            "last_activity": session.last_activity
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to generate topic suggestions", "details": str(e)}
        )


@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """
    Retrieve the complete session data for a user.
    Useful for debugging or client-side resumption.
    """
    manager = SessionStateManager.get_instance()
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


@app.post("/clear_sessions")
async def clear_sessions():
    """Reset all session data (for testing)."""
    SessionStateManager.get_instance().clear_all()
    return {"message": "All sessions cleared."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
