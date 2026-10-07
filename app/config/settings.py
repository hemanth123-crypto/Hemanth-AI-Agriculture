"""
app/config/settings.py
Centralized configuration management for the Agriculture Crop Advisory Assistant.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the repository
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

class Settings:
    BASE_DIR: Path = BASE_DIR
    # Server settings
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

    # LLM Settings (OpenAI-compatible)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "30"))

    # Embeddings
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "dense_local")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    EMBEDDING_DIM: int = int(os.getenv("EMBEDDING_DIM", "128"))

    # RAG Retrieval Parameters
    RETRIEVAL_TOP_K: int = int(os.getenv("RETRIEVAL_TOP_K", "5"))
    ALPHA_SEMANTIC: float = float(os.getenv("ALPHA_SEMANTIC", "0.50"))
    BETA_KEYWORD: float = float(os.getenv("BETA_KEYWORD", "0.30"))
    GAMMA_METADATA: float = float(os.getenv("GAMMA_METADATA", "0.20"))

    # Evaluation & Guardrails
    LLM_JUDGE_MIN_SCORE: float = float(os.getenv("LLM_JUDGE_MIN_SCORE", "0.70"))
    DEEPEVAL_ENABLED: bool = os.getenv("DEEPEVAL_ENABLED", "False").lower() in ("true", "1", "yes")
    GUARDRAIL_STRICT_MODE: bool = os.getenv("GUARDRAIL_STRICT_MODE", "True").lower() in ("true", "1", "yes")

    # Storage Paths
    DATA_RAW_DIR: Path = BASE_DIR / os.getenv("DATA_RAW_DIR", "data/raw")
    DATA_PROCESSED_DIR: Path = BASE_DIR / os.getenv("DATA_PROCESSED_DIR", "data/processed")
    DATA_SAMPLE_DIR: Path = BASE_DIR / "data" / "sample"
    MODELS_DIR: Path = BASE_DIR / os.getenv("MODELS_DIR", "models")
    INDEXES_DIR: Path = BASE_DIR / os.getenv("INDEXES_DIR", "indexes")
    EVALUATION_DIR: Path = BASE_DIR / "evaluation"
    FEEDBACK_FILE: Path = BASE_DIR / os.getenv("FEEDBACK_FILE", "data/feedback_store.json")

    # Default file paths
    RAW_CSV_FILE: Path = DATA_RAW_DIR / "crop_yield_data.csv"
    SAMPLE_CSV_FILE: Path = DATA_SAMPLE_DIR / "sample_crop_data.csv"
    PROCESSED_CSV_FILE: Path = DATA_PROCESSED_DIR / "processed_data.csv"
    QUALITY_REPORT_FILE: Path = DATA_PROCESSED_DIR / "data_quality_report.json"
    
    # Model files
    SUITABILITY_MODEL_FILE: Path = MODELS_DIR / "crop_suitability_model.pkl"
    YIELD_MODEL_FILE: Path = MODELS_DIR / "yield_prediction_model.pkl"
    FEATURE_METADATA_FILE: Path = MODELS_DIR / "feature_metadata.json"

    # Index files
    FAISS_INDEX_FILE: Path = INDEXES_DIR / "faiss_index.bin"
    CASES_METADATA_FILE: Path = INDEXES_DIR / "cases_metadata.json"
    KEYWORD_INDEX_FILE: Path = INDEXES_DIR / "keyword_index.pkl"

    def has_openai(self) -> bool:
        return bool(self.OPENAI_API_KEY and self.OPENAI_API_KEY.strip())

settings = Settings()
