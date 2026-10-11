# AI-Powered Agriculture Crop Advisory Assistant — Architecture Specification

## 1. System Architecture Diagram

```mermaid
flowchart TD
    %% Styling Classes
    classDef dataCls fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;
    classDef ragCls fill:#1e3a5f,stroke:#60a5fa,stroke-width:2px,color:#f8fafc;
    classDef mlCls fill:#2e1065,stroke:#c084fc,stroke-width:2px,color:#f8fafc;
    classDef agentCls fill:#064e3b,stroke:#34d399,stroke-width:2px,color:#f8fafc;
    classDef guardCls fill:#7f1d1d,stroke:#f87171,stroke-width:2px,color:#f8fafc;
    classDef apiCls fill:#78350f,stroke:#fbbf24,stroke-width:2px,color:#f8fafc;
    classDef evalCls fill:#3b0764,stroke:#e879f9,stroke-width:2px,color:#f8fafc;

    %% Data Pipeline Subgraph
    subgraph Data_Pipeline ["1. Data Engineering & Ingestion Pipeline"]
        D1[Raw Agricultural Data<br/><i>data/raw/agriculture.csv</i>]:::dataCls --> D2[Data Preprocessing & Validation<br/><i>Clean, Normalize, Impute</i>]:::dataCls
        D2 --> D3[Agricultural Case Construction<br/><i>Textual & Tabular Formatting</i>]:::dataCls
        D3 --> D4[Processed Cases Store<br/><i>data/processed/cases.json</i>]:::dataCls
    end

    %% RAG Indexing Subgraph
    subgraph RAG_Indexing ["2. Hybrid Index Construction"]
        D4 --> R1[Dense TF-IDF/SVD Vectorizer<br/><i>300-dim Normalized Embeddings</i>]:::ragCls
        D4 --> R2[Sparse Inverted Keyword Index<br/><i>BM25-style Token Frequencies</i>]:::ragCls
        R1 --> R3[(FAISS Vector Store<br/><i>IndexFlatIP Cosine Similarity</i>)]:::ragCls
        R2 --> R4[(Sparse Inverted Index<br/><i>Keyword Weights</i>)]:::ragCls
    end

    %% ML Model Training Subgraph
    subgraph ML_Training ["3. Machine Learning Models"]
        D2 --> M1[Feature Engineering<br/><i>NPK, pH, Rainfall, Temp</i>]:::mlCls
        M1 --> M2[Crop Suitability Classifier<br/><i>RandomForestClassifier</i>]:::mlCls
        M1 --> M3[Yield Prediction Regressor<br/><i>RandomForestRegressor + 80% CI</i>]:::mlCls
        M2 --> M4[(Persisted Models<br/><i>models/*.pkl</i>)]:::mlCls
        M3 --> M4
    end

    %% User Interface & API Gateways
    subgraph User_Boundary ["4. Client Application & API Layer"]
        UI[Single Page App Dashboard<br/><i>Login, Advisory, Explorer, Eval</i>]:::apiCls
        UI <-->|HTTP JSON| API[FastAPI Application Server<br/><i>app/api/routes_*.py</i>]:::apiCls
    end

    %% Multi-Agent Pipeline
    subgraph Agent_Pipeline ["5. Multi-Agent Advisory Workflow"]
        API --> G1{Input Guardrails<br/><i>Sanitize, Injection, Scope, Range</i>}:::guardCls
        G1 -->|Rejected| G_ERR[Validation Error Response]:::guardCls
        G1 -->|Approved| A1[Agent 1: Query Classifier<br/><i>Extract Intent, Crops, Soil, Weather</i>]:::agentCls
        
        A1 --> A2[Agent 2: Hybrid Retrieval<br/><i>FAISS Dense + Sparse Keyword</i>]:::agentCls
        R3 -.-> A2
        R4 -.-> A2
        
        A2 --> A3[Agent 3: Metadata Filter & Reranker<br/><i>RRF Fusion + Agronomic Re-ranking</i>]:::ragCls
        
        A3 --> A4[Agent 4: Recommendation Agent<br/><i>Evidence-Grounded Crop Selection</i>]:::agentCls
        A4 --> A5[Agent 5: Agronomic Risk Agent<br/><i>Soil Salinity, Stress & Drought Risk</i>]:::agentCls
        
        A5 --> A6[Agent 6: Yield Prediction Agent<br/><i>RandomForest Inference + 80% CI</i>]:::mlCls
        M4 -.-> A6
        
        A6 --> A7[Agent 7: Impact Analysis Agent<br/><i>Feature Importance & Sensitivities</i>]:::agentCls
        
        A7 --> G2{Agent 8: Validation & LLM Judge<br/><i>Groundedness & Output Guardrails</i>}:::guardCls
        G2 -->|Approved| RESP[Final Section 45 Structured Advisory]:::apiCls
    end

    %% Feedback & Evaluation
    subgraph Feedback_Evaluation ["6. Feedback & Continuous Governance"]
        RESP --> UI
        UI -->|Submit Rating| FB[Feedback Store<br/><i>data/feedback/feedback.json</i>]:::evalCls
        FB --> RETRAIN[Feedback Processor & Fine-Tuning Trigger]:::evalCls
        
        RESP -.-> EVAL[Evaluation Benchmark Engine<br/><i>Precision@K, MRR, R², MAE, guardrails</i>]:::evalCls
        EVAL --> REPO[Evaluation Reports<br/><i>JSON + Markdown</i>]:::evalCls
    end
```

