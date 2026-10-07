"""
app/agents/retrieval_agent.py
Retrieval Agent: Coordinates hybrid search, metadata filter generation, and case gathering.
Conforms to Section 21 of project specification.
"""

from typing import List, Dict, Any, Optional
from app.rag.retriever import case_retriever
from app.models.schemas import InterpretedConditions, HistoricalCase
from app.utils.logging import get_logger

logger = get_logger("retrieval_agent")

class RetrievalAgent:
    def execute_retrieval(
        self,
        query: str,
        conditions: InterpretedConditions,
        top_k: int = 5
    ) -> List[HistoricalCase]:
        """
        Translates structured conditions into search filters and invokes hybrid retrieval.
        """
        filters: Dict[str, Any] = {}
        if conditions.crop:
            filters["crop"] = conditions.crop
        if conditions.state:
            filters["state"] = conditions.state
        if conditions.season:
            filters["season"] = conditions.season
        if conditions.ph is not None:
            filters["ph"] = conditions.ph
        if conditions.rainfall is not None:
            filters["rainfall"] = conditions.rainfall
        if conditions.temperature is not None:
            filters["temperature"] = conditions.temperature
        if conditions.humidity is not None:
            filters["humidity"] = conditions.humidity
        if conditions.n is not None:
            filters["n"] = conditions.n
        if conditions.p is not None:
            filters["p"] = conditions.p
        if conditions.k is not None:
            filters["k"] = conditions.k

        logger.info(f"Retrieval Agent executing hybrid retrieval with {len(filters)} active filters.")
        cases = case_retriever.retrieve(query=query, filters=filters, top_k=top_k)
        return cases

retrieval_agent = RetrievalAgent()
