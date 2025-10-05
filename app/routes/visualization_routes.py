# api/visualization_routes.py
from fastapi import APIRouter, Form, HTTPException,Request
from fastapi.responses import HTMLResponse, Response
from typing import List, Optional
from services.visualization_service import VisualizationService
from app_state import SessionStateManager

router = APIRouter(prefix='/visualization',tags=['Visualization'])

@router.post("/visualize_map")
async def visualize_map(request:Request,paper_indices: str = Form(""),papers: List[dict] = Form(...)):
    try:

        manager = SessionStateManager.get_instance()
        session_id = request.headers.get('X-Session-ID')
        session_id = manager.get_or_create_session(session_id)
        session = manager.get_session(session_id)

        indices = []
        if paper_indices:
            indices = [int(x.strip()) for x in paper_indices.split(",") if x.strip().isdigit()]
        
        # Filter papers based on indices if provided, otherwise use all papers
        selected_papers = [papers[i] for i in indices] if indices else papers
        
        if not selected_papers:
            raise ValueError("No valid papers selected")
            
        service = VisualizationService()
        result = service.create_visual_map(papers=selected_papers)
        
        history = getattr(session, "suggested_topics", [])
        history.append({
            "action": "visualize_map",
            "papers_count": len(selected_papers),
            "timestamp": result["timestamp"]
        })
        manager.update_session(session_id, {"suggested_topics": history})

        #Return HTML and session info
        return JSONResponse({
            "session_id": session_id,
            "visualization_type": result["visualization_type"],
            "format": result["format"],
            "timestamp": result["timestamp"],
            "html_content": result["data"],
            "session_history": history
        })

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating visualization: {str(e)}"
        )

@router.post("/generate_flowchart")
async def generate_flowchart(request: Request,methods_text: str = Form(..., description="Text describing the methodology to visualize"),format: str = Form("png", description="Output format (png, svg, etc.)")):
    """
    Generate a methodology flowchart from text.
    Includes per-user session tracking for each flowchart generation.
    """
    try:
        # Get or create session
        manager = SessionStateManager.get_instance()
        session_id = request.headers.get("X-Session-ID")
        session_id = manager.get_or_create_session(session_id)
        session = manager.get_session(session_id)

        if not methods_text.strip():
            raise ValueError("Methods text cannot be empty")

        # Run service
        service = VisualizationService()
        result = service.generate_methodology_flowchart(
            methods_text=methods_text,
            format=format.lower()
        )

        # Update session with recent flowchart record
        history = getattr(session, "keywords", [])
        history.append({
            "action": "generate_flowchart",
            "format": format,
            "timestamp": result["timestamp"]
        })
        manager.update_session(session_id, {"keywords": history})

        # Return image data and session info
        response = Response(
            content=result["image_data"],
            media_type=f"image/{format}"
        )
        response.headers["X-Session-ID"] = session_id
        return response

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating flowchart: {str(e)}"
        )
