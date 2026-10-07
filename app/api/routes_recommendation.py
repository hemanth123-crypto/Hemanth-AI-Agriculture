"""
app/api/routes_recommendation.py
Crop recommendation endpoints for primary and alternative crop identification.
"""

from fastapi import APIRouter, HTTPException
from app.models.recommendation_models import (
    RecommendationRequest, RecommendationResponse, AlternativeCropsRequest
)
from app.services.recommendation_service import recommendation_service
from app.utils.logging import get_logger

logger = get_logger("routes_recommendation")
router = APIRouter(prefix="/api", tags=["Crop Recommendation"])

@router.post("/recommend", response_model=RecommendationResponse)
def get_crop_recommendations(request: RecommendationRequest):
    """
    Recommends suitable crops based on user-provided soil, weather, and regional parameters.
    """
    try:
        return recommendation_service.get_recommendations(request)
    except Exception as e:
        logger.error(f"Error generating crop recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alternatives", response_model=RecommendationResponse)
def get_alternative_crops(request: AlternativeCropsRequest):
    """
    Suggests alternative crop cultivars for the current crop under similar regional conditions.
    """
    try:
        rec_req = RecommendationRequest(
            query=f"Alternative crops for {request.current_crop} in {request.state or 'the region'}",
            state=request.state,
            season=request.season,
            ph=request.ph,
            rainfall=request.rainfall
        )
        return recommendation_service.get_recommendations(rec_req)
    except Exception as e:
        logger.error(f"Error suggesting alternative crops: {e}")
        raise HTTPException(status_code=500, detail=str(e))
