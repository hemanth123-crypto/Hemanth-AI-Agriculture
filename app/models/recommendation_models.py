"""
app/models/recommendation_models.py
Models specific to crop recommendations and alternatives.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, model_validator
from app.models.schemas import CropRecommendationItem, HistoricalCase

class RecommendationRequest(BaseModel):
    query: Optional[str] = "Suggest crops for my soil and weather"
    state: Optional[str] = None
    season: Optional[str] = None
    n: Optional[float] = None
    p: Optional[float] = None
    k: Optional[float] = None
    ph: Optional[float] = None
    temperature: Optional[float] = None
    rainfall: Optional[float] = None
    humidity: Optional[float] = None
    top_k: int = 5

class AlternativeCropsRequest(BaseModel):
    current_crop: str
    state: Optional[str] = None
    season: Optional[str] = None
    ph: Optional[float] = None
    rainfall: Optional[float] = None

class RecommendationResponse(BaseModel):
    primary_recommendations: List[CropRecommendationItem]
    alternative_options: List[CropRecommendationItem] = []
    historical_cases: List[HistoricalCase]
    explanation: str
    candidates: Optional[List[Dict[str, Any]]] = None

    @model_validator(mode="after")
    def populate_candidates(self):
        if not self.candidates and self.primary_recommendations:
            self.candidates = [
                {
                    "crop": item.crop,
                    "suitability_probability": item.suitability_score,
                    "risk_level": item.risk,
                    "historical_avg_yield": item.historical_yield_avg,
                    "explanation": item.explanation,
                }
                for item in self.primary_recommendations
            ]
        return self
