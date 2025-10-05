# api/suggestion_routes.py
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from services.suggestion_service import suggestion_service
from app_state import SessionStateManager

router = APIRouter(prefix="/suggestion", tags=["Suggestion"])

@router.post("/suggest_topics")
async def suggest_topics(request: Request,keywords: str = Form(..., description="Comma-separated list of keywords"),limit: int = Form(6, ge=1, le=20, description="Maximum number of suggestions to return")):

    try:
        # Get or create session
        manager = SessionStateManager.get_instance()
        session_id = request.headers.get("X-Session-ID")
        session_id = manager.get_or_create_session(session_id)
        session = manager.get_session(session_id)

        # Generate topic suggestions
        suggestions = await suggestion_service.generate_topic_suggestions(keywords, limit)

        # Update session
        history = getattr(session, "suggested_topics", [])
        history.append({"action": "suggest_topics","keywords_used": [kw.strip() for kw in keywords.split(",") if kw.strip()],"suggestion_count": len(suggestions)})
        manager.update_session(session_id, {"suggested_topics": history})

        # Return suggestions + session metadata
        return JSONResponse({"session_id": session_id,"suggested_topics": suggestions,"session_history": history})

    except Exception as e:
        raise HTTPException(status_code=500,detail={"error": "Failed to generate topic suggestions","details": str(e)})
