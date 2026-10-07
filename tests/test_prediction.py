"""
tests/test_prediction.py
Unit tests for Crop Suitability Classifier and Yield Prediction Regressor.
"""

import pytest
from app.ml.model_loader import model_manager
from app.ml.feature_analysis import ImpactAnalyzer
import pandas as pd

def test_crop_suitability_prediction():
    sample = {
        "crop": "Rice",
        "season": "Kharif",
        "state": "Andhra Pradesh",
        "ph": 6.5,
        "rainfall": 1200.0,
        "temperature": 28.0,
        "n": 80.0,
        "p": 40.0,
        "k": 40.0,
        "fertilizer": 120.0,
        "pesticide": 1.0
    }
    suit_cls, conf, probs = model_manager.suitability_model.predict(sample)
    assert suit_cls in ["Suitable", "Moderately Suitable", "High Risk"]
    assert 0.0 <= conf <= 1.0
    assert sum(probs.values()) == pytest.approx(1.0, rel=1e-2)

def test_yield_prediction():
    sample = {
        "crop": "Wheat",
        "season": "Rabi",
        "state": "Punjab",
        "area": 1000.0,
        "fertilizer": 150.0,
        "pesticide": 1.0,
        "n": 100.0,
        "p": 50.0,
        "k": 40.0,
        "ph": 6.8,
        "temperature": 18.0,
        "rainfall": 500.0,
        "humidity": 60.0
    }
    res = model_manager.yield_model.predict(sample)
    assert res.predicted_yield > 0.0
    assert res.lower_bound <= res.predicted_yield <= res.upper_bound
    assert res.unit == "tonnes/hectare"
    assert len(res.important_factors) > 0

def test_impact_analysis():
    df = pd.DataFrame({
        "Crop": ["Rice"] * 20,
        "Yield": [3.0, 3.2, 3.5, 3.8, 4.0, 3.9, 3.1, 3.6, 3.7, 4.1] * 2,
        "N": [70, 75, 80, 85, 90, 88, 72, 82, 86, 92] * 2,
        "P": [30, 35, 40, 45, 50, 48, 32, 42, 46, 52] * 2,
        "K": [30, 35, 40, 45, 50, 48, 32, 42, 46, 52] * 2,
        "pH": [6.0, 6.2, 6.5, 6.6, 6.5, 6.4, 6.1, 6.5, 6.7, 6.8] * 2,
        "Temperature": [26, 27, 28, 29, 28, 27, 26, 28, 29, 30] * 2,
        "Rainfall": [1000, 1100, 1200, 1300, 1250, 1200, 1050, 1220, 1280, 1350] * 2,
        "Humidity": [70, 72, 75, 78, 76, 74, 71, 75, 77, 80] * 2,
        "Fertilizer": [120, 125, 130, 135, 140, 138, 122, 132, 136, 142] * 2,
        "Pesticide": [1.0, 1.1, 1.2, 1.2, 1.3, 1.2, 1.0, 1.2, 1.2, 1.3] * 2
    })
    res = ImpactAnalyzer.analyze_dataset_impacts(df)
    assert len(res.correlations_with_yield) > 0
    assert len(res.feature_importances) > 0
    assert "association" in res.correlation_vs_causation_note.lower()
