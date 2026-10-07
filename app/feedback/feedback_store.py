"""
app/feedback/feedback_store.py
Persistent storage for user ratings, thumbs up/down, and advisory feedback.
Conforms to Section 30 of project specification.
"""

import json
import uuid
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.config.settings import settings
from app.utils.logging import get_logger

logger = get_logger("feedback_store")

class FeedbackStore:
    def __init__(self, filepath: Optional[Path] = None):
        self.filepath = filepath or settings.FEEDBACK_FILE
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        if not self.filepath.exists():
            self._write_records([])

    def _read_records(self) -> List[Dict[str, Any]]:
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _write_records(self, records: List[Dict[str, Any]]):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)

    def add_feedback(
        self,
        query: str,
        recommendation: str,
        retrieved_cases: List[str],
        rating: int,
        thumbs: str,
        comments: str
    ) -> str:
        feedback_id = f"FB_{uuid.uuid4().hex[:8]}"
        record = {
            "feedback_id": feedback_id,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "query": query,
            "recommendation": recommendation,
            "retrieved_cases": retrieved_cases,
            "rating": rating,
            "thumbs": thumbs,
            "comments": comments
        }
        records = self._read_records()
        records.append(record)
        self._write_records(records)
        logger.info(f"Recorded feedback {feedback_id} (rating: {rating}, thumbs: {thumbs})")
        return feedback_id

    def get_all_feedback(self) -> List[Dict[str, Any]]:
        return self._read_records()

feedback_store = FeedbackStore()
