"""
app/agents/crop_recommendation_agent.py
Crop Recommendation Agent: derives evidence-based crop candidates and alternatives.
Conforms to Sections 16, 17, and 21 of project specification.
"""

from typing import List, Dict, Any, Optional
from collections import defaultdict
from app.models.schemas import CropRecommendationItem, HistoricalCase, InterpretedConditions
from app.ml.model_loader import model_manager
from app.utils.logging import get_logger

logger = get_logger("crop_recommendation_agent")

class CropRecommendationAgent:
    def recommend(
        self,
        conditions: InterpretedConditions,
        retrieved_cases: List[HistoricalCase],
        is_alternative_request: bool = False
    ) -> List[CropRecommendationItem]:
        """
        Synthesizes candidate recommendations strictly grounded in retrieved historical cases.
        """
        if not retrieved_cases:
            return []

        # Group cases by crop
        crop_groups: Dict[str, List[HistoricalCase]] = defaultdict(list)
        for case in retrieved_cases:
            crop_groups[case.crop].append(case)

        # If alternative request, exclude the current crop if specified
        current_crop = conditions.crop.lower() if (conditions.crop and is_alternative_request) else None

        recommendations: List[CropRecommendationItem] = []

        for crop_name, cases in crop_groups.items():
            if current_crop and crop_name.lower() == current_crop:
                continue

            num_cases = len(cases)
            yields = [c.yield_val for c in cases]
            avg_yield = round(sum(yields) / num_cases, 2)
            avg_relevance = sum(c.relevance_score for c in cases) / num_cases

            # Use ML Suitability classifier for candidate validation
            sample_features = {
                "crop": crop_name,
                "season": conditions.season or cases[0].season,
                "state": conditions.state or cases[0].state,
                "n": conditions.n or cases[0].n,
                "p": conditions.p or cases[0].p,
                "k": conditions.k or cases[0].k,
                "ph": conditions.ph or cases[0].ph,
                "temperature": conditions.temperature or cases[0].temperature,
                "rainfall": conditions.rainfall or cases[0].rainfall,
                "humidity": conditions.humidity or cases[0].humidity,
                "fertilizer": conditions.fertilizer or cases[0].fertilizer,
                "pesticide": conditions.pesticide or cases[0].pesticide
            }

            suitability_label, ml_conf, probs = model_manager.suitability_model.predict(sample_features)

            # Combined suitability score [0.0, 1.0]
            score = round((0.60 * avg_relevance) + (0.40 * ml_conf), 3)

            # Derive risk label
            if suitability_label == "Suitable" and score >= 0.70:
                risk = "Low"
            elif suitability_label == "High Risk" or score < 0.50:
                risk = "High"
            else:
                risk = "Moderate"

            case_ids = [c.case_id for c in cases]
            matching_conditions = {
                "season": cases[0].season,
                "state": cases[0].state,
                "avg_historical_rainfall": round(sum(c.rainfall for c in cases) / num_cases, 1),
                "avg_historical_ph": round(sum(c.ph for c in cases) / num_cases, 2)
            }

            explanation = (
                f"{crop_name} is supported by {num_cases} historical cases in {matching_conditions['state']} "
                f"during {matching_conditions['season']} season. Historical yields averaged {avg_yield} t/ha "
                f"under rainfall averaging {matching_conditions['avg_historical_rainfall']} mm and pH {matching_conditions['avg_historical_ph']}."
            )

            limitations = (
                f"Yield outcomes for {crop_name} depend on adequate soil moisture during flowering and "
                "proper adherence to recommended fertilizer scheduling."
            )

            rec_item = CropRecommendationItem(
                crop=crop_name,
                suitability_score=score,
                suitability_label=suitability_label,
                risk=risk,
                historical_yield_avg=avg_yield,
                number_of_similar_cases=num_cases,
                matching_conditions=matching_conditions,
                explanation=explanation,
                confidence=round(ml_conf, 2),
                supporting_cases=case_ids,
                limitations=limitations
            )
            recommendations.append(rec_item)

        # Sort recommendations descending by suitability score
        recommendations.sort(key=lambda r: r.suitability_score, reverse=True)
        return recommendations

crop_recommendation_agent = CropRecommendationAgent()
