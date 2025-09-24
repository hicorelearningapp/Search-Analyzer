from fastapi import APIRouter, Form
import re
from services.review_service import ReviewService

router = APIRouter()

@router.post("/review_paper")
async def review_paper(subtopics: str = Form(""), selected_indices: str = Form("")):
    subs = [s.strip() for s in re.split(r'[,\n;]+', subtopics) if s.strip()] or ["Background","Methods","Results"]
    idxs = [int(x.strip())-1 for x in selected_indices.split(",") if x.strip().isdigit()]
    return ReviewService.scaffold_review(subs, idxs)
