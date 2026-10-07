"""
app/api/routes_search.py
Hybrid agricultural case search endpoint.
Combines semantic embeddings, lexical TF-IDF, and structured metadata filters.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException
from app.models.schemas import HistoricalCase
from app.services.retrieval_service import retrieval_service
from app.utils.logging import get_logger

logger = get_logger("routes_search")
router = APIRouter(prefix="/api", tags=["Retrieval & Search"])

class SearchRequest(BaseModel):
    query: str = Field(description="Natural-language search query")
    crop: Optional[str] = None
    state: Optional[str] = None
    season: Optional[str] = None
    ph: Optional[float] = None
    rainfall: Optional[float] = None
    temperature: Optional[float] = None
    top_k: int = Field(default=20, ge=1, le=500)

@router.get("/cases", response_model=List[HistoricalCase])
def get_all_historical_cases(
    crop: Optional[str] = None,
    state: Optional[str] = None,
    season: Optional[str] = None,
    limit: int = 1500
):
    """
    Returns historical agricultural cases directly from the indexed repository.
    """
    try:
        from app.rag.retriever import case_retriever
        if not case_retriever._is_ready:
            case_retriever.initialize()
            
        all_metadata = case_retriever.vector_store.metadata if case_retriever.vector_store else []
        cases = []
        for m in all_metadata:
            if crop and m.get("crop", "").lower() != crop.lower():
                continue
            if state and m.get("state", "").lower() != state.lower():
                continue
            if season and m.get("season", "").lower() != season.lower():
                continue
            cases.append(HistoricalCase(**m))
            if len(cases) >= limit:
                break
        return cases
    except Exception as e:
        logger.error(f"Error fetching historical cases: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=List[HistoricalCase])
def search_agricultural_cases(request: SearchRequest):
    """
    Executes hybrid retrieval across historical dataset records.
    Returns prioritized cases with relevance scores and match rationales.
    """
    try:
        filters = {}
        if request.crop:
            filters["crop"] = request.crop
        if request.state:
            filters["state"] = request.state
        if request.season:
            filters["season"] = request.season
        if request.ph is not None:
            filters["ph"] = request.ph
        if request.rainfall is not None:
            filters["rainfall"] = request.rainfall
        if request.temperature is not None:
            filters["temperature"] = request.temperature

        results = retrieval_service.search_cases(
            query=request.query,
            filters=filters,
            top_k=request.top_k
        )
        return results
    except Exception as e:
        logger.error(f"Error executing search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

