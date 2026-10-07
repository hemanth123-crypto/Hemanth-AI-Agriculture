"""
scripts/build_index.py
Builds and saves the FAISS index, keyword search index, and metadata for agricultural cases.
Conforms to Section 8 of project specification.
"""

import sys
import time
from pathlib import Path
import pandas as pd

# Add root directory to python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.config.settings import settings
from app.utils.logging import get_logger
from app.rag.document_processor import process_dataframe_to_cases
from app.rag.embeddings import embedding_service
from app.rag.vector_store import FAISSVectorStore
from app.rag.keyword_search import keyword_engine

logger = get_logger("build_index")

def build_indexes(force_rebuild: bool = True):
    start_time = time.time()
    logger.info("Starting agricultural case index construction...")

    # Ensure processed data exists
    if not settings.PROCESSED_CSV_FILE.exists():
        logger.info(f"Processed dataset not found at {settings.PROCESSED_CSV_FILE}. Running preprocessing first...")
        from app.utils.preprocessing import run_preprocessing
        run_preprocessing()

    df = pd.read_csv(settings.PROCESSED_CSV_FILE)
    logger.info(f"Loaded processed dataset with {len(df)} records.")

    # 1. Construct agricultural case representations
    texts, metadatas = process_dataframe_to_cases(df)
    logger.info(f"Constructed {len(texts)} natural-language case documents and structured metadata.")

    # 2. Generate Embeddings
    logger.info(f"Encoding case documents using {settings.EMBEDDING_PROVIDER} ({settings.EMBEDDING_DIM} dims)...")
    vectors = embedding_service.encode(texts, batch_size=128)
    logger.info(f"Generated embeddings array of shape {vectors.shape}.")

    # 3. Build & Save FAISS Index
    vector_store = FAISSVectorStore(dim=settings.EMBEDDING_DIM)
    vector_store.add_documents(vectors=vectors, metadatas=metadatas, texts=texts)
    vector_store.save()

    # 4. Fit & Save TF-IDF Keyword Index
    logger.info("Fitting and saving lexical TF-IDF keyword index...")
    keyword_engine.fit(texts=texts, metadata=metadatas)
    keyword_engine.save()

    elapsed = round(time.time() - start_time, 2)
    logger.info(f"[SUCCESS] FAISS and Keyword indexes built and saved in {elapsed}s.")
    print("=" * 60)
    print(f"INDEX BUILD COMPLETE: {len(texts)} cases indexed ({elapsed}s)")
    print(f"FAISS index: {settings.FAISS_INDEX_FILE}")
    print(f"Metadata:    {settings.CASES_METADATA_FILE}")
    print(f"Keyword:     {settings.KEYWORD_INDEX_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    build_indexes()
