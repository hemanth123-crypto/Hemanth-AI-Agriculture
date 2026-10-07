"""
app/guardrails/output_validation.py
Validates agent advisory recommendations against retrieved historical cases.
Conforms to Section 14 of project specification.
"""

from typing import List, Dict, Any, Tuple
from app.models.schemas import CropRecommendationItem, HistoricalCase

class OutputValidationGuardrail:
    @staticmethod
    def validate_recommendation_grounding(
        recommendations: List[CropRecommendationItem],
        retrieved_cases: List[HistoricalCase]
    ) -> Tuple[bool, List[str]]:
        """
        Verifies that every recommended crop is actually represented in retrieved historical cases
        or dataset crop profiles, ensuring no fictitious crops or fabricated records are recommended.
        """
        if not recommendations:
            return True, ["No recommendations generated."]

        retrieved_crops = {c.crop.lower() for c in retrieved_cases}
        violations = []

        for rec in recommendations:
            crop_name = rec.crop.lower()
            if crop_name not in retrieved_crops:
                violations.append(
                    f"Ungrounded Recommendation: Crop '{rec.crop}' was recommended but has 0 supporting cases in top retrieved historical records."
                )

        is_valid = len(violations) == 0
        return is_valid, violations

output_guardrail = OutputValidationGuardrail()
