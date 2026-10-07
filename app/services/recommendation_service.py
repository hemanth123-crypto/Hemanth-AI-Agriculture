"""
app/services/recommendation_service.py
Service providing specialized crop recommendation workflows.
"""

from typing import List, Dict, Any, Optional
from app.agents.crop_recommendation_agent import crop_recommendation_agent
from app.agents.retrieval_agent import retrieval_agent
from app.models.schemas import InterpretedConditions, CropRecommendationItem
from app.models.recommendation_models import RecommendationRequest, RecommendationResponse

class RecommendationService:
    def get_recommendations(self, req: RecommendationRequest) -> RecommendationResponse:
        cond = InterpretedConditions(
            state=req.state,
            season=req.season,
            n=req.n,
            p=req.p,
            k=req.k,
            ph=req.ph,
            temperature=req.temperature,
            rainfall=req.rainfall,
            humidity=req.humidity
        )
        cases = retrieval_agent.execute_retrieval(query=req.query or "", conditions=cond, top_k=req.top_k)
        primary = crop_recommendation_agent.recommend(conditions=cond, retrieved_cases=cases, is_alternative_request=False)
        alternatives = primary[1:] if len(primary) > 1 else []
        
        explanation = (
            f"Evaluated {len(cases)} historical farming cases. "
            f"Recommended {len(primary)} compatible crop cultivars ranked by empirical suitability."
        )

        return RecommendationResponse(
            primary_recommendations=primary,
            alternative_options=alternatives,
            historical_cases=cases,
            explanation=explanation
        )

recommendation_service = RecommendationService()
