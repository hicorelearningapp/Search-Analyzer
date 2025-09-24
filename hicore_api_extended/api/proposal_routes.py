from fastapi import APIRouter, Form
from services.proposal_service import ProposalService

router = APIRouter()

@router.post("/proposal_writer")
async def proposal_writer(title: str = Form(...), chosen_subtopics: str = Form(""), expected_methods: str = Form("")):
    subs = [s.strip() for s in chosen_subtopics.split(",") if s.strip()] if chosen_subtopics else []
    methods = [m.strip() for m in expected_methods.split(",") if m.strip()] if expected_methods else []
    return ProposalService.proposal_writer(title, subs, methods)
