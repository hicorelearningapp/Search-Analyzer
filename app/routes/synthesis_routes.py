# api/synthesis_routes.py
from fastapi import APIRouter, HTTPException, Form, Request
from fastapi.responses import StreamingResponse, JSONResponse
from typing import List, Dict, Any
import io
from services.summary_service import SummaryService
from app_state import SessionStateManager

router = APIRouter(prefix="/synthesis", tags=["Synthesis"])


@router.post("/generate_structured_summaries")
async def generate_structured_summaries_endpoint(
    request: Request,
    selected_indices: str = Form(""),
    papers: List[Dict[str, Any]] = Form(...)
):
    """
    Generate structured summaries for selected papers.
    Includes per-user session handling.
    """
    try:
        # Get or create session
        manager = SessionStateManager.get_instance()
        session_id = request.headers.get("X-Session-ID")
        session_id = manager.get_or_create_session(session_id)
        session = manager.get_session(session_id)

        # Process paper selection
        indices = []
        if selected_indices:
            indices = [int(x.strip()) for x in selected_indices.split(",") if x.strip().isdigit()]
        selected_papers = [papers[i] for i in indices] if indices else papers

        if not selected_papers:
            raise ValueError("No valid papers selected")

        # Generate summaries using the service
        service = SummaryService()
        result = await service.generate_structured_summaries(papers=selected_papers)

        # Update session
        history = getattr(session, "keywords", [])
        history.append({
            "action": "generate_structured_summaries",
            "paper_count": len(selected_papers)
        })
        manager.update_session(session_id, {"keywords": history})

        # Return structured summaries + session info
        return JSONResponse({
            "session_id": session_id,
            "structured_summaries": result,
            "session_history": history
        })

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating structured summaries: {str(e)}"
        )


@router.post("/generate_overall_synthesis")
async def generate_overall_synthesis(
    request: Request,
    selected_indices: str = Form(""),
    papers: List[Dict[str, Any]] = Form(...)
):
    """
    Generate an overall synthesis from selected papers.
    Includes per-user session handling.
    """
    try:
        # Get or create session
        manager = SessionStateManager.get_instance()
        session_id = request.headers.get("X-Session-ID")
        session_id = manager.get_or_create_session(session_id)
        session = manager.get_session(session_id)

        # Parse selected papers
        indices = []
        if selected_indices:
            indices = [int(x.strip()) for x in selected_indices.split(",") if x.strip().isdigit()]
        selected_papers = [papers[i] for i in indices] if indices else papers

        if not selected_papers:
            raise ValueError("No valid papers selected")

        # Generate synthesis
        service = SummaryService()
        result = await service.generate_overall_synthesis(papers=selected_papers)

        # Update session
        history = getattr(session, "suggested_topics", [])
        history.append({
            "action": "generate_overall_synthesis",
            "paper_count": len(selected_papers)
        })
        manager.update_session(session_id, {"suggested_topics": history})

        # Return synthesis + session info
        return JSONResponse({
            "session_id": session_id,
            "synthesis": result,
            "session_history": history
        })

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating synthesis: {str(e)}"
        )


@router.post("/download_synthesis")
async def download_synthesis(request: Request, synthesis_data: Dict[str, Any]):
    """
    Download the synthesis as a text file.
    Includes per-user session tracking.
    """
    try:
        # Get session info
        manager = SessionStateManager.get_instance()
        session_id = request.headers.get("X-Session-ID")
        session_id = manager.get_or_create_session(session_id)

        if not synthesis_data or "synthesis" not in synthesis_data:
            raise HTTPException(status_code=400, detail="No synthesis data provided")

        # Prepare content
        content = synthesis_data.get("synthesis", "")
        file_like = io.StringIO()
        file_like.write(content)
        file_like.seek(0)

        # Update session (log download)
        session = manager.get_session(session_id)
        downloads = getattr(session, "downloads", [])
        downloads.append({"action": "download_synthesis"})
        manager.update_session(session_id, {"downloads": downloads})

        # Return file stream
        response = StreamingResponse(
            iter([file_like.getvalue()]),
            media_type="text/plain",
            headers={"Content-Disposition": "attachment; filename=synthesis.txt"}
        )
        response.headers["X-Session-ID"] = session_id
        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error downloading synthesis: {str(e)}"
        )
