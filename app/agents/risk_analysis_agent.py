"""
app/agents/risk_analysis_agent.py
Risk Analysis Agent: Identifies environmental stress factors and prescribes mitigations.
Conforms to Section 21 of project specification.
"""

from typing import List
from app.models.schemas import InterpretedConditions, RiskAnalysisResult

class RiskAnalysisAgent:
    def analyze_risk(self, conditions: InterpretedConditions) -> RiskAnalysisResult:
        risk_factors = []
        mitigations = []

        # 1. pH evaluation
        if conditions.ph is not None:
            if conditions.ph < 5.5:
                risk_factors.append(f"Strongly acidic soil (pH {conditions.ph}), which limits phosphorus availability and microbial activity.")
                mitigations.append("Apply agricultural lime (calcium carbonate) or dolomite to raise soil pH toward 6.5.")
            elif conditions.ph > 8.0:
                risk_factors.append(f"Alkaline/saline soil (pH {conditions.ph}), hindering micronutrient (iron, zinc) absorption.")
                mitigations.append("Incorporate organic matter, farmyard manure, or gypsum to reduce alkalinity.")

        # 2. Moisture / Rainfall evaluation
        if conditions.rainfall is not None:
            if conditions.rainfall < 500.0:
                risk_factors.append(f"Low rainfall condition ({conditions.rainfall} mm), presenting moisture deficit or drought hazard.")
                mitigations.append("Adopt micro-irrigation (drip/sprinkler), mulching to preserve moisture, and drought-tolerant cultivars.")
            elif conditions.rainfall > 1800.0:
                risk_factors.append(f"High precipitation ({conditions.rainfall} mm), carrying waterlogging and root rot risks.")
                mitigations.append("Ensure raised-bed planting and clear field drainage channels to avoid standing water.")

        # 3. Thermal stress
        if conditions.temperature is not None:
            if conditions.temperature > 36.0:
                risk_factors.append(f"High ambient temperature ({conditions.temperature}°C) may cause pollen sterility or excessive transpiration.")
                mitigations.append("Schedule light irrigations during early morning or evening to cool the crop canopy.")
            elif conditions.temperature < 12.0:
                risk_factors.append(f"Low temperature ({conditions.temperature}°C) may retard germination and early vegetative vigor.")
                mitigations.append("Delay sowing until soil warms up or utilize frost-protection covers.")

        # Overall risk level
        if len(risk_factors) >= 2:
            overall_risk = "High"
        elif len(risk_factors) == 1:
            overall_risk = "Moderate"
        else:
            overall_risk = "Low"
            risk_factors.append("No critical soil or weather anomalies detected based on specified inputs.")
            mitigations.append("Follow standard regional agronomic practices and balanced fertilization schedule.")

        return RiskAnalysisResult(
            overall_risk=overall_risk,
            risk_factors=risk_factors,
            mitigations=mitigations
        )

risk_analysis_agent = RiskAnalysisAgent()
