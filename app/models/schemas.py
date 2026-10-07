"""
app/models/schemas.py
Comprehensive Pydantic schemas for request validation, structured agent outputs,
retrieval cases, ML predictions, evaluation metrics, and advisory responses.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class QueryIntent(str, Enum):
    CASE_SIMILARITY = "CASE_SIMILARITY"
    CROP_RECOMMENDATION = "CROP_RECOMMENDATION"
    ALTERNATIVE_CROP = "ALTERNATIVE_CROP"
    YIELD_ANALYSIS = "YIELD_ANALYSIS"
    YIELD_PREDICTION = "YIELD_PREDICTION"
    SOIL_ANALYSIS = "SOIL_ANALYSIS"
    WEATHER_ANALYSIS = "WEATHER_ANALYSIS"
    INPUT_ANALYSIS = "INPUT_ANALYSIS"
    CROP_SUITABILITY = "CROP_SUITABILITY"
    GENERAL_AGRICULTURE = "GENERAL_AGRICULTURE"
    UNSUPPORTED = "UNSUPPORTED"

class InterpretedConditions(BaseModel):
    crop: Optional[str] = None
    season: Optional[str] = None
    state: Optional[str] = None
    year: Optional[int] = None
    n: Optional[float] = Field(default=None, description="Nitrogen (kg/ha)")
    p: Optional[float] = Field(default=None, description="Phosphorus (kg/ha)")
    k: Optional[float] = Field(default=None, description="Potassium (kg/ha)")
    ph: Optional[float] = Field(default=None, description="Soil pH value")
    temperature: Optional[float] = Field(default=None, description="Temperature (°C)")
    rainfall: Optional[float] = Field(default=None, description="Rainfall (mm)")
    humidity: Optional[float] = Field(default=None, description="Relative humidity (%)")
    fertilizer: Optional[float] = Field(default=None, description="Fertilizer input")
    pesticide: Optional[float] = Field(default=None, description="Pesticide input")
    area: Optional[float] = Field(default=None, description="Land area in hectares")
    objective: Optional[str] = Field(default="high_yield", description="User objective")

class QueryClassificationResult(BaseModel):
    intent: QueryIntent
    confidence: float = Field(ge=0.0, le=1.0)
    interpreted_conditions: InterpretedConditions
    reasoning: str

class HistoricalCase(BaseModel):
    case_id: str
    crop: str
    year: int
    season: str
    state: str
    area: float
    production: float
    yield_val: float
    fertilizer: float
    pesticide: float
    n: float
    p: float
    k: float
    ph: float
    temperature: float
    rainfall: float
    humidity: float
    relevance_score: float = 0.0
    semantic_score: float = 0.0
    keyword_score: float = 0.0
    metadata_score: float = 0.0
    match_reasons: List[str] = []

class CropRecommendationItem(BaseModel):
    crop: str
    suitability_score: float = Field(ge=0.0, le=1.0)
    suitability_label: str = Field(description="Suitable, Moderately Suitable, or High Risk")
    risk: str = Field(description="Low, Moderate, High")
    historical_yield_avg: float
    number_of_similar_cases: int
    matching_conditions: Dict[str, Any]
    explanation: str
    confidence: float = Field(ge=0.0, le=1.0)
    supporting_cases: List[str] = []
    limitations: str

class YieldPredictionResult(BaseModel):
    crop: str
    predicted_yield: float
    lower_bound: float
    upper_bound: float
    unit: str = "tonnes/hectare"
    confidence_interval: str
    important_factors: List[str]
    model_name: str
    r2_score: float

class RiskAnalysisResult(BaseModel):
    overall_risk: str
    risk_factors: List[str]
    mitigations: List[str]

class ImpactAnalysisResult(BaseModel):
    feature_importances: Dict[str, float]
    correlations_with_yield: Dict[str, float]
    scientific_interpretation: str
    correlation_vs_causation_note: str = (
        "Historical records show an association between these factors and yield. "
        "Correlation does not imply direct causation, as micro-climates, soil biome, "
        "and crop genetics also interact."
    )

class LLMJudgeResult(BaseModel):
    relevance: float = Field(ge=0.0, le=1.0)
    groundedness: float = Field(ge=0.0, le=1.0)
    recommendation_quality: float = Field(ge=0.0, le=1.0)
    safety: float = Field(ge=0.0, le=1.0)
    overall: float = Field(ge=0.0, le=1.0)
    reason: str

class AdvisoryRequest(BaseModel):
    query: str
    crop: Optional[str] = None
    state: Optional[str] = None
    season: Optional[str] = None
    n: Optional[float] = None
    p: Optional[float] = None
    k: Optional[float] = None
    ph: Optional[float] = None
    temperature: Optional[float] = None
    rainfall: Optional[float] = None
    humidity: Optional[float] = None
    top_k: Optional[int] = 5

class AdvisoryResponse(BaseModel):
    query: str
    intent: QueryIntent
    interpreted_conditions: InterpretedConditions
    recommendations: List[CropRecommendationItem]
    similar_cases: List[HistoricalCase]
    risk_analysis: Optional[RiskAnalysisResult] = None
    yield_prediction: Optional[YieldPredictionResult] = None
    impact_analysis: Optional[ImpactAnalysisResult] = None
    validation: Optional[LLMJudgeResult] = None
    formatted_advisory: str
    limitations: List[str]
    execution_time_ms: float

class FeedbackRequest(BaseModel):
    query: str
    recommendation: Optional[str] = ""
    retrieved_cases: Optional[List[str]] = []
    rating: int = Field(ge=1, le=5)
    thumbs: Optional[str] = Field(default="up", description="'up' or 'down'")
    comments: Optional[str] = ""

class FeedbackResponse(BaseModel):
    status: str
    message: str
    feedback_id: str
