# api/visualization_routes.py
from fastapi import APIRouter, Form, HTTPException, Header, Depends
from fastapi.responses import HTMLResponse, Response
from typing import List, Optional
from services.visualization_service import VisualizationService
from app_state import AppStateManager

router = APIRouter()

def get_app_state():
    return AppStateManager()

@router.post("/visualize_map")
async def visualize_map(paper_indices: str = Form(""),session_id: str = Header(..., alias="X-Session-Id"),app_state: AppStateManager = Depends(get_app_state)):
    try:
        indices = []
        if paper_indices:
            indices = [int(x.strip()) for x in paper_indices.split(",") if x.strip().isdigit()]
        
        service = VisualizationService(app_state=app_state)
        result = await service.create_visual_map(paper_indices=indices,session_id=session_id)
        
        return HTMLResponse(content=result["html_content"])
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error generating visualization: {str(e)}")

@router.post("/generate_flowchart")
async def generate_flowchart(methods_text: str = Form(...),format: str = Form("png"),session_id: str = Header(..., alias="X-Session-Id"),app_state: AppStateManager = Depends(get_app_state)):
    try:
        service = VisualizationService(app_state=app_state)
        result = await service.generate_methodology_flowchart(methods_text=methods_text,session_id=session_id,format=format)
        
        return Response(content=result["image_data"],media_type=f"image/{format}")
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error generating flowchart: {str(e)}")

@router.get("/visualization/{session_id}")
async def get_visualization(session_id: str,app_state: AppStateManager = Depends(get_app_state)):
    try:
        session_data = app_state.get_user_state(session_id)
        
        if "latest_visualization" not in session_data.synthesis_storage:
            raise HTTPException(status_code=404,detail="No visualization found for this session")
            
        return session_data.synthesis_storage["latest_visualization"]
        
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error retrieving visualization: {str(e)}")