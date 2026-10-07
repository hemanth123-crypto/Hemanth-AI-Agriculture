"""
app/evaluation/ml_evaluation.py
Extracts and reports machine learning model evaluation metrics.
Conforms to Section 25 of project specification.
"""

import json
from pathlib import Path
from typing import Dict, Any
from app.config.settings import settings
from app.utils.logging import get_logger

logger = get_logger("ml_evaluation")

class MLEvaluator:
    @staticmethod
    def get_latest_metrics() -> Dict[str, Any]:
        """Loads calculated ML evaluation metrics from report file."""
        report_file = settings.EVALUATION_DIR / "reports" / "ml_metrics.json"
        if report_file.exists():
            try:
                with open(report_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error reading ML metrics report: {e}")

        # If not yet generated, run training pipeline
        from app.ml.model_training import train_and_evaluate_models
        return train_and_evaluate_models()

ml_evaluator = MLEvaluator()
