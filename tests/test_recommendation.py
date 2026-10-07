"""
tests/test_recommendation.py
Unit tests for crop recommendation and risk analysis agents.
"""

import pytest
from app.agents.crop_recommendation_agent import crop_recommendation_agent
from app.agents.risk_analysis_agent import risk_analysis_agent
from app.models.schemas import InterpretedConditions, HistoricalCase

def test_crop_recommendation_agent():
    cond = InterpretedConditions(state="Andhra Pradesh", season="Kharif", ph=6.5)
    cases = [
        HistoricalCase(
            case_id="C1", crop="Rice", year=2020, season="Kharif", state="Andhra Pradesh",
            area=100.0, production=380.0, yield_val=3.8, fertilizer=100.0, pesticide=1.0,
            n=80.0, p=40.0, k=40.0, ph=6.5, temperature=28.0, rainfall=1200.0, humidity=75.0,
            relevance_score=0.95
        ),
        HistoricalCase(
            case_id="C2", crop="Maize", year=2020, season="Kharif", state="Andhra Pradesh",
            area=100.0, production=320.0, yield_val=3.2, fertilizer=100.0, pesticide=1.0,
            n=80.0, p=40.0, k=40.0, ph=6.5, temperature=28.0, rainfall=1000.0, humidity=70.0,
            relevance_score=0.88
        )
    ]
    recs = crop_recommendation_agent.recommend(cond, cases)
    assert len(recs) == 2
    assert recs[0].crop in ["Rice", "Maize"]
    assert recs[0].suitability_score > 0.5
    assert recs[0].risk in ["Low", "Moderate", "High"]

def test_risk_analysis_agent():
    cond_stress = InterpretedConditions(ph=4.5, rainfall=300.0, temperature=42.0)
    risk_res = risk_analysis_agent.analyze_risk(cond_stress)
    assert risk_res.overall_risk == "High"
    assert len(risk_res.risk_factors) >= 2
    assert len(risk_res.mitigations) >= 2
