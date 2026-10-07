"""
app/agents/query_classifier.py
Query Understanding Agent: performs intent classification and structured parameter extraction.
Uses rule-based extraction with optional OpenAI-compatible LLM completion.
Conforms to Section 13 of project specification.
"""

import re
from typing import Dict, Any, Optional
from app.config.settings import settings
from app.utils.logging import get_logger
from app.models.schemas import (
    QueryIntent, InterpretedConditions, QueryClassificationResult
)

logger = get_logger("query_classifier")

# Common agricultural terms for entity parsing
KNOWN_CROPS = [
    "Rice", "Wheat", "Maize", "Cotton", "Sugarcane", "Chickpea", "Groundnut",
    "Soybean", "Mustard", "Millets", "Barley", "Jute", "Potato", "Pigeonpea", "Sorghum"
]

KNOWN_STATES = [
    "Andhra Pradesh", "West Bengal", "Punjab", "Uttar Pradesh", "Odisha", "Tamil Nadu",
    "Bihar", "Assam", "Haryana", "Madhya Pradesh", "Rajasthan", "Gujarat", "Karnataka",
    "Maharashtra", "Telangana", "Kerala"
]

KNOWN_SEASONS = ["Kharif", "Rabi", "Summer", "Winter", "Autumn", "Whole Year"]

class QueryClassificationAgent:
    def __init__(self):
        self.crops_map = {c.lower(): c for c in KNOWN_CROPS}
        self.states_map = {s.lower(): s for s in KNOWN_STATES}
        self.seasons_map = {s.lower(): s for s in KNOWN_SEASONS}

    def classify_and_extract(self, query: str, user_overrides: Optional[Dict[str, Any]] = None) -> QueryClassificationResult:
        """
        Extracts structured intent and agronomic conditions from natural language query.
        Applies user explicit overrides if provided via form/API.
        """
        user_overrides = user_overrides or {}
        q_lower = query.lower()

        # 1. Intent Detection Heuristics
        intent = QueryIntent.CROP_RECOMMENDATION  # default
        reasoning = "Classified as general crop recommendation."

        if any(term in q_lower for term in ["similar", "historical cases", "most similar", "cases like mine"]):
            intent = QueryIntent.CASE_SIMILARITY
            reasoning = "User is requesting historically similar farming records matching given conditions."
        elif any(term in q_lower for term in ["alternative", "substitute", "replace", "other crops"]):
            intent = QueryIntent.ALTERNATIVE_CROP
            reasoning = "User is seeking viable alternative crop options."
        elif any(term in q_lower for term in ["predict yield", "expected yield", "forecast yield", "what will the yield be"]):
            intent = QueryIntent.YIELD_PREDICTION
            reasoning = "User wants to forecast or predict crop yield."
        elif any(term in q_lower for term in ["why did the same crop produce different", "yield difference", "analyze yield", "yield factor"]):
            intent = QueryIntent.YIELD_ANALYSIS
            reasoning = "User is inquiring about causes of historical yield variance."
        elif any(term in q_lower for term in ["soil", "nitrogen", "phosphorus", "potassium", "ph balance"]):
            if "which crop" in q_lower or "suitable" in q_lower:
                intent = QueryIntent.CROP_RECOMMENDATION
            else:
                intent = QueryIntent.SOIL_ANALYSIS
            reasoning = "User query focuses on soil nutrient parameters."
        elif any(term in q_lower for term in ["weather", "rainfall", "temperature", "humidity", "monsoon"]):
            if "which crop" in q_lower or "suitable" in q_lower:
                intent = QueryIntent.CROP_RECOMMENDATION
            else:
                intent = QueryIntent.WEATHER_ANALYSIS
            reasoning = "User query evaluates weather conditions and climate."
        elif any(term in q_lower for term in ["suitable", "suitability", "can i grow", "is it good to grow"]):
            intent = QueryIntent.CROP_SUITABILITY
            reasoning = "User query asks for suitability assessment of crops under specific conditions."

        # 2. Entity Extraction
        cond = InterpretedConditions()

        # Extract Crop
        for c_lower, c_title in self.crops_map.items():
            if re.search(r"\b" + re.escape(c_lower) + r"\b", q_lower):
                cond.crop = c_title
                break

        # Extract State
        for s_lower, s_title in self.states_map.items():
            if re.search(r"\b" + re.escape(s_lower) + r"\b", q_lower):
                cond.state = s_title
                break

        # Extract Season
        for se_lower, se_title in self.seasons_map.items():
            if re.search(r"\b" + re.escape(se_lower) + r"\b", q_lower):
                cond.season = se_title
                break

        # Extract pH (e.g. 'ph 6.5', 'ph=6.5', 'ph around 6.5', 'ph: 6.5')
        ph_match = re.search(r"\bph[:=\s]+(?:around\s+|approx\s+)?(\d+(?:\.\d+)?)", q_lower)
        if ph_match:
            cond.ph = float(ph_match.group(1))

        # Extract Nitrogen (N)
        n_match = re.search(r"\b(?:n|nitrogen)[:=\s]+(?:around\s+)?(\d+(?:\.\d+)?)", q_lower)
        if n_match:
            cond.n = float(n_match.group(1))

        # Extract Phosphorus (P)
        p_match = re.search(r"\b(?:p|phosphorus)[:=\s]+(?:around\s+)?(\d+(?:\.\d+)?)", q_lower)
        if p_match:
            cond.p = float(p_match.group(1))

        # Extract Potassium (K)
        k_match = re.search(r"\b(?:k|potassium)[:=\s]+(?:around\s+)?(\d+(?:\.\d+)?)", q_lower)
        if k_match:
            cond.k = float(k_match.group(1))

        # Extract Rainfall
        rain_match = re.search(r"\b(?:rainfall|rain)[:=\s]+(?:around\s+)?(\d+(?:\.\d+)?)\s*(?:mm)?", q_lower)
        if rain_match:
            cond.rainfall = float(rain_match.group(1))
        elif "high rainfall" in q_lower:
            cond.rainfall = 1400.0
        elif "low rainfall" in q_lower or "drought" in q_lower:
            cond.rainfall = 400.0

        # Extract Temperature
        temp_match = re.search(r"\b(?:temperature|temp)[:=\s]+(?:around\s+)?(\d+(?:\.\d+)?)\s*(?:°?c)?", q_lower)
        if temp_match:
            cond.temperature = float(temp_match.group(1))

        # Extract Humidity
        hum_match = re.search(r"\b(?:humidity)[:=\s]+(?:around\s+)?(\d+(?:\.\d+)?)\s*(?:%)?", q_lower)
        if hum_match:
            cond.humidity = float(hum_match.group(1))

        # 3. Apply Explicit User Overrides
        for k, v in user_overrides.items():
            if v is not None and hasattr(cond, k):
                setattr(cond, k, v)

        return QueryClassificationResult(
            intent=intent,
            confidence=0.92,
            interpreted_conditions=cond,
            reasoning=reasoning
        )

query_classifier = QueryClassificationAgent()
