"""
app/utils/helpers.py
Utility functions for scoring, normalization, calculations, and text handling.
"""

import math
from typing import List, Dict, Any, Union

def min_max_normalize(scores: List[float]) -> List[float]:
    """Normalizes a list of numeric scores to the range [0.0, 1.0]."""
    if not scores:
        return []
    min_val = min(scores)
    max_val = max(scores)
    if math.isclose(min_val, max_val, rel_tol=1e-7, abs_tol=1e-7):
        return [1.0 if s > 0 else 0.0 for s in scores]
    return [(s - min_val) / (max_val - min_val) for s in scores]

def calculate_hybrid_score(
    semantic_score: float,
    keyword_score: float,
    metadata_score: float,
    alpha: float = 0.50,
    beta: float = 0.30,
    gamma: float = 0.20
) -> float:
    """
    Combines semantic, keyword, and metadata scores with normalized weighting.
    Formula: Final Score = alpha * semantic + beta * keyword + gamma * metadata
    """
    total_weight = alpha + beta + gamma
    if total_weight == 0:
        return 0.0
    a = alpha / total_weight
    b = beta / total_weight
    c = gamma / total_weight
    return (a * semantic_score) + (b * keyword_score) + (c * metadata_score)

def safe_float(val: Any, default: float = 0.0) -> float:
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

def safe_int(val: Any, default: int = 0) -> int:
    try:
        return int(val)
    except (ValueError, TypeError):
        return default

def clean_text(text: str) -> str:
    """Cleans and standardizes input text string."""
    if not text:
        return ""
    return " ".join(text.strip().split())
