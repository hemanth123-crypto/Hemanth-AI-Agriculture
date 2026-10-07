"""
app/ml/model_training.py
Training pipeline for Crop Suitability Classifier and Yield Prediction Regressor.
Computes evaluation metrics (Accuracy, Precision, Recall, F1, Confusion Matrix, MAE, RMSE, R2)
and persists models and metrics reports.
Conforms to Sections 18, 19, and 25 of project specification.
"""

import os
import json
import pickle
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, mean_absolute_error, mean_squared_error, r2_score
)

from app.config.settings import settings
from app.utils.logging import get_logger
from app.ml.crop_suitability import CropSuitabilityModel
from app.ml.yield_prediction import YieldPredictionModel

logger = get_logger("model_training")

def assign_suitability_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    Labels historical records as 'Suitable', 'Moderately Suitable', or 'High Risk'
    based on relative yield performance per crop.
    """
    df = df.copy()
    labels = []
    
    # Calculate crop-specific percentiles
    crop_stats = df.groupby("Crop")["Yield"].agg(["median", "std"]).to_dict("index")

    for _, row in df.iterrows():
        crop = row["Crop"]
        y = float(row["Yield"])
        stats = crop_stats.get(crop, {"median": 3.0, "std": 1.0})
        median = stats["median"]
        std = stats["std"] if not np.isnan(stats["std"]) and stats["std"] > 0 else 0.5

        if y >= (median + 0.10 * std):
            labels.append("Suitable")
        elif y >= (median - 0.50 * std):
            labels.append("Moderately Suitable")
        else:
            labels.append("High Risk")

    df["Suitability"] = labels
    return df

def train_and_evaluate_models() -> Dict[str, Any]:
    """
    Executes full offline ML training:
    1. Loads processed dataset
    2. Derives ground truth suitability targets
    3. Trains and evaluates CropSuitabilityModel
    4. Trains and evaluates YieldPredictionModel
    5. Saves models and metrics report to disk
    """
    logger.info("Starting ML model training pipeline...")
    
    if not settings.PROCESSED_CSV_FILE.exists():
        from app.utils.preprocessing import run_preprocessing
        run_preprocessing()

    df = pd.read_csv(settings.PROCESSED_CSV_FILE)
    df = assign_suitability_labels(df)

    # 80/20 train/test split
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df["Suitability"])
    logger.info(f"Split dataset: {len(train_df)} train, {len(test_df)} test.")

    # -------------------------------------------------------------
    # 1. Crop Suitability Classifier
    # -------------------------------------------------------------
    logger.info("Training CropSuitabilityModel (RandomForestClassifier)...")
    suitability_model = CropSuitabilityModel()
    suitability_model.fit(train_df, target_col="Suitability")

    # Evaluate on test set
    X_test_clf = test_df[["Crop", "Season", "State", "N", "P", "K", "pH", "Temperature", "Rainfall", "Humidity", "Fertilizer", "Pesticide"]]
    y_test_clf = test_df["Suitability"]
    
    X_test_trans = suitability_model.preprocessor.transform(X_test_clf)
    y_pred_clf = suitability_model.classifier.predict(X_test_trans)

    clf_acc = float(accuracy_score(y_test_clf, y_pred_clf))
    clf_prec = float(precision_score(y_test_clf, y_pred_clf, average="weighted", zero_division=0))
    clf_rec = float(recall_score(y_test_clf, y_pred_clf, average="weighted", zero_division=0))
    clf_f1 = float(f1_score(y_test_clf, y_pred_clf, average="weighted", zero_division=0))
    cm = confusion_matrix(y_test_clf, y_pred_clf, labels=suitability_model.classes_).tolist()

    suitability_metrics = {
        "model_type": "RandomForestClassifier",
        "classes": suitability_model.classes_,
        "accuracy": round(clf_acc, 4),
        "precision": round(clf_prec, 4),
        "recall": round(clf_rec, 4),
        "f1_score": round(clf_f1, 4),
        "confusion_matrix": cm,
        "test_samples": len(test_df)
    }
    logger.info(f"Suitability Classifier Results: Acc={clf_acc:.4f}, F1={clf_f1:.4f}")

    # -------------------------------------------------------------
    # 2. Yield Prediction Regressor
    # -------------------------------------------------------------
    logger.info("Training YieldPredictionModel (RandomForestRegressor)...")
    yield_model = YieldPredictionModel()
    yield_model.fit(train_df, target_col="Yield")

    X_test_reg = test_df[["Crop", "Season", "State", "Area", "Fertilizer", "Pesticide", "N", "P", "K", "pH", "Temperature", "Rainfall", "Humidity"]]
    y_test_reg = test_df["Yield"]

    X_reg_trans = yield_model.preprocessor.transform(X_test_reg)
    y_pred_reg = yield_model.regressor.predict(X_reg_trans)

    reg_mae = float(mean_absolute_error(y_test_reg, y_pred_reg))
    reg_rmse = float(np.sqrt(mean_squared_error(y_test_reg, y_pred_reg)))
    reg_r2 = float(r2_score(y_test_reg, y_pred_reg))

    yield_model.r2_score = reg_r2
    yield_model.mae = reg_mae

    yield_metrics = {
        "model_type": "RandomForestRegressor",
        "mae": round(reg_mae, 4),
        "rmse": round(reg_rmse, 4),
        "r2_score": round(reg_r2, 4),
        "test_samples": len(test_df)
    }
    logger.info(f"Yield Regressor Results: R2={reg_r2:.4f}, MAE={reg_mae:.4f}, RMSE={reg_rmse:.4f}")

    # -------------------------------------------------------------
    # 3. Save Models and Metadata
    # -------------------------------------------------------------
    settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    settings.EVALUATION_DIR.mkdir(parents=True, exist_ok=True)
    (settings.EVALUATION_DIR / "reports").mkdir(parents=True, exist_ok=True)

    with open(settings.SUITABILITY_MODEL_FILE, "wb") as f:
        pickle.dump(suitability_model, f)
    logger.info(f"Saved suitability model to: {settings.SUITABILITY_MODEL_FILE}")

    with open(settings.YIELD_MODEL_FILE, "wb") as f:
        pickle.dump(yield_model, f)
    logger.info(f"Saved yield prediction model to: {settings.YIELD_MODEL_FILE}")

    feature_metadata = {
        "categorical_features": ["Crop", "Season", "State"],
        "numeric_features": ["N", "P", "K", "pH", "Temperature", "Rainfall", "Humidity", "Fertilizer", "Pesticide"],
        "crops": sorted(list(df["Crop"].unique())),
        "states": sorted(list(df["State"].unique())),
        "seasons": sorted(list(df["Season"].unique())),
        "training_samples": len(train_df),
        "test_samples": len(test_df)
    }
    with open(settings.FEATURE_METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(feature_metadata, f, indent=2)

    # -------------------------------------------------------------
    # 4. Save Evaluation Metrics (Section 25)
    # -------------------------------------------------------------
    ml_report = {
        "suitability_classifier": suitability_metrics,
        "yield_regressor": yield_metrics,
        "training_data_records": len(df),
        "features": feature_metadata
    }

    metrics_file = settings.EVALUATION_DIR / "reports" / "ml_metrics.json"
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(ml_report, f, indent=2)
    logger.info(f"Saved ML metrics report to: {metrics_file}")

    return ml_report
