"""
app/api/routes_query.py
Main advisory query endpoint.
Executes the multi-agent pipeline from query input to evidence-based advisory response.
"""

from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import AdvisoryRequest, AdvisoryResponse
from app.agents.orchestrator import orchestrator
from app.utils.logging import get_logger

logger = get_logger("routes_query")
router = APIRouter(prefix="/api", tags=["Advisory Query"])

@router.post("/query", response_model=AdvisoryResponse)
def execute_advisory_query(request: AdvisoryRequest):
    """
    Submits a natural-language agricultural question.
    Coordinates input guardrails, query classification, hybrid retrieval,
    ML suitability & yield predictions, risk analysis, and LLM-as-a-judge validation.
    """
    try:
        response = orchestrator.process_query(request)
        return response
    except Exception as e:
        logger.error(f"Error handling query request: {e}")
        raise HTTPException(status_code=500, detail=f"Advisory execution error: {str(e)}")
