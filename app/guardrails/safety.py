"""
app/guardrails/safety.py
Enforces probabilistic, evidence-based advisory language and prohibits false guarantees.
Conforms to Section 14 of project specification.
"""

import re
from typing import Tuple

GUARANTEE_PATTERNS = [
    r"\b(will\s+definitely\s+(produce|yield|succeed))\b",
    r"\b(100%\s+guaranteed?\s+(success|harvest|yield))\b",
    r"\b(zero\s+risk\s+farming)\b",
    r"\b(promised?\s+profits?)\b",
    r"\b(foolproof\s+harvest)\b"
]

SAFE_DISCLAIMER = (
    "Recommendations and yield estimates are grounded in historical observational data and "
    "statistical machine learning models. Agricultural outcomes depend on unpredictable factors "
    "such as micro-climates, pest outbreaks, and groundwater availability. They do not guarantee "
    "future farming results."
)

class SafetyGuardrail:
    @staticmethod
    def sanitize_language(text: str) -> str:
        """
        Replaces absolute guarantees with calibrated historical phrasing.
        """
        sanitized = text
        sanitized = re.sub(r"\bwill definitely produce\b", "has historically shown potential to produce", sanitized, flags=re.I)
        sanitized = re.sub(r"\bguarantees?\s+success\b", "is strongly supported by historical records", sanitized, flags=re.I)
        sanitized = re.sub(r"\bguaranteed?\s+yield\b", "historically estimated yield", sanitized, flags=re.I)
        sanitized = re.sub(r"\bzero\s+risk\b", "controlled historical risk", sanitized, flags=re.I)
        return sanitized

    @staticmethod
    def verify_no_guarantees(text: str) -> Tuple[bool, str]:
        """
        Checks text for prohibited guarantee claims.
        """
        for p in GUARANTEE_PATTERNS:
            if re.search(p, text, re.IGNORECASE):
                return False, f"Safety Violation: Prohibited guarantee detected ('{p}'). Agricultural success cannot be unconditionally promised."
        return True, "Safe"

safety_guardrail = SafetyGuardrail()
