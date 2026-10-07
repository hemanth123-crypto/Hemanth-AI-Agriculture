"""
app/api/routes_analysis.py
Soil, weather, and farming input impact analysis endpoint.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException
from app.models.prediction_models import ImpactAnalysisRequest
from app.models.schemas import ImpactAnalysisResult
from app.services.analytics_service import analytics_service
from app.utils.logging import get_logger

logger = get_logger("routes_analysis")
router = APIRouter(prefix="/api", tags=["Impact Analysis"])

@router.post("/analyze-impact", response_model=ImpactAnalysisResult)
def analyze_agronomic_impacts(request: ImpactAnalysisRequest):
    """
    Computes statistical feature importances and Pearson correlations with yield,
    strictly distinguishing correlation from causation.
    """
    try:
        return analytics_service.get_impact_analysis(crop=request.crop)
    except Exception as e:
        logger.error(f"Error analyzing impacts: {e}")
        raise HTTPException(status_code=500, detail=str(e))
