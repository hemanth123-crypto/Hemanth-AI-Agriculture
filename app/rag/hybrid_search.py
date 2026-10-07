"""
app/rag/hybrid_search.py
Hybrid retrieval engine unifying dense semantic search, sparse lexical TF-IDF,
and structured metadata filtering with configurable weights.
Conforms to Section 11 of project specification.

WHY HYBRID RETRIEVAL IS USED:
Dense semantic search excels at understanding natural language queries, conceptual synonyms,
and fuzzy environmental contexts (e.g. "heavy monsoon", "acidic soil").
However, dense search can occasionally overlook exact entity constraints (e.g. specific state "Punjab"
or exact season "Kharif"). Lexical search (TF-IDF/BM25) provides precise token matching for technical terms,
crop cultivars, and locations. Structured metadata filtering verifies strict biological boundaries (pH, rainfall).
Combining them via:
    Score = (alpha * semantic) + (beta * keyword) + (gamma * metadata)
ensures that retrieved cases are both linguistically relevant and agronomically grounded.
"""

from typing import List, Dict, Any, Tuple
from app.config.settings import settings
from app.utils.logging import get_logger
from app.utils.helpers import calculate_hybrid_score, min_max_normalize
from app.rag.embeddings import embedding_service
from app.rag.vector_store import FAISSVectorStore
from app.rag.keyword_search import KeywordSearchEngine
from app.rag.metadata_filter import MetadataFilter
from app.rag.reranker import CaseReranker
from app.models.schemas import HistoricalCase

logger = get_logger("hybrid_search")

class HybridSearchEngine:
    def __init__(
        self,
        vector_store: FAISSVectorStore,
        keyword_engine: KeywordSearchEngine,
        alpha: float = None,
        beta: float = None,
        gamma: float = None
    ):
        self.vector_store = vector_store
        self.keyword_engine = keyword_engine
        self.alpha = alpha if alpha is not None else settings.ALPHA_SEMANTIC
        self.beta = beta if beta is not None else settings.BETA_KEYWORD
        self.gamma = gamma if gamma is not None else settings.GAMMA_METADATA

    def search(
        self,
        query: str,
        filters: Dict[str, Any] = None,
        top_k: int = 5,
        candidate_pool_size: int = 25
    ) -> List[HistoricalCase]:
        """
        Executes hybrid retrieval:
        1. Encodes query into dense vector -> FAISS search
        2. Queries lexical TF-IDF index
        3. Merges candidate cases from both sources
        4. Calculates metadata alignment score
        5. Computes combined hybrid score
        6. Re-ranks candidates with environmental similarity and returns top_k HistoricalCase objects
        """
        filters = filters or {}
        candidate_pool_size = max(candidate_pool_size, top_k * 3)

        # 1. Semantic Search
        q_vec = embedding_service.encode(query)
        semantic_results = self.vector_store.search(q_vec, top_k=candidate_pool_size)

        # 2. Keyword Search
        keyword_results = self.keyword_engine.search(query, top_k=candidate_pool_size)

        # 3. Merge candidate pool by case_id
        candidates_by_id: Dict[str, Dict[str, Any]] = {}

        for meta, sem_score, text in semantic_results:
            cid = meta["case_id"]
            candidates_by_id[cid] = {
                "metadata": meta,
                "text": text,
                "semantic_score": sem_score,
                "keyword_score": 0.0,
                "metadata_score": 0.0
            }

        for meta, kw_score, text in keyword_results:
            cid = meta["case_id"]
            if cid in candidates_by_id:
                candidates_by_id[cid]["keyword_score"] = kw_score
            else:
                candidates_by_id[cid] = {
                    "metadata": meta,
                    "text": text,
                    "semantic_score": 0.0,
                    "keyword_score": kw_score,
                    "metadata_score": 0.0
                }

        # If candidates are still empty (e.g. cold start with empty query), draw top cases from metadata
        if not candidates_by_id and self.vector_store.metadata:
            for meta in self.vector_store.metadata[:candidate_pool_size]:
                cid = meta["case_id"]
                candidates_by_id[cid] = {
                    "metadata": meta,
                    "text": "",
                    "semantic_score": 0.5,
                    "keyword_score": 0.5,
                    "metadata_score": 1.0
                }

        # 4. Evaluate metadata scores and combine
        candidate_list = list(candidates_by_id.values())
        for item in candidate_list:
            meta = item["metadata"]
            meta_score = MetadataFilter.compute_match_score(meta, filters)
            item["metadata_score"] = meta_score

            hybrid = calculate_hybrid_score(
                semantic_score=item["semantic_score"],
                keyword_score=item["keyword_score"],
                metadata_score=item["metadata_score"],
                alpha=self.alpha,
                beta=self.beta,
                gamma=self.gamma
            )
            item["hybrid_score"] = hybrid

        # 5. Re-ranking with domain-specific environmental proximity and yield weights
        reranked_cases = CaseReranker.rerank(candidate_list, query_conditions=filters, top_k=top_k)
        logger.info(f"Hybrid retrieval completed: returned {len(reranked_cases)} cases for query='{query[:40]}...'")
        return reranked_cases
