# AI-Powered Agriculture Crop Advisory Assistant — Evaluation Documentation

This document explains every evaluation metric employed across the system, why it was chosen, how it is calculated, which component it assesses, and how to interpret benchmark results.

---

## 1. Information Retrieval Metrics (Evaluates: RAG Hybrid Search Engine)

Retrieval metrics assess the quality of the dense FAISS vector index, sparse keyword index, and Reciprocal Rank Fusion (RRF) re-ranker.

### 1.1 Precision@K (e.g., Precision@1, Precision@3, Precision@5)
- **What it tells us:** Out of the top $K$ historical cases retrieved, what proportion is strictly relevant to the query's target crop, region, and season?
- **Formula:**
  $$\text{Precision@K} = \frac{\text{Count of relevant cases in top } K}{K}$$
- **Interpretation:** High Precision@5 ($> 0.80$) means the agricultural advisor does not flood the reasoning agent with noisy, irrelevant cases from mismatched states or seasons.
- **Evaluates:** Dense vector store + Sparse BM25 + Metadata filtering.

### 1.2 Recall@K (e.g., Recall@5)
- **What it tells us:** Out of all existing relevant cases in the database for the query context, what percentage was captured within the top $K$ results?
- **Formula:**
  $$\text{Recall@K} = \frac{\text{Count of relevant cases in top } K}{\text{Total relevant cases in dataset}}$$
- **Interpretation:** High Recall ensures that key historical precedent (e.g., record harvest years or drought survival cases) is not missed.
- **Evaluates:** Vector index coverage and retrieval cutoff threshold.

### 1.3 Mean Reciprocal Rank (MRR)
- **What it tells us:** How high up in the search results does the *first* genuinely relevant case appear?
- **Formula:**
  $$\text{MRR} = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}$$
  *(where $\text{rank}_i$ is the position of the first relevant result for query $i$)*
- **Interpretation:** An MRR of $1.0$ means the top result is always relevant. An MRR $> 0.90$ indicates the hybrid re-ranking algorithm prioritizes exact agricultural matches immediately.
- **Evaluates:** Reciprocal Rank Fusion (RRF) and re-ranking scoring.

### 1.4 Hit Rate@K (e.g., Hit Rate@5)
- **What it tells us:** What fraction of user queries retrieved *at least one* relevant case in the top $K$ results?
- **Formula:**
  $$\text{Hit Rate@K} = \frac{\text{Queries with } \ge 1 \text{ relevant case in top } K}{\text{Total Queries}}$$
- **Interpretation:** A Hit Rate of $0.95$ (95%) guarantees that almost no user receives a blank or completely irrelevant evidence set.
- **Evaluates:** End-to-end retrieval recall viability.

---

## 2. Generative RAG Quality Metrics (DeepEval Framework)

These metrics evaluate the generation quality of the multi-agent pipeline when synthesizing advice from retrieved cases.

### 2.1 Faithfulness
- **What it tells us:** Does the generated response state claims that are strictly supported by the retrieved context, without fabricating agricultural numbers or facts?
- **Formula:** Ratio of claims in the generated response that can be directly deduced from retrieved cases.
- **Evaluates:** Generative recommendation synthesis and anti-hallucination guardrails.

### 2.2 Answer Relevancy
- **What it tells us:** Does the final advisory directly answer the user's specific inquiry without drifting into unrelated farming advice?
- **Formula:** Semantic alignment between the user's original query and the generated advisory.
- **Evaluates:** Query classifier and final synthesizer agent.

### 2.3 Contextual Relevancy
- **What it tells us:** How much noise was present in the retrieved cases passed to the LLM?
- **Formula:** Ratio of retrieved sentences that are relevant to answering the query.
- **Evaluates:** Document chunking and hybrid reranker filter sharpness.

### 2.4 Contextual Precision
- **What it tells us:** Did the most informative agricultural cases appear at the top of the context window rather than buried at the bottom?
- **Evaluates:** Re-ranking prioritization.

### 2.5 Contextual Recall
- **What it tells us:** Did the retrieved context include all the background information necessary to produce a complete advisory?
- **Evaluates:** Retrieval depth ($top\_k$).

