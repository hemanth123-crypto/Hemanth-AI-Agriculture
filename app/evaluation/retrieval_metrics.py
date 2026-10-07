"""
app/evaluation/retrieval_metrics.py
Rigorous information retrieval evaluation metrics:
Precision@K, Recall@K, Mean Reciprocal Rank (MRR), and Hit Rate@K.
Evaluated directly against labeled test queries without fabricated numbers.
Conforms to Section 24 of project specification.
"""

from typing import List, Dict, Any, Set
import json
from pathlib import Path
from app.config.settings import settings
from app.rag.retriever import case_retriever
from app.agents.query_classifier import query_classifier
from app.models.schemas import HistoricalCase
from app.utils.logging import get_logger

logger = get_logger("retrieval_metrics")

class RetrievalEvaluator:
    @staticmethod
    def evaluate_retrieval(benchmark_file: Path = None, top_k: int = 5) -> Dict[str, Any]:
        """
        Runs labeled queries through the hybrid retriever and computes actual IR metrics:
        - Precision@1, Precision@3, Precision@5
        - Recall@5
        - MRR (Mean Reciprocal Rank)
        - Hit Rate@5
        """
        benchmark_file = benchmark_file or (settings.EVALUATION_DIR / "test_queries.json")
        if not benchmark_file.exists():
            return {
                "status": "NOT AVAILABLE",
                "message": f"Benchmark query file not found: {benchmark_file}"
            }

        with open(benchmark_file, "r", encoding="utf-8") as f:
            queries_data = json.load(f)

        total_queries = len(queries_data)
        if total_queries == 0:
            return {"status": "NOT AVAILABLE", "message": "Empty query dataset."}

        p1_list = []
        p3_list = []
        p5_list = []
        rec5_list = []
        rr_list = []
        hit5_list = []

        query_level_eval = []

        for q_item in queries_data:
            q_text = q_item["query"]
            relevant_crops = {c.lower() for c in q_item.get("relevant_crops", [])}
            expected_crop = q_item.get("expected_crop")
            if expected_crop:
                relevant_crops.add(expected_crop.lower())

            # Extract structured conditions
            classif = query_classifier.classify_and_extract(q_text)
            
            # Execute actual retrieval
            filters = {}
            if classif.interpreted_conditions.crop:
                filters["crop"] = classif.interpreted_conditions.crop
            if classif.interpreted_conditions.state:
                filters["state"] = classif.interpreted_conditions.state
            if classif.interpreted_conditions.season:
                filters["season"] = classif.interpreted_conditions.season

            retrieved = case_retriever.retrieve(query=q_text, filters=filters, top_k=5)
            
            # Evaluate relevance per position
            hits = []
            for rank, case in enumerate(retrieved, 1):
                is_rel = (case.crop.lower() in relevant_crops)
                hits.append(is_rel)

            # Precision@K
            p1 = 1.0 if (len(hits) > 0 and hits[0]) else 0.0
            p3 = sum(hits[:3]) / min(3, len(hits)) if hits else 0.0
            p5 = sum(hits[:5]) / min(5, len(hits)) if hits else 0.0

            # Recall@5: fraction of relevant crops represented
            retrieved_crop_set = {c.crop.lower() for c in retrieved}
            matched_rel_crops = len(relevant_crops.intersection(retrieved_crop_set))
            rec5 = matched_rel_crops / len(relevant_crops) if relevant_crops else 1.0

            # Reciprocal Rank (RR)
            rr = 0.0
            for rank, is_rel in enumerate(hits, 1):
                if is_rel:
                    rr = 1.0 / rank
                    break

            # Hit Rate@5
            hit5 = 1.0 if any(hits[:5]) else 0.0

            p1_list.append(p1)
            p3_list.append(p3)
            p5_list.append(p5)
            rec5_list.append(rec5)
            rr_list.append(rr)
            hit5_list.append(hit5)

            query_level_eval.append({
                "id": q_item.get("id"),
                "query": q_text,
                "retrieved_count": len(retrieved),
                "precision_at_5": round(p5, 3),
                "reciprocal_rank": round(rr, 3),
                "hit": bool(hit5)
            })

        metrics = {
            "total_benchmark_queries": total_queries,
            "precision_at_1": round(sum(p1_list) / total_queries, 4),
            "precision_at_3": round(sum(p3_list) / total_queries, 4),
            "precision_at_5": round(sum(p5_list) / total_queries, 4),
            "recall_at_5": round(sum(rec5_list) / total_queries, 4),
            "mrr": round(sum(rr_list) / total_queries, 4),
            "hit_rate_at_5": round(sum(hit5_list) / total_queries, 4),
            "details": query_level_eval[:5]
        }
        logger.info(f"Retrieval Evaluation finished: P@5={metrics['precision_at_5']}, MRR={metrics['mrr']}, HitRate@5={metrics['hit_rate_at_5']}")
        return metrics

retrieval_evaluator = RetrievalEvaluator()
