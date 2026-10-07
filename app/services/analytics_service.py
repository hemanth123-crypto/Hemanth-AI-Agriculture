"""
app/services/analytics_service.py
Service for soil/weather/input analytics and feature importances.
"""

from typing import Optional
from app.agents.agricultural_analysis_agent import agricultural_analysis_agent
from app.models.schemas import ImpactAnalysisResult

class AnalyticsService:
    def get_impact_analysis(self, crop: Optional[str] = None) -> ImpactAnalysisResult:
        return agricultural_analysis_agent.analyze_factors(crop=crop)

analytics_service = AnalyticsService()
