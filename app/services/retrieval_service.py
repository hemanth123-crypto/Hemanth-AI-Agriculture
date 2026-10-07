"""
app/services/retrieval_service.py
Service handling agricultural case search and metadata queries.
"""

from typing import List, Dict, Any, Optional
from app.rag.retriever import case_retriever
from app.models.schemas import HistoricalCase

class RetrievalService:
    def search_cases(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> List[HistoricalCase]:
        return case_retriever.retrieve(query=query, filters=filters, top_k=top_k)

retrieval_service = RetrievalService()
