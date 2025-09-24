from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import FileResponse
from services.visualization_service import VisualizationService

router = APIRouter()

@router.post("/visualize_map")
async def visualize_map(seed_indices: str = Form(...)):
    idxs = [int(x.strip())-1 for x in seed_indices.split(",") if x.strip().isdigit()]
    try:
        out_file = VisualizationService.create_visual_map(idxs)
        return FileResponse(out_file, media_type="text/html", filename="visual_map.html")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