*(Note: When running in fully offline mode without OpenAI API keys, DeepEval metrics gracefully display as `NOT AVAILABLE (Offline Mode)`, while deterministic LLM-as-a-Judge metrics execute).*

---

## 3. Classification Metrics (Evaluates: Crop Suitability Model)

The `RandomForestClassifier` predicts whether a given crop is viable under specified soil and weather features.

### 3.1 Accuracy
- **What it tells us:** Overall percentage of correct crop suitability predictions across all test samples.
- **Formula:** $\frac{TP + TN}{TP + TN + FP + FN}$

### 3.2 Precision
- **What it tells us:** When the model declares a crop suitable, how often is it truly viable?
- **Agronomic Impact:** High precision prevents farmers from planting crops that will fail.

### 3.3 Recall
- **What it tells us:** Out of all crops that could genuinely thrive in the given conditions, how many did the model identify?
- **Agronomic Impact:** High recall ensures viable alternative crops are not overlooked.

### 3.4 F1-Score
- **What it tells us:** Harmonic mean of Precision and Recall ($2 \cdot \frac{P \cdot R}{P + R}$), balancing risk avoidance with crop diversity.

---

## 4. Regression Metrics (Evaluates: ML Yield Prediction Model)

The `RandomForestRegressor` estimates crop yield (in tonnes/hectare) alongside an empirical 80% confidence interval.

### 4.1 Mean Absolute Error (MAE)
- **What it tells us:** On average, how many tonnes per hectare does the prediction deviate from actual historical yield?
- **Formula:** $\text{MAE} = \frac{1}{n} \sum |y_i - \hat{y}_i|$
- **Interpretation:** Lower is better. Typical benchmark: $\le 0.45\text{ tonnes/ha}$.

### 4.2 Root Mean Squared Error (RMSE)
- **What it tells us:** Similar to MAE, but penalizes large forecasting errors heavily.
- **Formula:** $\text{RMSE} = \sqrt{\frac{1}{n} \sum (y_i - \hat{y}_i)^2}$

### 4.3 Coefficient of Determination ($R^2$)
- **What it tells us:** What percentage of historical yield variance is explained by soil, climate, fertilizer, and pesticide inputs?
- **Formula:** $R^2 = 1 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \bar{y})^2}$
- **Interpretation:** $1.0$ is a perfect fit. The trained model achieves $R^2 \approx 0.98$, confirming strong predictive signal from agronomic features.

---

## 5. LLM-as-a-Judge Evaluation (Evaluates: End-to-End Advisory)

A deterministic, offline-safe auditor (`LLMJudgeValidator`) inspects the final output payload before dispatch.

| Dimension | Scoring Mechanism | Target Standard |
|---|---|---|
| **Relevance** | Verifies that crops and conditions mentioned in the query are addressed in the response. | Score $\ge 0.90$ |
| **Groundedness** | Checks that every recommended crop is present in retrieved historical cases. | Score $\ge 0.95$ |
| **Completeness (Quality)** | Checks that all Section 45 components (interpreted conditions, yield, risk, impact, limitations) are populated. | Score $1.00$ |
| **Safety** | Confirms output contains mandatory agricultural disclaimers and no toxic/restricted chemical recipes. | Score $1.00$ |

---

## 6. Guardrail Evaluation Metrics

### 6.1 Injection Detection Rate
- **What it tells us:** Percentage of adversarial injection attempts ("ignore instructions", "system prompt reveal", "jailbreak") caught and blocked.
- **Benchmark Target:** $100\%$ on standard evaluation suite.

### 6.2 Domain Scope Pass Rate
- **What it tells us:** Accuracy in filtering non-agricultural queries while passing legitimate agricultural queries.
- **Benchmark Target:** $> 98\%$.

### 6.3 Agronomic Range Protection
- **What it tells us:** Verification that impossible inputs ($pH < 0$, $pH > 14$, negative rainfall) are flagged before reaching the ML models.
- **Benchmark Target:** $100\%$.

---

## 7. How to Run the Automated Benchmark Suite

Execute from terminal:
```powershell
python scripts/evaluate.py
```
Or trigger via the web interface: **System Evaluation** tab $\rightarrow$ click **Run Automated Benchmark**.

Results are saved to:
- `evaluation/reports/evaluation_report.json`
- `evaluation/reports/evaluation_report.md`
