# AI-Powered Agriculture Crop Advisory Assistant — API Documentation

This document describes all REST API endpoints provided by the application server, including request schemas, responses, curl examples, and error handling.

Interactive Swagger/OpenAPI documentation is also available live at `http://localhost:8000/docs`.

---

## 1. System Health Check

### `GET /health`
- **Purpose:** Verifies backend service status, index loading, ML model readiness, and available memory.
- **Method:** `GET`
- **URL:** `/health`
- **Headers:** None required

#### Success Response (200 OK)
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "vector_store_cases": 1500,
  "keyword_store_cases": 1500,
  "suitability_model_loaded": true,
  "yield_model_loaded": true,
  "openai_configured": false
}
```

#### Error Case (503 Service Unavailable)
Returned if critical indexes or ML models cannot be loaded into memory.
```json
{
  "detail": "Vector store or ML models not initialized."
}
```

---

## 2. Multi-Agent Advisory Query

### `POST /api/query`
- **Purpose:** Executes the full 8-agent advisory pipeline (Guardrails $\rightarrow$ Intent Classification $\rightarrow$ Hybrid RAG $\rightarrow$ Crop Recommendation $\rightarrow$ Risk Analysis $\rightarrow$ Yield Prediction $\rightarrow$ Impact Analysis $\rightarrow$ LLM Judge Validation).
- **Method:** `POST`
- **URL:** `/api/query`
- **Headers:** `Content-Type: application/json`

#### Request Schema
```json
{
  "query": "Which crops performed well in Andhra Pradesh during Kharif with pH 6.5 and high rainfall?",
  "top_k": 5,
  "filters": {
    "state": "Andhra Pradesh",
    "season": "Kharif"
  }
}
```
*Note: `filters` and `top_k` are optional.*

#### Success Response (200 OK)
```json
{
  "query": "Which crops performed well in Andhra Pradesh during Kharif with pH 6.5 and high rainfall?",
  "interpreted_conditions": {
    "crop": null,
    "season": "Kharif",
    "state": "Andhra Pradesh",
    "soil_type": null,
    "n": null,
    "p": null,
    "k": null,
    "ph": 6.5,
    "temperature": null,
    "rainfall": 1200.0,
    "humidity": null
  },
  "recommended_crops": [
    {
      "crop": "Rice",
      "suitability_score": 0.94,
      "risk_level": "LOW",
      "historical_avg_yield": 3.42,
      "recommendation_reason": "Strong performance across 4 historical Kharif cases in Andhra Pradesh with high rainfall."
    }
  ],
  "similar_cases": [
    {
      "case_id": "CASE_0412",
      "crop": "Rice",
      "season": "Kharif",
      "state": "Andhra Pradesh",
      "yield": 3.65,
      "rainfall": 1240.0,
      "ph": 6.4,
      "similarity_score": 0.884
    }
  ],
  "yield_prediction": {
    "crop": "Rice",
    "predicted_yield": 3.48,
    "unit": "tonnes/hectare",
    "confidence_interval_80": [3.12, 3.84],
    "key_influencing_factors": [
      {"factor": "Rainfall", "importance": 0.38},
      {"factor": "Nitrogen (N)", "importance": 0.24}
    ]
  },
  "risk_analysis": {
    "overall_risk": "LOW",
    "risk_factors": ["Adequate rainfall matching crop transpiration requirements."]
  },
  "impact_analysis": {
    "insights": ["Soil pH 6.5 is optimal for nutrient uptake in Rice."]
  },
  "validation": {
    "passed": true,
    "llm_judge_score": 0.96,
    "groundedness": "HIGH",
    "notes": "All recommended crops are verified against retrieved historical cases."
  },
  "formatted_advisory": "AGRICULTURAL ADVISORY\n=====================\n...",
  "disclaimer": "Recommendations are based on historical data and model predictions. They do not guarantee future agricultural outcomes."
}
```

#### Error Cases
- **400 Bad Request (Guardrail Failure - Injection):**
  ```json
  {"detail": "Query rejected by security guardrails: adversarial injection attempt detected."}
  ```
- **400 Bad Request (Guardrail Failure - Out of Domain):**
  ```json
  {"detail": "Query out of domain: please ask questions related to agriculture, crops, soil, or climate."}
  ```
- **422 Unprocessable Entity:** Query text is empty or parameter out of bounds.

---

## 3. Hybrid Semantic & Keyword Search

### `POST /api/search`
- **Purpose:** Direct hybrid search over historical agricultural cases using FAISS dense vectors and BM25-style keyword scores combined via Reciprocal Rank Fusion (RRF).
- **Method:** `POST`
- **URL:** `/api/search`

#### Request Schema
```json
{
  "query": "High yield Sugarcane in Maharashtra with drip irrigation",
  "top_k": 5,
  "state": "Maharashtra",
  "season": "Whole Year",
  "crop": "Sugarcane"
}
```

#### Success Response (200 OK)
```json
{
  "query": "High yield Sugarcane in Maharashtra with drip irrigation",
  "total_retrieved": 5,
  "cases": [
    {
      "case_id": "CASE_0109",
      "crop": "Sugarcane",
      "season": "Whole Year",
      "state": "Maharashtra",
      "yield": 84.5,
      "rainfall": 920.0,
      "ph": 7.2,
      "dense_score": 0.842,
      "sparse_score": 0.791,
      "rrf_score": 0.0328
    }
  ]
}
```

---

## 4. Standalone Crop Recommendation

### `POST /api/recommendation`
- **Purpose:** Standalone crop suitability ranking without running the full advisory agent chain.
- **Method:** `POST`
- **URL:** `/api/recommendation`

#### Request Schema
```json
{
  "state": "Punjab",
  "season": "Rabi",
  "ph": 7.0,
  "n": 120.0,
  "p": 60.0,
  "k": 40.0,
  "rainfall": 150.0,
  "temperature": 18.0
}
```

#### Success Response (200 OK)
```json
{
  "state": "Punjab",
  "season": "Rabi",
  "candidates": [
    {
      "crop": "Wheat",
      "suitability_probability": 0.95,
      "historical_avg_yield": 4.62,
      "risk_level": "LOW"
    },
    {
      "crop": "Barley",
      "suitability_probability": 0.81,
      "historical_avg_yield": 3.15,
      "risk_level": "LOW"
    }
  ]
}
```

---

## 5. Machine Learning Yield Prediction

### `POST /api/prediction`
- **Purpose:** Evaluates the `RandomForestRegressor` model to predict expected yield with 80% confidence interval for specific agronomic inputs.
- **Method:** `POST`
- **URL:** `/api/prediction`

#### Request Schema
```json
{
  "crop": "Cotton",
  "state": "Gujarat",
  "season": "Kharif",
  "area": 10.0,
  "n": 100.0,
  "p": 50.0,
  "k": 50.0,
  "ph": 7.4,
  "rainfall": 750.0,
  "temperature": 29.0,
  "humidity": 65.0,
  "fertilizer": 200.0,
  "pesticide": 12.0
}
```

#### Success Response (200 OK)
```json
{
  "crop": "Cotton",
  "predicted_yield": 2.14,
  "unit": "tonnes/hectare",
  "expected_range_80_ci": [1.88, 2.40],
  "standard_deviation": 0.20,
  "top_feature_importances": {
    "Rainfall": 0.32,
    "Temperature": 0.25,
    "Nitrogen": 0.18
  }
}
```

---

## 6. Soil, Weather & Farming-Input Impact Analysis

### `POST /api/analysis`
- **Purpose:** Identifies limiting factors and agricultural sensitivity for specific crop conditions.
- **Method:** `POST`
- **URL:** `/api/analysis`

#### Request Schema
```json
{
  "crop": "Maize",
  "ph": 5.2,
  "rainfall": 450.0,
  "temperature": 34.0
}
```

#### Success Response (200 OK)
```json
{
  "crop": "Maize",
  "limiting_factors": [
    "Soil pH (5.2) is acidic; optimal range for Maize is 5.8 to 7.0.",
    "Rainfall (450 mm) is below optimal vegetative water requirements."
  ],
  "recommendations": [
    "Apply agricultural lime to raise soil pH.",
    "Plan supplemental furrow or drip irrigation during tasseling stage."
  ]
}
```

---

## 7. User Feedback Submission

### `POST /api/feedback`
- **Purpose:** Submits agronomist / user feedback on an advisory response for continuous evaluation.
- **Method:** `POST`
- **URL:** `/api/feedback`

#### Request Schema
```json
{
  "query": "Which crops performed well in Andhra Pradesh during Kharif?",
  "rating": 5,
  "feedback_category": "ACCURATE",
  "comments": "Matches regional agricultural university package of practices.",
  "recommended_crop_evaluated": "Rice"
}
```

#### Success Response (200 OK)
```json
{
  "status": "success",
  "message": "Feedback recorded successfully",
  "feedback_id": "FB_20261006_0312"
}
```

---

## 8. Evaluation Benchmark

### `POST /api/evaluate`
- **Purpose:** Executes the automated evaluation suite against standardized test queries and test datasets.
- **Method:** `POST`
- **URL:** `/api/evaluate`

#### Success Response (200 OK)
```json
{
  "status": "completed",
  "latency_ms": 56.38,
  "precision_at_5": 0.83,
  "recall_at_5": 0.78,
  "mrr": 0.925,
  "hit_rate_at_5": 0.95,
  "yield_r2": 0.9876,
  "guardrail_detection_rate": 1.0,
  "report_json_path": "evaluation/reports/evaluation_report.json",
  "report_md_path": "evaluation/reports/evaluation_report.md"
}
```

### `GET /api/evaluation/latest`
- **Purpose:** Retrieves the most recently generated evaluation benchmark report.
- **Method:** `GET`
- **URL:** `/api/evaluation/latest`

#### Success Response (200 OK)
Returns the complete JSON evaluation benchmark dictionary.
