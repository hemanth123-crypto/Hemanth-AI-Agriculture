"""
app/utils/preprocessing.py
Data preprocessing and cleaning pipeline for Crop Yield Data with Soil and Weather Dataset.
Conforms to Section 6 of project specification.
"""

import os
import json
from pathlib import Path
from typing import Tuple, Dict, Any, List
import pandas as pd
import numpy as np

from app.config.settings import settings
from app.utils.logging import get_logger

logger = get_logger("data_preprocessing")

REQUIRED_COLUMNS = [
    "Crop", "Crop_Year", "Season", "State", "Area", "Production", "Yield",
    "Fertilizer", "Pesticide", "N", "P", "K", "pH", "Temperature", "Rainfall", "Humidity"
]

NUMERIC_COLUMNS = [
    "Crop_Year", "Area", "Production", "Yield", "Fertilizer", "Pesticide",
    "N", "P", "K", "pH", "Temperature", "Rainfall", "Humidity"
]

CATEGORICAL_COLUMNS = ["Crop", "Season", "State"]

SEASON_MAPPING = {
    "kharif": "Kharif",
    "rabi": "Rabi",
    "summer": "Summer",
    "winter": "Winter",
    "autumn": "Autumn",
    "whole year": "Whole Year",
    "annual": "Whole Year"
}

def find_raw_dataset() -> Path:
    """Finds raw CSV dataset in raw directory or falls back to sample directory."""
    raw_dir = settings.DATA_RAW_DIR
    if raw_dir.exists():
        csv_files = list(raw_dir.glob("*.csv"))
        if csv_files:
            logger.info(f"Discovered raw dataset: {csv_files[0]}")
            return csv_files[0]
            
    # Fallback to sample dataset
    if settings.SAMPLE_CSV_FILE.exists():
        logger.info(f"Using synthetic sample dataset at: {settings.SAMPLE_CSV_FILE}")
        return settings.SAMPLE_CSV_FILE

    raise FileNotFoundError(
        f"No dataset found in '{raw_dir}' or sample dataset at '{settings.SAMPLE_CSV_FILE}'."
    )

def load_and_validate_dataset(csv_path: Path) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Loads CSV and validates schema columns."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Dataset path does not exist: {csv_path}")

    df = pd.read_csv(csv_path)
    initial_shape = df.shape
    logger.info(f"Loaded dataset with {initial_shape[0]} rows and {initial_shape[1]} columns.")

    # Match columns case-insensitively
    actual_cols = {col.lower().strip(): col for col in df.columns}
    col_rename = {}
    missing_cols = []
    
    for req in REQUIRED_COLUMNS:
        req_clean = req.lower()
        if req_clean in actual_cols:
            col_rename[actual_cols[req_clean]] = req
        else:
            missing_cols.append(req)

    if missing_cols:
        raise ValueError(f"Dataset is missing required columns: {missing_cols}")

    df = df.rename(columns=col_rename)
    df = df[REQUIRED_COLUMNS].copy()

    validation_report = {
        "source_file": str(csv_path),
        "initial_rows": initial_shape[0],
        "initial_columns": initial_shape[1],
        "is_synthetic": "sample" in str(csv_path).lower()
    }
    return df, validation_report

