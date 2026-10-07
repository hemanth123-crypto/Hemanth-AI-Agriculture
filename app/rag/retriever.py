"""
app/rag/retriever.py
High-level agricultural case retriever.
Manages vector store and keyword index instances, and provides clean query endpoints.
"""

from typing import List, Dict, Any, Optional
from app.config.settings import settings
from app.utils.logging import get_logger
from app.rag.vector_store import FAISSVectorStore
from app.rag.keyword_search import keyword_engine
from app.rag.hybrid_search import HybridSearchEngine
from app.models.schemas import HistoricalCase

logger = get_logger("retriever")

class AgriculturalCaseRetriever:
    def __init__(self):
        self.vector_store = FAISSVectorStore(dim=settings.EMBEDDING_DIM)
        self.keyword_engine = keyword_engine
        self.hybrid_engine = None
        self._is_ready = False

    def initialize(self) -> bool:
        """Loads indexes from disk if available."""
        vs_loaded = self.vector_store.load()
        kw_loaded = self.keyword_engine.load()
        
        if vs_loaded and kw_loaded:
            self.hybrid_engine = HybridSearchEngine(
                vector_store=self.vector_store,
                keyword_engine=self.keyword_engine
            )
            self._is_ready = True
            logger.info("AgriculturalCaseRetriever initialized successfully from disk indexes.")
            return True
        else:
            logger.warning("Indexes not fully loaded on disk. Will initialize after index build.")
            self._is_ready = False
            return False

    def retrieve(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> List[HistoricalCase]:
        if not self._is_ready or self.hybrid_engine is None:
            # Try lazy init
            if not self.initialize():
                logger.warning("Retriever called before indexes built. Returning empty list.")
                return []

        return self.hybrid_engine.search(query=query, filters=filters, top_k=top_k)

case_retriever = AgriculturalCaseRetriever()
