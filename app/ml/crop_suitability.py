"""
app/ml/crop_suitability.py
Machine learning classification model for crop suitability assessment.
Categorizes crop viability into 'Suitable', 'Moderately Suitable', or 'High Risk'.
Conforms to Section 18 of project specification.
"""

from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer

from app.utils.logging import get_logger

logger = get_logger("crop_suitability")

NUMERIC_FEATURES = ["N", "P", "K", "pH", "Temperature", "Rainfall", "Humidity", "Fertilizer", "Pesticide"]
CATEGORICAL_FEATURES = ["Crop", "Season", "State"]

class CropSuitabilityModel:
    def __init__(self):
        self.preprocessor = ColumnTransformer(
            transformers=[
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES),
                ("num", "passthrough", NUMERIC_FEATURES)
            ]
        )
        self.classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=12,
            min_samples_split=4,
            random_state=42
        )
        self.classes_ = ["High Risk", "Moderately Suitable", "Suitable"]
        self.is_trained = False

    def fit(self, df: pd.DataFrame, target_col: str = "Suitability"):
        """Trains the Random Forest classification model."""
        X = df[CATEGORICAL_FEATURES + NUMERIC_FEATURES]
        y = df[target_col]

        X_trans = self.preprocessor.fit_transform(X)
        self.classifier.fit(X_trans, y)
        self.classes_ = list(self.classifier.classes_)
        self.is_trained = True
        logger.info(f"Fitted CropSuitabilityModel with classes: {self.classes_}")

    def predict(self, sample: Dict[str, Any]) -> Tuple[str, float, Dict[str, float]]:
        """
        Predicts suitability class for an agricultural scenario.
        Returns: (suitability_class, confidence, probabilities_dict)
        """
        if not self.is_trained:
            # Fallback heuristic
            return self._heuristic_fallback(sample)

        try:
            # Format row
            row = {
                "Crop": str(sample.get("crop", "Rice")),
                "Season": str(sample.get("season", "Kharif")),
                "State": str(sample.get("state", "Andhra Pradesh")),
                "N": float(sample.get("n", 80.0)),
                "P": float(sample.get("p", 40.0)),
                "K": float(sample.get("k", 40.0)),
                "pH": float(sample.get("ph", 6.5)),
                "Temperature": float(sample.get("temperature", 28.0)),
                "Rainfall": float(sample.get("rainfall", 1000.0)),
                "Humidity": float(sample.get("humidity", 70.0)),
                "Fertilizer": float(sample.get("fertilizer", 120.0)),
                "Pesticide": float(sample.get("pesticide", 1.0))
            }
            df_in = pd.DataFrame([row])
            X_trans = self.preprocessor.transform(df_in)
            probs = self.classifier.predict_proba(X_trans)[0]

            prob_dict = {cls_name: round(float(p), 4) for cls_name, p in zip(self.classifier.classes_, probs)}
            top_idx = int(np.argmax(probs))
            top_class = str(self.classifier.classes_[top_idx])
            confidence = round(float(probs[top_idx]), 4)
            return top_class, confidence, prob_dict
        except Exception as e:
            logger.error(f"Error in CropSuitabilityModel predict: {e}")
            return self._heuristic_fallback(sample)

    def _heuristic_fallback(self, sample: Dict[str, Any]) -> Tuple[str, float, Dict[str, float]]:
        """Deterministic agronomic fallback when ML weights are unavailable."""
        ph = float(sample.get("ph", 6.5))
        rain = float(sample.get("rainfall", 800.0))
        temp = float(sample.get("temperature", 25.0))

        if 5.8 <= ph <= 7.8 and 500.0 <= rain <= 2000.0 and 15.0 <= temp <= 35.0:
            return "Suitable", 0.85, {"Suitable": 0.85, "Moderately Suitable": 0.12, "High Risk": 0.03}
        elif 5.0 <= ph <= 8.5 and 300.0 <= rain <= 2500.0:
            return "Moderately Suitable", 0.70, {"Suitable": 0.20, "Moderately Suitable": 0.70, "High Risk": 0.10}
        else:
            return "High Risk", 0.80, {"Suitable": 0.05, "Moderately Suitable": 0.15, "High Risk": 0.80}
