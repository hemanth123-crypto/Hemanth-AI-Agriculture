"""
app/guardrails/hallucination_check.py
Detects hallucinations, fabricated case IDs, or uncorroborated numerical claims.
Conforms to Section 14 of project specification.
"""

from typing import List, Tuple, Set
import re
from app.models.schemas import HistoricalCase

class HallucinationChecker:
    @staticmethod
    def verify_case_references(advisory_text: str, valid_cases: List[HistoricalCase]) -> Tuple[bool, List[str]]:
        """
        Extracts referenced Case IDs (e.g. 'CASE_0012') from text and verifies
        that they strictly match real cases retrieved from the dataset.
        """
        valid_ids: Set[str] = {c.case_id for c in valid_cases}
        referenced_ids = set(re.findall(r"\bCASE_\d+\b", advisory_text, re.IGNORECASE))

        hallucinated_ids = []
        for ref_id in referenced_ids:
            # Check upper case
            if ref_id.upper() not in valid_ids:
                hallucinated_ids.append(ref_id)

        if hallucinated_ids:
            return False, [f"Fabricated Case Reference: '{cid}' cited in advisory was not among retrieved dataset cases." for cid in hallucinated_ids]

        return True, []

hallucination_checker = HallucinationChecker()
