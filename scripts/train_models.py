"""
scripts/train_models.py
CLI script to train ML models (Crop Suitability & Yield Prediction) and generate evaluation report.
"""

import sys
from pathlib import Path

# Add root directory to python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.ml.model_training import train_and_evaluate_models
from app.ml.model_loader import model_manager

def main():
    print("=" * 60)
    print("AI Agriculture Advisory - Machine Learning Training Pipeline")
    print("=" * 60)
    try:
        report = train_and_evaluate_models()
        model_manager.reload()
        print("[SUCCESS] Models trained, evaluated, and saved successfully!")
        print(f"Suitability Accuracy: {report['suitability_classifier']['accuracy']:.4f}")
        print(f"Yield Regressor R^2:  {report['yield_regressor']['r2_score']:.4f}")
        print(f"Yield Regressor MAE:  {report['yield_regressor']['mae']:.4f}")
        print("=" * 60)
    except Exception as e:
        print(f"[ERROR] Model training failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
