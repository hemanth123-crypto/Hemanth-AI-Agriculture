"""
app/api/routes_evaluation.py
System evaluation endpoints returning RAG, retrieval, ML, and guardrail metrics.
"""

from typing import Dict, Any
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.config.settings import settings
from app.evaluation.end_to_end_evaluation import end_to_end_evaluator
from app.evaluation.report_generator import report_generator
from app.utils.logging import get_logger

logger = get_logger("routes_evaluation")
router = APIRouter(prefix="/api", tags=["Evaluation"])

@router.post("/evaluate")
def run_evaluation() -> Dict[str, Any]:
    """
    Executes live end-to-end evaluation across benchmark queries
    and regenerates the evaluation report files.
    """
    try:
        data = end_to_end_evaluator.run_full_evaluation()
        report_generator.save_reports(data)
        return data
    except Exception as e:
        logger.error(f"Error running evaluation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/evaluation/latest")
def get_latest_evaluation() -> Dict[str, Any]:
    """
    Retrieves the latest persisted evaluation metrics report.
    """
    json_path = settings.EVALUATION_DIR / "reports" / "evaluation_report.json"
    if json_path.exists():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading evaluation report: {e}")

    # If report does not exist yet, trigger evaluation
    return run_evaluation()
