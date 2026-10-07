"""
tests/test_evaluation.py
Unit tests for retrieval evaluation metrics, guardrail benchmarking, and LLM-as-a-judge.
"""

import pytest
from app.evaluation.retrieval_metrics import retrieval_evaluator
from app.evaluation.guardrail_evaluation import guardrail_evaluator
from app.evaluation.llm_judge import llm_judge
from app.models.schemas import CropRecommendationItem, HistoricalCase

def test_retrieval_evaluation():
    metrics = retrieval_evaluator.evaluate_retrieval()
    assert metrics["total_benchmark_queries"] > 0
    assert 0.0 <= metrics["precision_at_5"] <= 1.0
    assert 0.0 <= metrics["mrr"] <= 1.0
    assert 0.0 <= metrics["hit_rate_at_5"] <= 1.0

def test_guardrail_evaluator():
    res = guardrail_evaluator.evaluate_guardrails()
    assert res["total_test_cases"] > 0
    assert res["guardrail_accuracy_rate"] >= 0.90
    assert res["prompt_injection_detection_rate"] == 1.0

def test_llm_judge_local_scoring():
    cases = [
        HistoricalCase(
            case_id="C1", crop="Rice", year=2020, season="Kharif", state="AP",
            area=100.0, production=380.0, yield_val=3.8, fertilizer=100.0, pesticide=1.0,
            n=80.0, p=40.0, k=40.0, ph=6.5, temperature=28.0, rainfall=1000.0, humidity=75.0
        )
    ]
    recs = [
        CropRecommendationItem(
            crop="Rice", suitability_score=0.92, suitability_label="Suitable", risk="Low",
            historical_yield_avg=3.8, number_of_similar_cases=1, matching_conditions={},
            explanation="Rice fits well.", confidence=0.9, supporting_cases=["C1"], limitations="None"
        )
    ]
    advisory = "AGRICULTURAL ADVISORY\nPREDICTED YIELD: 3.8 t/ha\nRISK ANALYSIS: Low risk"
    judge_res = llm_judge.evaluate("Rice in AP", recs, cases, advisory)
    assert judge_res.overall > 0.70
    assert judge_res.groundedness == 1.0
    assert judge_res.safety == 1.0
