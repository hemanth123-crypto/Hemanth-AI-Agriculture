"""
app/rag/keyword_search.py
Lexical / Keyword search engine using TF-IDF token weighting across agricultural fields.
Conforms to Section 10 of project specification.
"""

import pickle
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from app.config.settings import settings
from app.utils.logging import get_logger
from app.utils.helpers import min_max_normalize

logger = get_logger("keyword_search")

class KeywordSearchEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            lowercase=True,
            sublinear_tf=True
        )
        self.tfidf_matrix = None
        self.case_metadata: List[Dict[str, Any]] = []
        self.raw_texts: List[str] = []

    def fit(self, texts: List[str], metadata: List[Dict[str, Any]]):
        """Fits TF-IDF on corpus of agricultural case texts."""
        self.raw_texts = texts
        self.case_metadata = metadata
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)
        logger.info(f"Fitted TF-IDF keyword index on {len(texts)} cases with {len(self.vectorizer.vocabulary_)} tokens.")

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict[str, Any], float, str]]:
        """
        Executes lexical keyword search.
        Returns list of (metadata, normalized_keyword_score, raw_text).
        """
        if self.tfidf_matrix is None or not self.raw_texts:
            return []

        query_vec = self.vectorizer.transform([query])
        scores = (self.tfidf_matrix * query_vec.T).toarray().flatten()

        if len(scores) == 0 or np.all(scores == 0):
            return []

        top_k = min(top_k, len(self.raw_texts))
        top_indices = np.argsort(-scores)[:top_k]

        max_score = float(np.max(scores)) if np.max(scores) > 0 else 1.0
        results = []
        for idx in top_indices:
            raw_score = float(scores[idx])
            # Normalize score
            norm_score = float(raw_score / max_score) if max_score > 0 else 0.0
            results.append((self.case_metadata[idx], norm_score, self.raw_texts[idx]))

        return results

    def save(self, filepath: Path = None):
        """Saves fitted TF-IDF model and text mapping."""
        filepath = filepath or settings.KEYWORD_INDEX_FILE
        filepath.parent.mkdir(parents=True, exist_ok=True)
        bundle = {
            "vectorizer": self.vectorizer,
            "tfidf_matrix": self.tfidf_matrix,
            "case_metadata": self.case_metadata,
            "raw_texts": self.raw_texts
        }
        with open(filepath, "wb") as f:
            pickle.dump(bundle, f)
        logger.info(f"Saved keyword index to {filepath}")

    def load(self, filepath: Path = None) -> bool:
        """Loads fitted TF-IDF model and corpus."""
        filepath = filepath or settings.KEYWORD_INDEX_FILE
        if not filepath.exists():
            logger.warning(f"Keyword index file not found: {filepath}")
            return False
        try:
            with open(filepath, "rb") as f:
                bundle = pickle.load(f)
            self.vectorizer = bundle["vectorizer"]
            self.tfidf_matrix = bundle["tfidf_matrix"]
            self.case_metadata = bundle["case_metadata"]
            self.raw_texts = bundle["raw_texts"]
            logger.info(f"Loaded keyword search index with {len(self.raw_texts)} cases.")
            return True
        except Exception as e:
            logger.error(f"Error loading keyword search index: {e}")
            return False

keyword_engine = KeywordSearchEngine()
