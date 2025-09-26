from fastapi import APIRouter, Form
from services.suggestion_service import suggestion_service

router = APIRouter()

@router.post("/suggest_topics")
async def suggest_topics(keywords: str = Form(...), limit: int = Form(6), session_id: str = Form(None)):
    return suggestion_service.generate_topic_suggestions(keywords, limit, session_id)
