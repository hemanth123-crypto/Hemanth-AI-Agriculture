"""
app/feedback/feedback_processor.py
Analyzes collected user feedback to identify poor retrieval, ungrounded recommendations,
and pattern failures. Does NOT automatically retrain production models without validation.
Conforms to Section 30 of project specification.
"""

from typing import Dict, Any, List
from app.feedback.feedback_store import feedback_store

class FeedbackProcessor:
    @staticmethod
    def analyze_feedback() -> Dict[str, Any]:
        records = feedback_store.get_all_feedback()
        if not records:
            return {
                "total_feedback": 0,
                "average_rating": 0.0,
                "positive_percentage": 0.0,
                "negative_percentage": 0.0,
                "flagged_poor_retrieval": [],
                "flagged_low_ratings": [],
                "common_failure_patterns": []
            }

        total = len(records)
        ratings = [r.get("rating", 3) for r in records]
        avg_rating = round(sum(ratings) / total, 2)
        thumbs_up = sum(1 for r in records if r.get("thumbs") == "up")
        pos_pct = round((thumbs_up / total) * 100, 1)

        low_ratings = [r for r in records if r.get("rating", 5) <= 2 or r.get("thumbs") == "down"]
        
        # Identify failure patterns
        poor_retrieval_cases = []
        failure_patterns = []

        for r in low_ratings:
            comment = str(r.get("comments", "")).lower()
            if "not relevant" in comment or "wrong state" in comment or "unrelated" in comment:
                poor_retrieval_cases.append(r)
            if "yield wrong" in comment or "unrealistic" in comment:
                failure_patterns.append(f"Yield estimate discrepancy reported for query: '{r.get('query')}'")

        return {
            "total_feedback": total,
            "average_rating": avg_rating,
            "positive_percentage": pos_pct,
            "negative_percentage": round(100.0 - pos_pct, 1),
            "flagged_low_ratings_count": len(low_ratings),
            "poor_retrieval_count": len(poor_retrieval_cases),
            "common_failure_patterns": failure_patterns[:5],
            "governance_rule": "Retraining requires human agronomic validation; auto-retraining disabled."
        }

feedback_processor = FeedbackProcessor()
