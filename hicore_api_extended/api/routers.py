from fastapi import APIRouter, HTTPException, Form, Request
from typing import List, Dict, Any, Optional
import re
import time
from ..app_state import AppState
from ..services.search_service import search_multiple_sources, find_top_researchers, select_papers
from ..services.summary_service import generate_structured_summaries
from ..services.proposal_service import generate_proposal
from ..services.methodology_service import extract_methodology, compare_methodologies
from ..services.review_service import generate_review_draft
from ..services.visualization_service import generate_visualization
from ..services.synthesis_service import generate_synthesis

router = APIRouter()

# Session Management
@router.post("/start_session")
async def start_session(request: Request,intent: str = Form(...),user_id: str = Form("default")):
    session_id = f"{user_id}_{int(time.time())}"
    request.app.state.app_state.sessions[session_id] = {"intent": intent,"created_at": time.time(),"selected_papers": [],"suggested_topics": []}
    return {"session_id": session_id, "message": "Session started"}

# Search and Selection
@router.post("/search_papers")
async def search_papers(request: Request,topic: str = Form(...),sources: str = Form("semantic,arxiv,openalex"),limit: int = Form(6, ge=1, le=20)):
    source_list = [s.strip().lower() for s in sources.split(",") if s.strip()]
    results = await search_multiple_sources(topic, source_list, limit)
    request.app.state.app_state.search_results = results
    return {"count": len(results), "results": results}

@router.post("/select_papers")
async def select_papers(request: Request,indices: str = Form(...)):
    try:
        selected = await select_papers(indices, request.app.state.app_state.search_results,
            request.app.state.app_state.sessions.get(request.headers.get("session_id")))
        return {"selected_indices": [i for i, _ in selected]}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Summaries and Analysis
@router.post("/generate_summaries")
async def generate_summaries(request: Request):
    session = request.app.state.app_state.sessions.get(request.headers.get("session_id"))
    if not session or not session.get("selected_papers"):
        raise HTTPException(status_code=400, detail="No papers selected")
    
    summaries = await generate_structured_summaries(session["selected_papers"],request.app.state.azure_client)
    return {"summaries": summaries}

# Proposal and Review Generation
@router.post("/generate_proposal")
async def generate_proposal_endpoint(request: Request,title: str = Form(...),subtopics: str = Form(""),methods: str = Form("")):
    session = request.app.state.app_state.sessions.get(request.headers.get("session_id"))
    if not session or not session.get("selected_papers"):
        raise HTTPException(status_code=400, detail="No papers selected")
    
    proposal = await generate_proposal(title=title,subtopics=subtopics,methods=methods,papers=session["selected_papers"],azure_client=request.app.state.azure_client)
    return {"proposal": proposal}

# Methodology Analysis
@router.post("/analyze_methodology")
async def analyze_methodology(request: Request,paper_indices: str = Form("")):
    session = request.app.state.app_state.sessions.get(request.headers.get("session_id"))
    if not session or not session.get("selected_papers"):
        raise HTTPException(status_code=400, detail="No papers selected")
    
    idxs = [int(x.strip())-1 for x in paper_indices.split(",") if x.strip().isdigit()]
    selected = [session["selected_papers"][i] for i in idxs if 0 <= i < len(session["selected_papers"])]
    
    analysis = await extract_methodology(papers=selected,azure_client=request.app.state.azure_client)
    return {"analysis": analysis}

# Visualization
@router.post("/visualize_papers")
async def visualize_papers(request: Request,seed_indices: str = Form("")):
    session = request.app.state.app_state.sessions.get(request.headers.get("session_id"))
    if not session or not session.get("selected_papers"):
        raise HTTPException(status_code=400, detail="No papers selected")
    
    idxs = [int(x.strip())-1 for x in seed_indices.split(",") if x.strip().isdigit()]
    selected = [session["selected_papers"][i] for i in idxs if 0 <= i < len(session["selected_papers"])]
    
    visualization = await generate_visualization(papers=selected,azure_client=request.app.state.azure_client)
    return {"visualization": visualization}

# State Management
@router.post("/clear_state")
async def clear_state(request: Request):
    request.app.state.app_state.clear()
    return {"status": "success", "message": "Application state has been reset"}
