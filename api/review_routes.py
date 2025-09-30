# api/review_routes.py
from fastapi import APIRouter, Form, Depends, HTTPException, Header
from app_state import AppStateManager
from services.review_service import ReviewService
from typing import List

router = APIRouter()

def get_app_state():
    return AppStateManager()

@router.post("/review_paper")
async def review_paper(subtopics: str = Form(""), selected_indices: str = Form(""),session_id: str = Header(..., alias="X-Session-Id"),app_state: AppStateManager = Depends(get_app_state)):

    try:
        user_state = app_state.get_user_state(session_id)   

        if not user_state.search_results:
            raise HTTPException(status_code=400, detail="No search results found")
        subs = [s.strip() for s in subtopics.split(",") if s.strip()] or ["Background", "Methods", "Results"]
        try:
            idxs = [int(x.strip()) for x in selected_indices.split(",") if x.strip().isdigit()]
        except ValueError:
            raise HTTPException(status_code=400,detail="Invalid indices provided")

        selected_papers = [
            paper for i, paper in enumerate(user_state.search_results)
            if i in idxs
        ]

        if not selected_papers:
            raise HTTPException(status_code=400,detail="No valid papers selected")

        review = await ReviewService(app_state=app_state).scaffold_review(selected_papers, subs, session_id=session_id)
        user_state.synthesis_storage["latest_review"] = review
        
        return review

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))