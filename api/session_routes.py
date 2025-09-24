from fastapi import APIRouter, Form
from services.session_service import SessionService

router = APIRouter()

@router.post("/suggest_topics")
async def suggest_topics(keywords: str = Form(...), limit: int = Form(6), session_id: str = Form(None)):
    return SessionService.suggest_topics(keywords, limit, session_id)
