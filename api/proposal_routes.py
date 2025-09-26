# api/proposal_routes.py
from fastapi import APIRouter, Form, HTTPException, Header, Depends
from typing import List, Optional
from services.proposal_service import ProposalService
from app_state import AppState

router = APIRouter()

def get_app_state():
    return AppState()

@router.post("/proposal_writer")
async def proposal_writer(
    title: str = Form(..., description="Title of the research proposal"),
    chosen_subtopics: str = Form("", description="Comma-separated list of subtopics"),
    expected_methods: str = Form("", description="Comma-separated list of expected methods"),
    session_id: str = Header(..., alias="X-Session-Id"),
    app_state: AppState = Depends(get_app_state)
):
    try:
        user_state = app_state.get_user_state(session_id)
        
        subs = [s.strip() for s in chosen_subtopics.split(",") if s.strip()] if chosen_subtopics else []
        methods = [m.strip() for m in expected_methods.split(",") if m.strip()] if expected_methods else []
        
        proposal_service = ProposalService(app_state=app_state)
        proposal = await proposal_service.proposal_writer(
            title=title,
            chosen_subtopics=subs,
            expected_methods=methods,
            session_id=session_id
        )
        
        return {
            "session_id": session_id,
            "proposal": proposal
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating proposal: {str(e)}")

@router.get("/proposal/{session_id}")
async def get_proposal(
    session_id: str,
    app_state: AppState = Depends(get_app_state)
):
    user_state = app_state.get_user_state(session_id)
    if "latest_proposal" not in user_state.synthesis_storage:
        raise HTTPException(
            status_code=404,
            detail="No proposal found for this session"
        )
    return {
        "session_id": session_id,
        "proposal": user_state.synthesis_storage["latest_proposal"]
    }