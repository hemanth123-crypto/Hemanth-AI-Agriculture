"""
app/agents/yield_prediction_agent.py
Yield Prediction Agent: Interfaces with the trained regression model to forecast yields.
Conforms to Section 21 of project specification.
"""

from typing import Optional
from app.models.schemas import InterpretedConditions, YieldPredictionResult
from app.ml.model_loader import model_manager
from app.utils.logging import get_logger

logger = get_logger("yield_prediction_agent")

class YieldPredictionAgent:
    def predict(self, conditions: InterpretedConditions, target_crop: Optional[str] = None) -> YieldPredictionResult:
        crop = target_crop or conditions.crop or "Rice"
        sample_dict = {
            "crop": crop,
            "season": conditions.season or "Kharif",
            "state": conditions.state or "Andhra Pradesh",
            "area": conditions.area or 1000.0,
            "fertilizer": conditions.fertilizer or 120.0,
            "pesticide": conditions.pesticide or 1.0,
            "n": conditions.n or 80.0,
            "p": conditions.p or 40.0,
            "k": conditions.k or 40.0,
            "ph": conditions.ph or 6.5,
            "temperature": conditions.temperature or 28.0,
            "rainfall": conditions.rainfall or 1000.0,
            "humidity": conditions.humidity or 70.0
        }
        logger.info(f"Yield Prediction Agent predicting for crop='{crop}'")
        return model_manager.yield_model.predict(sample_dict)

yield_prediction_agent = YieldPredictionAgent()
