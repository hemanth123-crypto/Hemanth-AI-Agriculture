"""
app/ml/model_loader.py
Singleton loader for machine learning models.
Ensures zero-downtime lazy loading and graceful agronomic heuristic fallbacks.
"""

import pickle
import json
from pathlib import Path
from typing import Optional, Dict, Any

from app.config.settings import settings
from app.utils.logging import get_logger
from app.ml.crop_suitability import CropSuitabilityModel
from app.ml.yield_prediction import YieldPredictionModel

logger = get_logger("model_loader")

class ModelManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance.suitability_model = None
            cls._instance.yield_model = None
            cls._instance.metadata = {}
            cls._instance._load_models()
        return cls._instance

    def _load_models(self):
        # 1. Load Suitability Model
        if settings.SUITABILITY_MODEL_FILE.exists():
            try:
                with open(settings.SUITABILITY_MODEL_FILE, "rb") as f:
                    self.suitability_model = pickle.load(f)
                logger.info("Successfully loaded CropSuitabilityModel from disk.")
            except Exception as e:
                logger.error(f"Error loading suitability model: {e}")
                self.suitability_model = CropSuitabilityModel()
        else:
            logger.warning("Suitability model file not found; initializing un-fitted heuristic model.")
            self.suitability_model = CropSuitabilityModel()

        # 2. Load Yield Model
        if settings.YIELD_MODEL_FILE.exists():
            try:
                with open(settings.YIELD_MODEL_FILE, "rb") as f:
                    self.yield_model = pickle.load(f)
                logger.info("Successfully loaded YieldPredictionModel from disk.")
            except Exception as e:
                logger.error(f"Error loading yield model: {e}")
                self.yield_model = YieldPredictionModel()
        else:
            logger.warning("Yield model file not found; initializing un-fitted heuristic model.")
            self.yield_model = YieldPredictionModel()

        # 3. Load Feature Metadata
        if settings.FEATURE_METADATA_FILE.exists():
            try:
                with open(settings.FEATURE_METADATA_FILE, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
            except Exception as e:
                logger.error(f"Error loading feature metadata: {e}")

    def reload(self):
        """Forces reloading of models from disk."""
        self._load_models()

model_manager = ModelManager()
