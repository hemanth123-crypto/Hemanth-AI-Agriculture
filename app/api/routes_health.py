"""
app/api/routes_health.py
System health check and metadata options endpoints for UI dropdowns.
"""

from typing import List, Dict, Any
from fastapi import APIRouter
import pandas as pd
from app.config.settings import settings
from app.rag.retriever import case_retriever
from app.ml.model_loader import model_manager

router = APIRouter(tags=["Health & Metadata"])

@router.get("/health")
@router.get("/api/health")
def health_check() -> Dict[str, Any]:
    """
    Returns system health status, index readiness, and model load states.
    """
    return {
        "status": "HEALTHY",
        "service": "AI-Powered Agriculture Crop Advisory Assistant",
        "vector_store_ready": case_retriever._is_ready,
        "indexed_cases_count": len(case_retriever.vector_store.metadata) if case_retriever.vector_store else 0,
        "suitability_model_loaded": model_manager.suitability_model is not None and model_manager.suitability_model.is_trained,
        "yield_model_loaded": model_manager.yield_model is not None and model_manager.yield_model.is_trained,
        "embedding_provider": settings.EMBEDDING_PROVIDER,
        "openai_configured": settings.has_openai()
    }

@router.get("/api/crops")
def get_available_crops() -> List[str]:
    """Returns list of distinct crops present in the dataset."""
    if model_manager.metadata and "crops" in model_manager.metadata:
        return model_manager.metadata["crops"]
    return [
        "Barley", "Chickpea", "Cotton", "Groundnut", "Jute", "Maize",
        "Millets", "Mustard", "Rice", "Soybean", "Sugarcane", "Wheat"
    ]

@router.get("/api/states")
def get_available_states() -> List[str]:
    """Returns list of distinct states in the dataset."""
    if model_manager.metadata and "states" in model_manager.metadata:
        return model_manager.metadata["states"]
    return [
        "Andhra Pradesh", "Assam", "Bihar", "Gujarat", "Haryana",
        "Karnataka", "Madhya Pradesh", "Maharashtra", "Odisha",
        "Punjab", "Rajasthan", "Tamil Nadu", "Uttar Pradesh", "West Bengal"
    ]

@router.get("/api/seasons")
def get_available_seasons() -> List[str]:
    """Returns list of distinct seasons in the dataset."""
    if model_manager.metadata and "seasons" in model_manager.metadata:
        return model_manager.metadata["seasons"]
    return ["Kharif", "Rabi", "Summer", "Whole Year"]
