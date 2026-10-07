"""
app/api/routes_feedback.py
User feedback collection and continuous improvement analytics endpoints.
Conforms to Section 30 of project specification.
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from app.models.schemas import FeedbackRequest, FeedbackResponse
from app.feedback.feedback_store import feedback_store
from app.feedback.feedback_processor import feedback_processor
from app.utils.logging import get_logger

logger = get_logger("routes_feedback")
router = APIRouter(prefix="/api", tags=["Feedback"])

@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(request: FeedbackRequest):
    """
    Submits user rating (1-5), thumbs up/down, and comments on an advisory response.
    Persists feedback for offline audit and continuous improvement.
    """
    try:
        fb_id = feedback_store.add_feedback(
            query=request.query,
            recommendation=request.recommendation or "",
            retrieved_cases=request.retrieved_cases or [],
            rating=request.rating,
            thumbs=request.thumbs or "up",
            comments=request.comments or ""
        )
        return FeedbackResponse(
            status="SUCCESS",
            message="Feedback recorded successfully. Thank you for helping improve the advisory system.",
            feedback_id=fb_id
        )
    except Exception as e:
        logger.error(f"Error recording feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feedback/summary")
def get_feedback_analytics() -> Dict[str, Any]:
    """
    Returns aggregated feedback metrics and identified failure patterns.
    """
    try:
        return feedback_processor.analyze_feedback()
    except Exception as e:
        logger.error(f"Error calculating feedback summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
