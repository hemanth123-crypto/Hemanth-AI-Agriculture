"""
app/rag/metadata_filter.py
Structured metadata filtering for agricultural records.
Conforms to Section 12 of project specification.
"""

from typing import Dict, Any, List, Optional
import math

class MetadataFilter:
    @staticmethod
    def compute_match_score(case: Dict[str, Any], filters: Dict[str, Any]) -> float:
        """
        Computes a normalized metadata match score [0.0, 1.0] based on how many
        active user criteria are satisfied by the given case.
        """
        if not filters:
            return 1.0

        matches = 0
        total_criteria = 0

        # Exact / Substring categorical filters
        if filters.get("crop"):
            total_criteria += 1
            if str(case.get("crop", "")).lower() == str(filters["crop"]).lower():
                matches += 1

        if filters.get("state"):
            total_criteria += 1
            if str(case.get("state", "")).lower() == str(filters["state"]).lower():
                matches += 1

        if filters.get("season"):
            total_criteria += 1
            if str(case.get("season", "")).lower() == str(filters["season"]).lower():
                matches += 1

        if filters.get("year"):
            total_criteria += 1
            if int(case.get("year", 0)) == int(filters["year"]):
                matches += 1

        # Numerical range tolerances
        # pH: tolerance +/- 0.8
        if filters.get("ph") is not None:
            total_criteria += 1
            target_ph = float(filters["ph"])
            case_ph = float(case.get("ph", 7.0))
            if abs(case_ph - target_ph) <= 0.8:
                matches += 1

        # Rainfall: tolerance +/- 25% or min/max
        if filters.get("rainfall_min") is not None:
            total_criteria += 1
            if float(case.get("rainfall", 0.0)) >= float(filters["rainfall_min"]):
                matches += 1
        elif filters.get("rainfall") is not None:
            total_criteria += 1
            target_rain = float(filters["rainfall"])
            case_rain = float(case.get("rainfall", 800.0))
            if abs(case_rain - target_rain) <= (0.35 * max(target_rain, 100.0)):
                matches += 1

        # Temperature: tolerance +/- 4°C
        if filters.get("temperature") is not None:
            total_criteria += 1
            target_temp = float(filters["temperature"])
            case_temp = float(case.get("temperature", 25.0))
            if abs(case_temp - target_temp) <= 4.0:
                matches += 1

        # Humidity: tolerance +/- 15%
        if filters.get("humidity") is not None:
            total_criteria += 1
            target_hum = float(filters["humidity"])
            case_hum = float(case.get("humidity", 60.0))
            if abs(case_hum - target_hum) <= 15.0:
                matches += 1

        # N, P, K: tolerance +/- 30%
        for nutrient in ["n", "p", "k"]:
            if filters.get(nutrient) is not None:
                total_criteria += 1
                target_val = float(filters[nutrient])
                case_val = float(case.get(nutrient, 0.0))
                if abs(case_val - target_val) <= max(20.0, 0.35 * target_val):
                    matches += 1

        if total_criteria == 0:
            return 1.0

        return matches / total_criteria

    @staticmethod
    def filter_cases(cases: List[Dict[str, Any]], filters: Dict[str, Any], min_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Filters cases that meet at least min_threshold fraction of metadata criteria."""
        if not filters:
            return cases

        filtered = []
        for case in cases:
            score = MetadataFilter.compute_match_score(case, filters)
            if score >= min_threshold:
                filtered.append(case)
        return filtered
