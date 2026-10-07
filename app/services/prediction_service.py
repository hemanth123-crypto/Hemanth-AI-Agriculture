"""
app/services/prediction_service.py
Service wrapping ML yield prediction and crop suitability classification endpoints.
"""

from typing import Dict, Any
from app.models.prediction_models import PredictionRequest, SuitabilityRequest, SuitabilityResponse
from app.models.schemas import YieldPredictionResult
from app.ml.model_loader import model_manager

class PredictionService:
    def predict_yield(self, req: PredictionRequest) -> YieldPredictionResult:
        sample = req.model_dump()
        return model_manager.yield_model.predict(sample)

    def assess_suitability(self, req: SuitabilityRequest) -> SuitabilityResponse:
        sample = req.model_dump()
        top_cls, conf, probs = model_manager.suitability_model.predict(sample)

        advice = {
            "Suitable": f"{req.crop} is well-adapted to the specified soil and climatic conditions.",
            "Moderately Suitable": f"{req.crop} is viable but may require nutrient supplementation or moisture management.",
            "High Risk": f"{req.crop} faces significant environmental stress under these parameters. Alternative crops recommended."
        }.get(top_cls, "Suitability evaluated.")

        return SuitabilityResponse(
            crop=req.crop,
            suitability_class=top_cls,
            confidence=conf,
            probability_distribution=probs,
            advisory_recommendation=advice
        )

prediction_service = PredictionService()
