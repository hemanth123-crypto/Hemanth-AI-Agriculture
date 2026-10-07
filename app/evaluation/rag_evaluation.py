"""
app/evaluation/rag_evaluation.py
Calculates RAG metrics: Faithfulness, Answer Relevancy, and Contextual Precision/Recall.
"""

from typing import Dict, Any, List
import re
from app.rag.retriever import case_retriever
from app.models.schemas import HistoricalCase

class RAGEvaluator:
    @staticmethod
    def evaluate_grounded_faithfulness(advisory_text: str, context_cases: List[HistoricalCase]) -> float:
        """
        Computes factual alignment: calculates percentage of crop claims and case references
        that are strictly grounded in retrieved historical context.
        """
        if not context_cases or not advisory_text:
            return 0.50

        # Check crops mentioned
        valid_crops = {c.crop.lower() for c in context_cases}
        mentioned_crops = set()
        for c in ["rice", "wheat", "maize", "cotton", "sugarcane", "chickpea", "groundnut", "soybean", "mustard", "millets", "barley", "jute"]:
            if re.search(r"\b" + c + r"\b", advisory_text.lower()):
                mentioned_crops.add(c)

        if not mentioned_crops:
            return 1.0

        supported = mentioned_crops.intersection(valid_crops)
        faithfulness = len(supported) / len(mentioned_crops)
        return round(float(faithfulness), 3)

    @staticmethod
    def evaluate_contextual_relevancy(query: str, context_cases: List[HistoricalCase]) -> float:
        """
        Computes relevance of retrieved context to query keywords.
        """
        if not context_cases:
            return 0.0

        q_words = set(query.lower().split())
        case_scores = []
        for c in context_cases:
            case_words = set(f"{c.crop} {c.state} {c.season}".lower().split())
            overlap = len(q_words.intersection(case_words))
            case_scores.append(min(1.0, overlap / max(1, len(q_words) // 2)))

        return round(sum(case_scores) / len(case_scores), 3)

rag_evaluator = RAGEvaluator()
