from fastapi import APIRouter
from app_state import AppState

router = APIRouter()

@router.post("/clear_state")
async def clear_state_endpoint(app_state: AppState):
    app_state.state.search_results = []
    app_state.state.selected_indices = []
    app_state.state.synthesis_storage = {}
    app_state.state.sessions = {}
    return {"message": "State cleared"}