def clean_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Cleans duplicates, handles missing values, validates boundaries, and flags outliers.
    """
    report: Dict[str, Any] = {}
    
    # 1. Duplicates
    dup_count = int(df.duplicated().sum())
    report["duplicate_rows_removed"] = dup_count
    df = df.drop_duplicates().copy()

    # 2. Missing values
    missing_per_col = df.isnull().sum().to_dict()
    report["missing_values_imputed"] = {k: int(v) for k, v in missing_per_col.items() if v > 0}

    # Impute numeric columns with median
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)

    # Impute categorical columns with mode
    for col in CATEGORICAL_COLUMNS:
        df[col] = df[col].astype(str).str.strip()
        mode_val = df[col].mode()[0] if not df[col].mode().empty else "Unknown"
        df[col] = df[col].replace({"nan": mode_val, "": mode_val})

    # 3. Categorical Normalization
    df["Crop"] = df["Crop"].astype(str).str.title().str.strip()
    df["State"] = df["State"].astype(str).str.title().str.strip()
    df["Season"] = df["Season"].astype(str).str.lower().str.strip().map(lambda s: SEASON_MAPPING.get(s, s.title()))

    # 4. Domain & Biological Boundaries Validation
    # pH: [3.5, 10.0]
    invalid_ph = ((df["pH"] < 3.5) | (df["pH"] > 10.0)).sum()
    df["pH"] = df["pH"].clip(3.5, 10.0)

    # Temperature: [-10.0, 55.0]
    invalid_temp = ((df["Temperature"] < -10.0) | (df["Temperature"] > 55.0)).sum()
    df["Temperature"] = df["Temperature"].clip(0.0, 55.0)

    # Rainfall: >= 0
    invalid_rain = (df["Rainfall"] < 0).sum()
    df["Rainfall"] = df["Rainfall"].clip(lower=0.0)

    # Humidity: [0, 100]
    invalid_humidity = ((df["Humidity"] < 0) | (df["Humidity"] > 100)).sum()
    df["Humidity"] = df["Humidity"].clip(0.0, 100.0)

    # N, P, K: >= 0
    invalid_n = (df["N"] < 0).sum()
    invalid_p = (df["P"] < 0).sum()
    invalid_k = (df["K"] < 0).sum()
    df["N"] = df["N"].clip(lower=0)
    df["P"] = df["P"].clip(lower=0)
    df["K"] = df["K"].clip(lower=0)

    # Fertilizer, Pesticide, Area, Production, Yield >= 0
    df["Fertilizer"] = df["Fertilizer"].clip(lower=0.0)
    df["Pesticide"] = df["Pesticide"].clip(lower=0.0)
    df["Area"] = df["Area"].clip(lower=0.1)
    df["Production"] = df["Production"].clip(lower=0.0)
    df["Yield"] = df["Yield"].clip(lower=0.01)

    report["boundary_corrections"] = {
        "pH_out_of_bounds": int(invalid_ph),
        "temperature_out_of_bounds": int(invalid_temp),
        "rainfall_negative": int(invalid_rain),
        "humidity_out_of_bounds": int(invalid_humidity),
        "npk_negative": int(invalid_n + invalid_p + invalid_k)
    }

    # 5. Outlier Detection using IQR
    outlier_counts = {}
    for col in ["Yield", "Rainfall", "Temperature", "Fertilizer", "Pesticide"]:
        q25 = df[col].quantile(0.25)
        q75 = df[col].quantile(0.75)
        iqr = q75 - q25
        lower_bound = q25 - 1.5 * iqr
        upper_bound = q75 + 1.5 * iqr
        outlier_count = int(((df[col] < lower_bound) | (df[col] > upper_bound)).sum())
        outlier_counts[col] = outlier_count
    report["outliers_detected_iqr"] = outlier_counts

    # 6. Derived Features
    df["NPK_Total"] = (df["N"] + df["P"] + df["K"]).round(2)
    df["NPK_Ratio_N"] = (df["N"] / (df["NPK_Total"] + 1e-5)).round(4)
    df["NPK_Ratio_P"] = (df["P"] / (df["NPK_Total"] + 1e-5)).round(4)
    df["NPK_Ratio_K"] = (df["K"] / (df["NPK_Total"] + 1e-5)).round(4)
    df["Rain_Temp_Ratio"] = (df["Rainfall"] / (df["Temperature"] + 1e-5)).round(3)
    df["Fertilizer_Per_Area"] = (df["Fertilizer"] / (df["Area"] + 1e-5)).round(4)

    report["final_rows"] = len(df)
    report["unique_crops"] = int(df["Crop"].nunique())
    report["unique_states"] = int(df["State"].nunique())
    report["unique_seasons"] = int(df["Season"].nunique())

    return df, report

def run_preprocessing(input_path: Path = None, output_dir: Path = None) -> Tuple[Path, Path]:
    """Runs end-to-end preprocessing, saves processed CSV and data quality report."""
    if output_dir is None:
        output_dir = settings.DATA_PROCESSED_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    if input_path is None:
        input_path = find_raw_dataset()

    df, val_report = load_and_validate_dataset(input_path)
    clean_df, clean_report = clean_data(df)

    processed_file = output_dir / "processed_data.csv"
    report_file = output_dir / "data_quality_report.json"

    clean_df.to_csv(processed_file, index=False)
    
    full_report = {
        "status": "SUCCESS",
        "validation": val_report,
        "cleaning": clean_report,
        "feature_columns": list(clean_df.columns)
    }

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2)

    logger.info(f"Processed dataset saved: {processed_file} ({len(clean_df)} records)")
    logger.info(f"Data quality report saved: {report_file}")
    return processed_file, report_file
