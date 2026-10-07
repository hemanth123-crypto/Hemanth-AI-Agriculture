"""
app/guardrails/input_validation.py
Input validation guardrail checking boundary conditions, lengths, and biological limits.
Conforms to Section 14 of project specification.
"""

from typing import Tuple, Optional, Dict, Any

class InputValidationGuardrail:
    @staticmethod
    def validate_query_text(query: Optional[str]) -> Tuple[bool, Optional[str]]:
        """Checks for empty, whitespace-only, or excessively long user queries."""
        if not query or not query.strip():
            return False, "Query cannot be empty or whitespace only."
        
        cleaned = query.strip()
        if len(cleaned) < 3:
            return False, "Query is too short. Please provide meaningful agricultural context."

        if len(cleaned) > 1500:
            return False, f"Query length ({len(cleaned)} characters) exceeds maximum permissible limit of 1500."

        return True, None

    @staticmethod
    def validate_environmental_inputs(inputs: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validates agronomic values:
        - pH: [0.0, 14.0]
        - Humidity: [0.0, 100.0] %
        - Rainfall: >= 0.0 mm
        - N, P, K: >= 0.0
        - Temperature: [-30.0, 65.0] °C
        """
        if inputs.get("ph") is not None:
            try:
                val = float(inputs["ph"])
                if val < 0.0 or val > 14.0:
                    return False, f"Impossible soil pH value: {val}. Valid scientific range is 0.0 to 14.0."
            except (ValueError, TypeError):
                return False, f"Malformed numeric value for pH: {inputs['ph']}"

        if inputs.get("humidity") is not None:
            try:
                val = float(inputs["humidity"])
                if val < 0.0 or val > 100.0:
                    return False, f"Invalid relative humidity: {val}%. Must be between 0% and 100%."
            except (ValueError, TypeError):
                return False, f"Malformed numeric value for humidity: {inputs['humidity']}"

        if inputs.get("rainfall") is not None:
            try:
                val = float(inputs["rainfall"])
                if val < 0.0:
                    return False, f"Negative rainfall ({val} mm) is physically impossible."
            except (ValueError, TypeError):
                return False, f"Malformed numeric value for rainfall: {inputs['rainfall']}"

        for nutrient in ["n", "p", "k"]:
            if inputs.get(nutrient) is not None:
                try:
                    val = float(inputs[nutrient])
                    if val < 0.0:
                        return False, f"Negative nutrient level for {nutrient.upper()} ({val} kg/ha) is invalid."
                except (ValueError, TypeError):
                    return False, f"Malformed numeric value for {nutrient.upper()}: {inputs[nutrient]}"

        if inputs.get("temperature") is not None:
            try:
                val = float(inputs["temperature"])
                if val < -30.0 or val > 65.0:
                    return False, f"Extreme temperature ({val}°C) outside plausible agricultural thresholds (-30°C to 65°C)."
            except (ValueError, TypeError):
                return False, f"Malformed numeric value for temperature: {inputs['temperature']}"

        return True, None

input_guardrail = InputValidationGuardrail()
