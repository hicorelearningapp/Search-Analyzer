from fastapi import APIRouter, Form, Header, Depends
from services.suggestion_service import suggestion_service
from app_state import AppStateManager


router = APIRouter()

def get_app_state():
    return AppStateManager()

@router.post("/suggest_topics")
async def suggest_topics(keywords: str = Form(...), limit: int = Form(6), session_id: str = Header(..., alias="X-Session-Id"), app_state: AppStateManager = Depends(get_app_state)):
    return suggestion_service.generate_topic_suggestions(keywords, limit, session_id)

