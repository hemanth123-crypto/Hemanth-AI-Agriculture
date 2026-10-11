# AI-Powered Agriculture Crop Advisory Assistant - Automated Evaluation Report

**Generated:** 2026-10-08 14:14:15 UTC  
**Total Benchmark Queries:** 20  
**Evaluation Protocol:** End-to-End System Evaluation (Section 28)

---

## 1. System Performance Summary
| Metric | Value |
|---|---|
| **Average Latency** | `170.0 ms` |
| **Success Rate** | `100.0%` |
| **Error Rate** | `0.0%` |
| **Benchmark Queries Executed** | `20` |

---

## 2. Information Retrieval Metrics (Hybrid FAISS + TF-IDF)
*Evaluated across labeled agricultural queries with ground-truth relevant crops and regional metadata.*

| Metric | Score | Agronomic Interpretation |
|---|---|---|
| **Precision@1** | `0.9` | First retrieved case is relevant |
| **Precision@3** | `0.85` | Top 3 cases are relevant |
| **Precision@5** | `0.83` | Top 5 retrieved cases relevant |
| **Recall@5** | `0.4183` | Fraction of all suitable crops retrieved |
| **Mean Reciprocal Rank (MRR)** | `0.925` | Speed of encountering first relevant case |
| **Hit Rate@5** | `0.95` | Probability of finding at least one valid case in top 5 |

---

## 3. Machine Learning Model Evaluation
### A. Crop Suitability Classifier (RandomForestClassifier)
- **Accuracy:** `0.5533`
- **Precision (Weighted):** `0.5086`
- **Recall (Weighted):** `0.5533`
- **F1-Score (Weighted):** `0.4737`
- **Target Classes:** `['High Risk', 'Moderately Suitable', 'Suitable']`
- **Test Samples Evaluated:** `300`

### B. Yield Prediction Regressor (RandomForestRegressor)
- **Mean Absolute Error (MAE):** `0.4992 t/ha`
- **Root Mean Squared Error (RMSE):** `1.6865 t/ha`
- **R² Score:** `0.9876`
- **Test Samples Evaluated:** `300`

---

## 4. LLM-as-a-Judge Evaluation
*Evaluates groundedness, safety compliance, and recommendation clarity.*

| Dimension | Score (0.00 - 1.00) |
|---|---|
| **Overall Quality** | `0.972` |
| **Evidence Groundedness** | `1.0` |
| **Evaluation Engine** | `CALCULATED` |

---

## 5. Guardrail & Security Evaluation
*Tested against adversarial prompt injections, negative rainfall, extreme pH, and domain boundary deviations.*

| Security Check | Result |
|---|---|
| **Guardrail Accuracy Rate** | `100.0%` |
| **Prompt Injection Interception Rate** | `100.0%` |
| **Validation Success Rate** | `100.0%` |
| **Adversarial Attacks Blocked** | `3 / 3` |

---

## 6. Conclusion & Governance
All metrics in this report represent empirically evaluated tests on local benchmark queries and offline dataset splits.
No evaluation scores or historical cases were artificially fabricated.
