"""
app/models/prediction_models.py
Models specific to ML yield prediction, crop suitability classification, and impact analysis.
"""

from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class PredictionRequest(BaseModel):
    crop: str
    season: str = "Kharif"
    state: str = "Andhra Pradesh"
    area: float = 1000.0
    fertilizer: float = 120.0
    pesticide: float = 1.0
    n: float = 80.0
    p: float = 40.0
    k: float = 40.0
    ph: float = 6.5
    temperature: float = 28.0
    rainfall: float = 1000.0
    humidity: float = 75.0

class SuitabilityRequest(BaseModel):
    crop: str
    season: str = "Kharif"
    state: str = "Andhra Pradesh"
    n: float = 80.0
    p: float = 40.0
    k: float = 40.0
    ph: float = 6.5
    temperature: float = 28.0
    rainfall: float = 1000.0
    humidity: float = 75.0
    fertilizer: float = 120.0
    pesticide: float = 1.0

class SuitabilityResponse(BaseModel):
    crop: str
    suitability_class: str
    confidence: float
    probability_distribution: Dict[str, float]
    advisory_recommendation: str

class ImpactAnalysisRequest(BaseModel):
    crop: Optional[str] = None
    state: Optional[str] = None
