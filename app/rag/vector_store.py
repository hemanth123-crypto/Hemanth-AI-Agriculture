"""
app/rag/vector_store.py
FAISS-powered vector store with persistence, metadata alignment, and fallback cosine search.
Conforms to Section 9 of project specification.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

from app.config.settings import settings
from app.utils.logging import get_logger

logger = get_logger("vector_store")

class FAISSVectorStore:
    def __init__(self, dim: int = 128):
        self.dim = dim
        self.index = None
        self.metadata: List[Dict[str, Any]] = []
        self.raw_texts: List[str] = []
        self.vectors: Optional[np.ndarray] = None
        self.is_faiss_active = FAISS_AVAILABLE
        
        if self.is_faiss_active:
            # Using IndexFlatIP on normalized vectors implements exact Cosine Similarity
            self.index = faiss.IndexFlatIP(self.dim)
        else:
            logger.warning("FAISS not found in environment; using NumPy Cosine Similarity fallback.")

    def add_documents(self, vectors: np.ndarray, metadatas: List[Dict[str, Any]], texts: List[str]):
        """Adds embedded vectors along with corresponding metadata and case texts."""
        if vectors.shape[1] != self.dim:
            raise ValueError(f"Vector dimension {vectors.shape[1]} does not match index dimension {self.dim}")

        vectors = vectors.astype(np.float32)
        # Ensure L2 normalized
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        vectors = vectors / norms

        self.metadata.extend(metadatas)
        self.raw_texts.extend(texts)
        
        if self.vectors is None:
            self.vectors = vectors
        else:
            self.vectors = np.vstack([self.vectors, vectors])

        if self.is_faiss_active and self.index is not None:
            self.index.add(vectors)
            logger.info(f"Added {vectors.shape[0]} vectors to FAISS index. Total: {self.index.ntotal}")
        else:
            logger.info(f"Added {vectors.shape[0]} vectors to NumPy vector store. Total: {len(self.metadata)}")

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Tuple[Dict[str, Any], float, str]]:
        """
        Retrieves top_k most semantically similar agricultural cases.
        Returns list of (metadata_dict, similarity_score, raw_text).
        """
        if len(self.metadata) == 0:
            return []

        query_vector = query_vector.astype(np.float32)
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
            
        norm = np.linalg.norm(query_vector)
        if norm > 0:
            query_vector = query_vector / norm

        top_k = min(top_k, len(self.metadata))

        if self.is_faiss_active and self.index is not None and self.index.ntotal > 0:
            distances, indices = self.index.search(query_vector, top_k)
            results = []
            for score, idx in zip(distances[0], indices[0]):
                if idx < 0 or idx >= len(self.metadata):
                    continue
                # Cosine similarity in range [0, 1]
                norm_score = float(max(0.0, min(1.0, (score + 1.0) / 2.0)))
                results.append((self.metadata[idx], norm_score, self.raw_texts[idx]))
            return results
        else:
            # Fallback pure NumPy dot product
            scores = np.dot(self.vectors, query_vector.T).flatten()
            top_indices = np.argsort(-scores)[:top_k]
            results = []
            for idx in top_indices:
                score = float(scores[idx])
                norm_score = float(max(0.0, min(1.0, (score + 1.0) / 2.0)))
                results.append((self.metadata[idx], norm_score, self.raw_texts[idx]))
            return results

    def save(self, index_path: Path = None, metadata_path: Path = None):
        """Persists index and metadata to disk."""
        index_path = index_path or settings.FAISS_INDEX_FILE
        metadata_path = metadata_path or settings.CASES_METADATA_FILE
        
        index_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)

        if self.is_faiss_active and self.index is not None:
            faiss.write_index(self.index, str(index_path))
            logger.info(f"Saved FAISS index to {index_path}")
        elif self.vectors is not None:
            # Save numpy backup
            np.save(str(index_path) + ".npy", self.vectors)
            logger.info(f"Saved NumPy vector store to {index_path}.npy")

        bundle = {
            "metadata": self.metadata,
            "raw_texts": self.raw_texts,
            "dim": self.dim
        }
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(bundle, f, indent=2)
        logger.info(f"Saved case metadata to {metadata_path}")

    def load(self, index_path: Path = None, metadata_path: Path = None) -> bool:
        """Loads index and metadata from disk. Returns True if successful."""
        index_path = index_path or settings.FAISS_INDEX_FILE
        metadata_path = metadata_path or settings.CASES_METADATA_FILE

        if not metadata_path.exists():
            logger.warning(f"Metadata file not found: {metadata_path}")
            return False

        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                bundle = json.load(f)
            self.metadata = bundle.get("metadata", [])
            self.raw_texts = bundle.get("raw_texts", [])
            self.dim = bundle.get("dim", self.dim)

            if self.is_faiss_active and index_path.exists():
                self.index = faiss.read_index(str(index_path))
                logger.info(f"Loaded FAISS index from {index_path} with {self.index.ntotal} vectors.")
            elif (Path(str(index_path) + ".npy")).exists():
                self.vectors = np.load(str(index_path) + ".npy")
                logger.info(f"Loaded NumPy vector store from {index_path}.npy with {len(self.metadata)} records.")
            else:
                logger.warning("FAISS binary not found, reconstructing fallback representation...")
                return False

            return True
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return False
