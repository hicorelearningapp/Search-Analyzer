# api/review_routes.py
from fastapi import APIRouter, Form, HTTPException, Request
from typing import List
from services.review_service import ReviewService
from app_state import SessionStateManager   # Session manager for per-user session tracking

router = APIRouter()

@router.post("/review_paper")
async def review_paper(
    request: Request,
    subtopics: str = Form(""),
    selected_indices: str = Form(""),
    papers: List[dict] = Form(...)
):
    """
    Generate a review of selected papers, tracked per user session.
    
    Args:
        subtopics: Comma-separated list of subtopics to include in the review.
        selected_indices: Comma-separated list of indices of papers to review.
        papers: List of paper objects to review.
    
    Returns:
        The generated review and session details.
    """
    try:
        # ✅ Identify or create session
        session_id = request.headers.get("X-Session-ID")
        if not session_id:
            session_id = SessionStateManager.get_instance().create_session()
        
        session_state = SessionStateManager.get_instance().get_session(session_id)

        # ✅ Parse subtopics or use default ones
        subs = [s.strip() for s in subtopics.split(",") if s.strip()] or ["Background", "Methods", "Results"]

        # ✅ Parse and validate selected indices
        try:
            idxs = [int(x.strip()) for x in selected_indices.split(",") if x.strip().isdigit()]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid indices provided")

        # ✅ Select papers based on indices
        selected_papers = [papers[i] for i in idxs if 0 <= i < len(papers)]
        if not selected_papers:
            raise HTTPException(status_code=400, detail="No valid papers selected")

        # ✅ Generate review
        review = await ReviewService().scaffold_review(selected_papers, subs)

        # ✅ Update session data
        session_state.last_activity = SessionStateManager.get_instance().timestamp()
        session_state.review = {
            "subtopics": subs,
            "selected_indices": idxs,
            "review_text": review
        }
        SessionStateManager.get_instance().update_session(session_id, session_state)

        # ✅ Return review with session tracking info
        return {
            "session_id": session_id,
            "subtopics": subs,
            "selected_indices": idxs,
            "review": review,
            "session_timestamp": session_state.last_activity
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to generate review", "details": str(e)}
        )
