"""
app/agents/validation_agent.py
Validation Agent: Inspects candidate recommendations and advisory draft against retrieved evidence.
Conforms to Section 21 of project specification.
"""

from typing import List, Tuple
from app.models.schemas import CropRecommendationItem, HistoricalCase
from app.guardrails.output_validation import output_guardrail
from app.guardrails.safety import safety_guardrail
from app.guardrails.hallucination_check import hallucination_checker
from app.utils.logging import get_logger

logger = get_logger("validation_agent")

class ValidationAgent:
    def validate(
        self,
        recommendations: List[CropRecommendationItem],
        retrieved_cases: List[HistoricalCase],
        raw_advisory_text: str = ""
    ) -> Tuple[bool, List[str]]:
        """
        Validates:
        1. Every recommended crop has at least 1 supporting retrieved historical case.
        2. No prohibited guarantee language is present in text.
        3. All case citations are genuine dataset case IDs.
        """
        violations = []

        # 1. Evidence Grounding Check
        is_grounded, ground_violations = output_guardrail.validate_recommendation_grounding(
            recommendations, retrieved_cases
        )
        if not is_grounded:
            violations.extend(ground_violations)

        # 2. Safety / Guarantee Check
        if raw_advisory_text:
            is_safe, safe_msg = safety_guardrail.verify_no_guarantees(raw_advisory_text)
            if not is_safe:
                violations.append(safe_msg)

        # 3. Hallucination Check
        if raw_advisory_text:
            is_factual, fact_violations = hallucination_checker.verify_case_references(
                raw_advisory_text, retrieved_cases
            )
            if not is_factual:
                violations.extend(fact_violations)

        passed = len(violations) == 0
        if not passed:
            logger.warning(f"Validation Agent flagged {len(violations)} issues: {violations}")
        else:
            logger.info("Validation Agent passed: all recommendations rigorously grounded.")

        return passed, violations

validation_agent = ValidationAgent()