---

## 2. High-Level Architectural Flow (The 16-Step Pipeline)

1. **Dataset Ingestion:** Raw agricultural records (`data/raw/agriculture.csv` or auto-generated 1,500 synthetic records) ingested with soil, climate, fertilizer, and yield attributes.
2. **Data Preprocessing:** Missing value imputation, outlier handling, agronomic range validation, and feature normalization.
3. **Case Construction:** Transformation of tabular rows into structured semantic documents combining natural language summaries and structured metadata dictionaries.
4. **Vector Embedding:** High-efficiency normalized dense vectorization (TF-IDF/SVD 300 dimensions) encoding agronomic context.
5. **FAISS Vector Index:** `IndexFlatIP` storing normalized embeddings for exact inner-product (cosine) similarity at sub-millisecond speeds.
6. **Keyword Inverted Index:** Lexical inverted index with BM25-style term-frequency inverse-document-frequency weighting for exact tokens (pH, crop names, agro-climatic zones).
7. **Hybrid Retrieval:** Concurrent execution of dense semantic search and sparse keyword retrieval.
8. **Metadata Filtering:** Hard regional and seasonal boundary filtering (`State`, `Season`, `Soil pH`, `Rainfall`).
9. **Re-ranking Engine:** Reciprocal Rank Fusion ($k=60$) coupled with agronomic similarity re-scoring.
10. **Multi-Agent Orchestrator:** Sequential, deterministic pipeline coordinating 8 specialized agents.
11. **Machine Learning Models:**
    - `RandomForestClassifier` for multi-crop suitability probability scoring.
    - `RandomForestRegressor` for expected yield estimation with tree-variance 80% confidence intervals.
12. **LLM Recommendation Synthesis:** Grounded synthesis of agricultural rationale strictly referencing retrieved historical case IDs.
13. **LLM-as-a-Judge Evaluation:** Offline-safe verification of relevance, groundedness, completeness, and safety.
14. **Output Guardrails:** Enforces mandatory agricultural disclaimers ("no future outcome guarantee"), verifies absence of hallucinated chemical recipes.
15. **Final Advisory Delivery:** Section 45 compliant structured JSON payload and rendered Markdown for the user dashboard.
16. **Continuous Feedback & Evaluation:** User star ratings and benchmark suites computing Precision@k, Recall@k, MRR, Hit Rate@k, $R^2$, MAE, and Guardrail pass rates.

---

## 3. Subsystem Breakdown

### Subsystem A: Data & Indexing Layer
- Location: `data/`, `indexes/`, `scripts/`
- Responsibilities: Preprocessing, index persistence, data quality auditing, synthetic record synthesis.

### Subsystem B: RAG & Search Layer
- Location: `app/rag/`
- Responsibilities: Dense vector representation, inverted keyword indexing, hybrid Reciprocal Rank Fusion, metadata constraint enforcement.

### Subsystem C: Machine Learning Layer
- Location: `app/ml/`, `models/`
- Responsibilities: Model training, hyperparameter management, serialization (`.pkl`), confidence interval calculation via ensemble variance.

### Subsystem D: Multi-Agent Pipeline
- Location: `app/agents/`
- Responsibilities: Intent extraction, modular risk analysis, yield extrapolation, recommendation assembly, groundedness auditing.

### Subsystem E: Guardrails & Safety
- Location: `app/guardrails/`
- Responsibilities: Prompt injection regex filters, out-of-domain query classification, numerical physical range checking, output disclaimer enforcement.

### Subsystem F: API & Presentation Layer
- Location: `app/api/`, `frontend/`, `app/main.py`
- Responsibilities: Asynchronous REST endpoints, interactive single-page dashboard with real-time feedback submission and live benchmark runs.

---

## 4. Visual Diagram Files
High-resolution visual diagrams are automatically generated and maintained in:
- `docs/architecture.png` (High-resolution PNG, 300 DPI)
- `docs/architecture.pdf` (Print-ready Vector PDF)
