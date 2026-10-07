"""
tests/test_api.py
Integration tests for FastAPI endpoints: /health, /api/query, /api/search, /api/feedback.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    """
    Health endpoint test.
    Uses the lifespan-enabled context manager so indexes and models are initialized.
    """
    with TestClient(app) as lc:
        response = lc.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    # vector_store_ready and model loaded flags should be True after lifespan startup
    assert data["vector_store_ready"] is True

def test_metadata_endpoints():
    r_crops = client.get("/api/crops")
    assert r_crops.status_code == 200
    assert "Rice" in r_crops.json()

    r_states = client.get("/api/states")
    assert r_states.status_code == 200
    assert len(r_states.json()) > 0

def test_advisory_query_endpoint():
    payload = {
        "query": "Which crops are suitable for Kharif season in Andhra Pradesh with pH 6.5 and rainfall around 1000 mm?"
    }
    response = client.post("/api/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert "similar_cases" in data
    assert "formatted_advisory" in data
    assert "AGRICULTURAL ADVISORY" in data["formatted_advisory"]
    assert len(data["recommendations"]) > 0

def test_search_cases_endpoint():
    payload = {
        "query": "Rice cultivation in Andhra Pradesh",
        "top_k": 3
    }
    response = client.post("/api/search", json=payload)
    assert response.status_code == 200
    cases = response.json()
    assert len(cases) <= 3
    if cases:
        assert "case_id" in cases[0]
        assert "crop" in cases[0]

def test_yield_prediction_endpoint():
    payload = {
        "crop": "Rice",
        "season": "Kharif",
        "state": "Andhra Pradesh",
        "area": 1000.0,
        "fertilizer": 120.0,
        "pesticide": 1.0,
        "n": 80.0,
        "p": 40.0,
        "k": 40.0,
        "ph": 6.5,
        "temperature": 28.0,
        "rainfall": 1100.0,
        "humidity": 75.0
    }
    response = client.post("/api/predict-yield", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_yield"] > 0.0
    assert data["unit"] == "tonnes/hectare"

def test_suitability_endpoint():
    payload = {
        "crop": "Rice",
        "season": "Kharif",
        "state": "Andhra Pradesh",
        "ph": 6.5,
        "rainfall": 1200.0
    }
    response = client.post("/api/suitability", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["suitability_class"] in ["Suitable", "Moderately Suitable", "High Risk"]

def test_feedback_endpoint():
    payload = {
        "query": "Rice in AP",
        "recommendation": "Rice",
        "rating": 5,
        "thumbs": "up",
        "comments": "Accurate recommendation."
    }
    response = client.post("/api/feedback", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "SUCCESS"
