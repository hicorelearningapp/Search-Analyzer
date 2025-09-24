# app/api/search_routes.py
from fastapi import APIRouter, Form, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel, Field
from services.search_service import SearchService

router = APIRouter()

# Import Request/Response Models
from .search_service import SearchRequest, PaperResponse, SearchResponse, SelectPapersRequest

# Endpoints
@router.post("/project_start", response_model=SearchResponse)
async def project_start(topic: str = Form(...),limit: int = Form(5, ge=1, le=10)):
    results = []
    results.extend(semantic_scholar_search(topic, limit))
    results.extend(arxiv_search(topic, limit))
    results.extend(openalex_search(topic, limit))
    return {"topic": topic, "papers": results[:limit]}

@router.post("/search_papers", response_model=SearchResponse)
async def search_papers(topic: str = Form(...),sources: str = Form("semantic,arxiv,openalex"),limit: int = Form(6, ge=1, le=20)):
    try:
        source_list = [s.strip().lower() for s in sources.split(",") if s.strip()]
        results = await SearchService.search_multiple_sources(topic=topic,sources=source_list,limit=limit)
        return {"count": len(results), "results": results}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to search papers")

@router.post("/select_papers")
async def select_papers(request: SelectPapersRequest):
    try:
        selected = await SearchService.select_papers(request.indices)
        return {"selected_indices": selected}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to select papers")

@router.post("/top_researchers")
async def top_researchers(topic: str = Form(...),limit: int = Form(5, ge=1, le=20)):
    try:
        researchers = await SearchService.find_top_researchers(topic, limit)
        return {"topic": topic, "researchers": researchers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))