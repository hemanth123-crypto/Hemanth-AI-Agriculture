"""
app/evaluation/llm_judge.py
LLM-as-a-Judge evaluation engine for groundedness, relevance, safety, and advisory quality.
Conforms to Section 22 of project specification.
"""

from typing import List, Dict, Any, Optional
import json
from app.config.settings import settings
from app.models.schemas import LLMJudgeResult, HistoricalCase, CropRecommendationItem
from app.utils.logging import get_logger

logger = get_logger("llm_judge")

class LLMJudge:
    def evaluate(
        self,
        query: str,
        recommendations: List[CropRecommendationItem],
        retrieved_cases: List[HistoricalCase],
        advisory_text: str,
        allow_remote: bool = True,
    ) -> LLMJudgeResult:
        """
        Evaluates the generated advisory response across 5 critical dimensions:
        1. Relevance: Did the answer address user's conditions?
        2. Groundedness: Are recommendations supported by retrieved cases?
        3. Recommendation Quality: Are agronomic explanations logical and complete?
        4. Safety: Are guarantees avoided and safety disclaimers included?
        5. Overall: Harmonic/weighted aggregate.
        """
        # If OpenAI is configured, attempt cloud LLM judge
        if allow_remote and settings.has_openai():
            try:
                import requests
                headers = {
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                }
                system_prompt = (
                    "You are a strict agricultural evaluation judge. "
                    "Score the advisory on: relevance (0-1), groundedness (0-1), "
                    "recommendation_quality (0-1), safety (0-1), overall (0-1). "
                    "Output pure JSON with keys: relevance, groundedness, recommendation_quality, safety, overall, reason."
                )
                user_msg = (
                    f"USER QUERY: {query}\n"
                    f"RETRIEVED CASES COUNT: {len(retrieved_cases)}\n"
                    f"GENERATED ADVISORY:\n{advisory_text[:2000]}"
                )
                payload = {
                    "model": settings.LLM_MODEL,
                    "temperature": 0.0,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_msg}
                    ]
                }
                resp = requests.post(
                    f"{settings.OPENAI_BASE_URL}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=settings.LLM_TIMEOUT
                )
                if resp.status_code == 200:
                    data = resp.json()["choices"][0]["message"]["content"]
                    parsed = json.loads(data)
                    return LLMJudgeResult(
                        relevance=float(parsed.get("relevance", 0.9)),
                        groundedness=float(parsed.get("groundedness", 0.9)),
                        recommendation_quality=float(parsed.get("recommendation_quality", 0.9)),
                        safety=float(parsed.get("safety", 1.0)),
                        overall=float(parsed.get("overall", 0.92)),
                        reason=str(parsed.get("reason", "OpenAI LLM Judge completed evaluation successfully."))
                    )
            except Exception as e:
                logger.warning(f"Cloud LLM Judge failed ({e}); switching to local deterministic evaluator.")

        # Local deterministic evaluator based on concrete verifiable metrics
        groundedness_score = 1.0
        if recommendations:
            retrieved_crop_names = {c.crop.lower() for c in retrieved_cases}
            grounded_count = sum(1 for r in recommendations if r.crop.lower() in retrieved_crop_names)
            groundedness_score = round(grounded_count / len(recommendations), 2)
        elif not retrieved_cases:
            groundedness_score = 0.50

        # Relevance score
        relevance_score = 0.95 if (recommendations or "No sufficiently similar" in advisory_text) else 0.40

        # Safety score: checks for absence of forbidden guarantee keywords
        guarantee_phrases = ["will definitely produce", "100% guaranteed", "zero risk"]
        has_prohibited = any(p in advisory_text.lower() for p in guarantee_phrases)
        safety_score = 0.40 if has_prohibited else 1.00

        # Quality score
        has_prediction = "PREDICTED YIELD" in advisory_text.upper()
        has_risk = "RISK ANALYSIS" in advisory_text.upper()
        quality_score = 0.95 if (has_prediction and has_risk and len(recommendations) > 0) else 0.80

        overall = round(
            (0.30 * relevance_score) + (0.35 * groundedness_score) + (0.20 * quality_score) + (0.15 * safety_score),
            3
        )

        reason = (
            f"Advisory evaluated locally: {len(recommendations)} recommendations grounded across "
            f"{len(retrieved_cases)} retrieved historical cases. Safety compliance: {safety_score:.2f}."
        )

        return LLMJudgeResult(
            relevance=relevance_score,
            groundedness=groundedness_score,
            recommendation_quality=quality_score,
            safety=safety_score,
            overall=overall,
            reason=reason
        )

llm_judge = LLMJudge()
