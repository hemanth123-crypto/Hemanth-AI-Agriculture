"""
tests/test_preprocessing.py
Unit tests for data cleaning, boundary validations, and derived features.
"""

import pytest
import pandas as pd
import numpy as np
from app.utils.preprocessing import clean_data, REQUIRED_COLUMNS

def test_clean_data_removes_duplicates():
    df = pd.DataFrame({
        "Crop": ["Rice", "Rice"],
        "Crop_Year": [2020, 2020],
        "Season": ["Kharif", "Kharif"],
        "State": ["Andhra Pradesh", "Andhra Pradesh"],
        "Area": [1000.0, 1000.0],
        "Production": [3800.0, 3800.0],
        "Yield": [3.8, 3.8],
        "Fertilizer": [120.0, 120.0],
        "Pesticide": [1.0, 1.0],
        "N": [80.0, 80.0],
        "P": [40.0, 40.0],
        "K": [40.0, 40.0],
        "pH": [6.5, 6.5],
        "Temperature": [28.0, 28.0],
        "Rainfall": [1000.0, 1000.0],
        "Humidity": [75.0, 75.0]
    })
    clean_df, report = clean_data(df)
    assert len(clean_df) == 1
    assert report["duplicate_rows_removed"] == 1

def test_clean_data_bounds_clipping():
    df = pd.DataFrame({
        "Crop": ["Wheat"],
        "Crop_Year": [2021],
        "Season": ["Rabi"],
        "State": ["Punjab"],
        "Area": [500.0],
        "Production": [2000.0],
        "Yield": [4.0],
        "Fertilizer": [150.0],
        "Pesticide": [0.8],
        "N": [-10.0],      # Invalid negative
        "P": [50.0],
        "K": [40.0],
        "pH": [15.0],      # Invalid pH > 10
        "Temperature": [70.0], # Extreme temp > 55
        "Rainfall": [-50.0],   # Negative rainfall
        "Humidity": [120.0]    # Humidity > 100
    })
    clean_df, report = clean_data(df)
    row = clean_df.iloc[0]
    assert row["N"] >= 0.0
    assert row["pH"] <= 10.0
    assert row["Temperature"] <= 55.0
    assert row["Rainfall"] >= 0.0
    assert row["Humidity"] <= 100.0

def test_derived_features_generation():
    df = pd.DataFrame({
        "Crop": ["Maize"],
        "Crop_Year": [2022],
        "Season": ["Kharif"],
        "State": ["Karnataka"],
        "Area": [1000.0],
        "Production": [3000.0],
        "Yield": [3.0],
        "Fertilizer": [100.0],
        "Pesticide": [1.0],
        "N": [50.0],
        "P": [30.0],
        "K": [20.0],
        "pH": [6.5],
        "Temperature": [25.0],
        "Rainfall": [500.0],
        "Humidity": [60.0]
    })
    clean_df, _ = clean_data(df)
    row = clean_df.iloc[0]
    assert "NPK_Total" in clean_df.columns
    assert row["NPK_Total"] == pytest.approx(100.0)
    assert "Rain_Temp_Ratio" in clean_df.columns
    assert row["Rain_Temp_Ratio"] == pytest.approx(20.0)
