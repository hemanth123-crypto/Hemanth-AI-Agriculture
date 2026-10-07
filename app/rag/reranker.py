"""
app/rag/reranker.py
Re-ranking and case prioritization module.
Calculates multidimensional relevance incorporating semantic, lexical, environmental,
and yield signals, and provides transparent explanations for why each case was retrieved.
Conforms to Section 15 of project specification.
"""

from typing import List, Dict, Any, Tuple
import math
from app.models.schemas import HistoricalCase

class CaseReranker:
    @staticmethod
    def calculate_environmental_similarity(case_meta: Dict[str, Any], query_conditions: Dict[str, Any]) -> float:
        """Computes continuous Euclidean similarity across normalized environmental variables."""
        diff_sq = 0.0
        dims = 0

        # Soil pH (scale ~ 4-9)
        if query_conditions.get("ph") is not None:
            q_ph = float(query_conditions["ph"])
            c_ph = float(case_meta.get("ph", 7.0))
            diff_sq += ((c_ph - q_ph) / 2.0) ** 2
            dims += 1

        # Temperature (scale ~ 10-40)
        if query_conditions.get("temperature") is not None:
            q_temp = float(query_conditions["temperature"])
            c_temp = float(case_meta.get("temperature", 25.0))
            diff_sq += ((c_temp - q_temp) / 10.0) ** 2
            dims += 1

        # Rainfall (scale ~ 300-2500)
        if query_conditions.get("rainfall") is not None:
            q_rain = float(query_conditions["rainfall"])
            c_rain = float(case_meta.get("rainfall", 800.0))
            diff_sq += ((c_rain - q_rain) / 500.0) ** 2
            dims += 1

        # NPK (scale ~ 20-150)
        for nutrient in ["n", "p", "k"]:
            if query_conditions.get(nutrient) is not None:
                q_val = float(query_conditions[nutrient])
                c_val = float(case_meta.get(nutrient, 50.0))
                diff_sq += ((c_val - q_val) / 40.0) ** 2
                dims += 1

        if dims == 0:
            return 1.0

        dist = math.sqrt(diff_sq / dims)
        sim = 1.0 / (1.0 + dist)
        return float(sim)

    @staticmethod
    def generate_match_reasons(case_meta: Dict[str, Any], query_conditions: Dict[str, Any], score: float) -> List[str]:
        """Generates clear, natural language reasons for why this case was selected."""
        reasons = []

        if query_conditions.get("crop") and str(case_meta.get("crop", "")).lower() == str(query_conditions["crop"]).lower():
            reasons.append(f"Direct crop match: {case_meta.get('crop')}")

        if query_conditions.get("state") and str(case_meta.get("state", "")).lower() == str(query_conditions["state"]).lower():
            reasons.append(f"Region match: {case_meta.get('state')}")

        if query_conditions.get("season") and str(case_meta.get("season", "")).lower() == str(query_conditions["season"]).lower():
            reasons.append(f"Identical cultivation season: {case_meta.get('season')}")

        if query_conditions.get("ph") is not None:
            diff = abs(float(case_meta.get("ph", 7.0)) - float(query_conditions["ph"]))
            if diff <= 0.4:
                reasons.append(f"Close soil pH: {case_meta.get('ph')} (target: {query_conditions['ph']})")

        if query_conditions.get("rainfall") is not None:
            diff = abs(float(case_meta.get("rainfall", 800.0)) - float(query_conditions["rainfall"]))
            if diff <= 150.0:
                reasons.append(f"Comparable rainfall: {case_meta.get('rainfall')} mm")

        # Yield outcome
        yield_val = float(case_meta.get("yield_val", 0.0))
        if yield_val > 3.0:
            reasons.append(f"Demonstrated productive yield ({yield_val:.2f} t/ha)")

        if not reasons:
            reasons.append("High overall semantic and environmental similarity to query profile")

        return reasons

    @staticmethod
    def rerank(
        candidate_cases: List[Dict[str, Any]],
        query_conditions: Dict[str, Any],
        top_k: int = 5
    ) -> List[HistoricalCase]:
        """
        Reranks candidates incorporating base hybrid score + environmental proximity + yield bonus.
        """
        scored_cases = []

        for item in candidate_cases:
            meta = item["metadata"]
            sem_score = item.get("semantic_score", 0.0)
            kw_score = item.get("keyword_score", 0.0)
            meta_score = item.get("metadata_score", 0.0)
            base_hybrid = item.get("hybrid_score", 0.0)

            # Environmental similarity
            env_sim = CaseReranker.calculate_environmental_similarity(meta, query_conditions)

            # High yield bonus
            yield_val = float(meta.get("yield_val", 1.0))
            yield_bonus = min(0.15, yield_val / 50.0)

            # Recency bonus (more recent records slightly preferred)
            year = int(meta.get("year", 2015))
            recency_bonus = max(0.0, (year - 2012) * 0.005)

            # Final Reranked Score
            final_score = (0.50 * base_hybrid) + (0.35 * env_sim) + (0.10 * yield_bonus) + (0.05 * recency_bonus)
            final_score = float(max(0.0, min(1.0, final_score)))

            reasons = CaseReranker.generate_match_reasons(meta, query_conditions, final_score)

            hist_case = HistoricalCase(
                case_id=meta.get("case_id", "CASE_UNKNOWN"),
                crop=meta.get("crop", "Unknown"),
                year=int(meta.get("year", 2020)),
                season=meta.get("season", "Unknown"),
                state=meta.get("state", "Unknown"),
                area=float(meta.get("area", 0.0)),
                production=float(meta.get("production", 0.0)),
                yield_val=float(meta.get("yield_val", 0.0)),
                fertilizer=float(meta.get("fertilizer", 0.0)),
                pesticide=float(meta.get("pesticide", 0.0)),
                n=float(meta.get("n", 0.0)),
                p=float(meta.get("p", 0.0)),
                k=float(meta.get("k", 0.0)),
                ph=float(meta.get("ph", 7.0)),
                temperature=float(meta.get("temperature", 25.0)),
                rainfall=float(meta.get("rainfall", 800.0)),
                humidity=float(meta.get("humidity", 65.0)),
                relevance_score=round(final_score, 4),
                semantic_score=round(sem_score, 4),
                keyword_score=round(kw_score, 4),
                metadata_score=round(meta_score, 4),
                match_reasons=reasons
            )
            scored_cases.append((hist_case, final_score))

        # Sort descending by final score
        scored_cases.sort(key=lambda x: x[1], reverse=True)
        return [c[0] for c in scored_cases[:top_k]]
