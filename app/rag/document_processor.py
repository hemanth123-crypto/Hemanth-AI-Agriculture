"""
app/rag/document_processor.py
Constructs structured agricultural case documents from cleaned historical data.
Conforms to Section 7 of project specification.
"""

from typing import List, Dict, Any, Tuple
import pandas as pd

def build_case_text(row: pd.Series, case_id: str) -> str:
    """
    Creates a rich natural language representation of an agricultural case.
    Designed for high-accuracy semantic embedding and BM25/TF-IDF keyword matching.
    """
    crop = row.get("Crop", "Unknown")
    year = int(row.get("Crop_Year", 2020))
    season = row.get("Season", "Unknown")
    state = row.get("State", "Unknown")
    area = float(row.get("Area", 0.0))
    prod = float(row.get("Production", 0.0))
    yield_val = float(row.get("Yield", 0.0))
    fert = float(row.get("Fertilizer", 0.0))
    pest = float(row.get("Pesticide", 0.0))
    n = float(row.get("N", 0.0))
    p = float(row.get("P", 0.0))
    k = float(row.get("K", 0.0))
    ph = float(row.get("pH", 7.0))
    temp = float(row.get("Temperature", 25.0))
    rain = float(row.get("Rainfall", 800.0))
    humidity = float(row.get("Humidity", 65.0))

    text = (
        f"Case ID: {case_id}. "
        f"Crop: {crop}. Year: {year}. Season: {season}. State: {state}. "
        f"Soil conditions: Nitrogen N={n:.1f} kg/ha, Phosphorus P={p:.1f} kg/ha, "
        f"Potassium K={k:.1f} kg/ha, pH level {ph:.2f}. "
        f"Weather conditions: Temperature {temp:.1f}°C, Rainfall {rain:.1f} mm, Humidity {humidity:.1f}%. "
        f"Farming inputs: Fertilizer {fert:.1f} kg/ha, Pesticide {pest:.2f} kg/ha. "
        f"Cultivation: Area {area:.1f} hectares, Total Production {prod:.1f} tonnes. "
        f"Achieved Historical Crop Yield: {yield_val:.2f} tonnes/hectare."
    )
    return text

def build_case_metadata(row: pd.Series, case_id: str) -> Dict[str, Any]:
    """Generates structured metadata for precise filtering and re-ranking."""
    return {
        "case_id": case_id,
        "crop": str(row.get("Crop", "")),
        "year": int(row.get("Crop_Year", 2020)),
        "season": str(row.get("Season", "")),
        "state": str(row.get("State", "")),
        "area": float(row.get("Area", 0.0)),
        "production": float(row.get("Production", 0.0)),
        "yield_val": float(row.get("Yield", 0.0)),
        "fertilizer": float(row.get("Fertilizer", 0.0)),
        "pesticide": float(row.get("Pesticide", 0.0)),
        "n": float(row.get("N", 0.0)),
        "p": float(row.get("P", 0.0)),
        "k": float(row.get("K", 0.0)),
        "ph": float(row.get("pH", 7.0)),
        "temperature": float(row.get("Temperature", 25.0)),
        "rainfall": float(row.get("Rainfall", 800.0)),
        "humidity": float(row.get("Humidity", 65.0)),
        "npk_total": float(row.get("NPK_Total", 0.0))
    }

def process_dataframe_to_cases(df: pd.DataFrame) -> Tuple[List[str], List[Dict[str, Any]]]:
    """Converts entire dataframe into searchable case texts and structured metadata dictionaries."""
    texts: List[str] = []
    metadatas: List[Dict[str, Any]] = []

    for idx, row in df.iterrows():
        case_id = f"CASE_{idx + 1:04d}"
        text = build_case_text(row, case_id)
        meta = build_case_metadata(row, case_id)
        texts.append(text)
        metadatas.append(meta)

    return texts, metadatas
