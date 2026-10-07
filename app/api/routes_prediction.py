"""
app/api/routes_prediction.py
Machine learning inference endpoints for yield prediction and crop suitability classification.
"""

from fastapi import APIRouter, HTTPException
from app.models.prediction_models import (
    PredictionRequest, SuitabilityRequest, SuitabilityResponse
)
from app.models.schemas import YieldPredictionResult
from app.services.prediction_service import prediction_service
from app.utils.logging import get_logger

logger = get_logger("routes_prediction")
router = APIRouter(prefix="/api", tags=["ML Predictions"])

@router.post("/predict-yield", response_model=YieldPredictionResult)
@router.post("/prediction", response_model=YieldPredictionResult)
def predict_crop_yield(request: PredictionRequest):
    """
    Predicts expected crop yield (tonnes/ha) with confidence intervals
    using the trained Random Forest regressor.
    """
    try:
        return prediction_service.predict_yield(request)
    except Exception as e:
        logger.error(f"Error predicting yield: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/suitability", response_model=SuitabilityResponse)
def evaluate_crop_suitability(request: SuitabilityRequest):
    """
    Assesses crop suitability class ('Suitable', 'Moderately Suitable', 'High Risk')
    using the trained Random Forest classification model.
    """
    try:
        return prediction_service.assess_suitability(request)
    except Exception as e:
        logger.error(f"Error evaluating suitability: {e}")
        raise HTTPException(status_code=500, detail=str(e))
