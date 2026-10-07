"""
tests/test_hybrid_search.py
Unit tests for hybrid search weighting, metadata filtering, and re-ranking.
"""

import pytest
from app.utils.helpers import calculate_hybrid_score
from app.rag.metadata_filter import MetadataFilter
from app.rag.reranker import CaseReranker

def test_calculate_hybrid_score():
    score = calculate_hybrid_score(
        semantic_score=1.0,
        keyword_score=0.8,
        metadata_score=0.5,
        alpha=0.5,
        beta=0.3,
        gamma=0.2
    )
    # 0.5*1.0 + 0.3*0.8 + 0.2*0.5 = 0.5 + 0.24 + 0.10 = 0.84
    assert score == pytest.approx(0.84)

def test_metadata_filter_matching():
    case = {
        "crop": "Rice",
        "state": "Andhra Pradesh",
        "season": "Kharif",
        "ph": 6.5,
        "rainfall": 1200.0
    }

    # Perfect match
    filters_exact = {"crop": "Rice", "state": "Andhra Pradesh", "ph": 6.5}
    score_exact = MetadataFilter.compute_match_score(case, filters_exact)
    assert score_exact == 1.0

    # Partial match
    filters_partial = {"crop": "Wheat", "state": "Andhra Pradesh"}
    score_partial = MetadataFilter.compute_match_score(case, filters_partial)
    assert score_partial == 0.5

def test_case_reranker_environmental_similarity():
    case_meta = {"ph": 6.5, "temperature": 28.0, "rainfall": 1000.0, "n": 80.0}
    query_exact = {"ph": 6.5, "temperature": 28.0, "rainfall": 1000.0, "n": 80.0}
    sim_exact = CaseReranker.calculate_environmental_similarity(case_meta, query_exact)
    assert sim_exact == pytest.approx(1.0)

    query_divergent = {"ph": 4.0, "temperature": 45.0, "rainfall": 200.0, "n": 10.0}
    sim_divergent = CaseReranker.calculate_environmental_similarity(case_meta, query_divergent)
    assert sim_divergent < sim_exact
