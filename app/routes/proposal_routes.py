# api/proposal_routes.py
from fastapi import APIRouter, Form, HTTPException, Request
from services.proposal_service import ProposalService
from app_state import SessionStateManager   # ✅ Session tracking
from typing import List

router = APIRouter()

@router.post("/proposal_writer")
async def proposal_writer(
    request: Request,
    title: str = Form(..., description="Title of the research proposal"),
    chosen_subtopics: str = Form("", description="Comma-separated list of subtopics"),
    expected_methods: str = Form("", description="Comma-separated list of expected methods"),
):
    """
    Generate a research proposal, tracked per user session.

    Args:
        title: Title of the research proposal.
        chosen_subtopics: Comma-separated list of chosen subtopics.
        expected_methods: Comma-separated list of expected methods.

    Returns:
        Generated proposal text and session tracking details.
    """
    try:
        # ✅ Identify or create session
        session_id = request.headers.get("X-Session-ID")
        if not session_id:
            session_id = SessionStateManager.get_instance().create_session()

        session_state = SessionStateManager.get_instance().get_session(session_id)

        # ✅ Parse subtopics and methods (default fallback optional)
        subs = [s.strip() for s in chosen_subtopics.split(",") if s.strip()] or ["Introduction", "Methodology", "Expected Outcomes"]
        methods = [m.strip() for m in expected_methods.split(",") if m.strip()] or ["Qualitative Analysis", "Quantitative Evaluation"]

        # ✅ Generate proposal via service
        proposal_service = ProposalService()
        proposal = await proposal_service.proposal_writer(
            title=title,
            chosen_subtopics=subs,
            expected_methods=methods,
        )

        # ✅ Update session state
        session_state.last_activity = SessionStateManager.get_instance().timestamp()
        session_state.proposal = {
            "title": title,
            "subtopics": subs,
            "methods": methods,
            "proposal_text": proposal
        }
        SessionStateManager.get_instance().update_session(session_id, session_state)

        # ✅ Return result
        return {
            "session_id": session_id,
            "title": title,
            "chosen_subtopics": subs,
            "expected_methods": methods,
            "proposal": proposal,
            "session_timestamp": session_state.last_activity
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Error generating proposal", "details": str(e)}
        )

@router.get("/proposal/session")
async def get_saved_proposal(request: Request):
    """
    Retrieve the last saved proposal for a session.
    """
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing session ID")

    session_state = SessionStateManager.get_instance().get_session(session_id)
    if not hasattr(session_state, "proposal") or not session_state.proposal:
        raise HTTPException(status_code=404, detail="No saved proposal found for this session")

    return {
        "session_id": session_id,
        "saved_proposal": session_state.proposal,
        "last_updated": session_state.last_activity
    }
