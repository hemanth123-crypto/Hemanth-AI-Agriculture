"""
app/guardrails/scope_guardrail.py
Enforces domain boundary constraints so the assistant remains strictly focused
on agricultural, agronomic, soil, crop, and weather advisory.
Conforms to Section 14 of project specification.
"""

from typing import Tuple, Optional
import re

AGRICULTURAL_KEYWORDS = [
    "crop", "yield", "soil", "kharif", "rabi", "summer", "season", "farm", "farming",
    "fertilizer", "pesticide", "ph", "rainfall", "temperature", "humidity", "rain",
    "nitrogen", "phosphorus", "potassium", "npk", "rice", "wheat", "maize", "cotton",
    "sugarcane", "chickpea", "groundnut", "soybean", "mustard", "millets", "barley",
    "jute", "potato", "andhra", "punjab", "haryana", "maharashtra", "karnataka",
    "tamil", "bengal", "gujarat", "bihar", "rajasthan", "agriculture", "harvest",
    "cultivation", "irrigation", "hectare", "tonnes", "plant", "sow", "seed"
]

OUT_OF_SCOPE_PATTERNS = [
    r"\b(cryptocurrency|bitcoin|ethereum|stock\s+market|forex)\b",
    r"\b(write\s+a\s+poem|write\s+a\s+story|joke|movie|song)\b",
    r"\b(write\s+python|javascript|java|c\+\+|code\s+for|programming)\b",
    r"\b(solve\s+my|calculus|physics\s+homework|math\s+equation)\b",
    r"\b(who\s+won|president|prime\s+minister|celebrity|actor|sports|cricket|football)\b",
    r"\b(what('s|\s+is)?\s+(the\s+)?(time|date|day|clock|year\s+now))\b",
    r"\b(tell\s+me\s+the\s+time)\b"
]

class ScopeGuardrail:
    @staticmethod
    def check_scope(query: str) -> Tuple[bool, Optional[str]]:
        """
        Determines whether a query is within the agricultural domain scope.
        """
        if not query:
            return False, "Query is empty."

        lower_q = query.lower().strip()

        # Allow simple greetings
        if lower_q in ["hello", "hi", "help", "hey"]:
            return True, None

        # Check explicit out of scope triggers
        for p in OUT_OF_SCOPE_PATTERNS:
            if re.search(p, lower_q):
                return False, "Domain Boundary: This system is exclusively dedicated to agricultural advisory, crop suitability, soil, and yield analysis. Please ask an agriculture-related question."

        # Check if at least one agricultural term or environmental token is present
        has_agri_context = any(term in lower_q for term in AGRICULTURAL_KEYWORDS)
        
        # If no agricultural context found
        if not has_agri_context:
            return False, "Domain Boundary: Query does not appear to be related to agriculture, soil conditions, weather, or crop management. Please ask questions about crops, soil nutrients, rainfall, or farming conditions."

        return True, None

scope_guardrail = ScopeGuardrail()
