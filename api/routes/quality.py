"""
Routes qualité pipeline — section 15.
"""
from fastapi import APIRouter, HTTPException

from src.utils.db import get_pipeline_quality
from api.schemas.crypto import PipelineQuality

router = APIRouter()


@router.get("/pipeline/quality", response_model=PipelineQuality)
def pipeline_quality(hours: int = 24):
    if hours <= 0 or hours > 720:
        raise HTTPException(status_code=400, detail="Le paramètre 'hours' doit être entre 1 et 720")
    return get_pipeline_quality(hours=hours)
