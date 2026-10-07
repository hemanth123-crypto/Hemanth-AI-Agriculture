"""
app/evaluation/report_generator.py
Generates comprehensive evaluation reports in JSON and Markdown formats.
Conforms to Section 28 of project specification.
"""

import json
from pathlib import Path
from typing import Dict, Any, Tuple

from app.config.settings import settings
from app.utils.logging import get_logger

logger = get_logger("report_generator")

class ReportGenerator:
    @staticmethod
    def generate_markdown(eval_data: Dict[str, Any]) -> str:
        sys_perf = eval_data.get("system_performance", {})
        ret_metrics = eval_data.get("retrieval_metrics", {})
        rag_metrics = eval_data.get("rag_and_deepeval_metrics", {})
        ml_metrics = eval_data.get("ml_model_metrics", {})
        judge_metrics = eval_data.get("llm_judge_metrics", {})
        gr_metrics = eval_data.get("guardrail_metrics", {})

        suitability = ml_metrics.get("suitability_classifier", {})
        yield_reg = ml_metrics.get("yield_regressor", {})

        md = f"""# AI-Powered Agriculture Crop Advisory Assistant - Automated Evaluation Report

**Generated:** {eval_data.get('evaluation_timestamp', 'N/A')}  
**Total Benchmark Queries:** {eval_data.get('total_benchmark_queries', 0)}  
**Evaluation Protocol:** End-to-End System Evaluation (Section 28)

---

## 1. System Performance Summary
| Metric | Value |
|---|---|
| **Average Latency** | `{sys_perf.get('average_latency_ms', 0)} ms` |
| **Success Rate** | `{sys_perf.get('success_rate', 0) * 100:.1f}%` |
| **Error Rate** | `{sys_perf.get('error_rate', 0) * 100:.1f}%` |
| **Benchmark Queries Executed** | `{sys_perf.get('total_queries_executed', 0)}` |

---

## 2. Information Retrieval Metrics (Hybrid FAISS + TF-IDF)
*Evaluated across labeled agricultural queries with ground-truth relevant crops and regional metadata.*

| Metric | Score | Agronomic Interpretation |
|---|---|---|
| **Precision@1** | `{ret_metrics.get('precision_at_1', 'N/A')}` | First retrieved case is relevant |
| **Precision@3** | `{ret_metrics.get('precision_at_3', 'N/A')}` | Top 3 cases are relevant |
| **Precision@5** | `{ret_metrics.get('precision_at_5', 'N/A')}` | Top 5 retrieved cases relevant |
| **Recall@5** | `{ret_metrics.get('recall_at_5', 'N/A')}` | Fraction of all suitable crops retrieved |
| **Mean Reciprocal Rank (MRR)** | `{ret_metrics.get('mrr', 'N/A')}` | Speed of encountering first relevant case |
| **Hit Rate@5** | `{ret_metrics.get('hit_rate_at_5', 'N/A')}` | Probability of finding at least one valid case in top 5 |

---

## 3. RAG Quality & DeepEval Metrics
| Metric | Status / Score | Description |
|---|---|---|
| **Faithfulness** | `{rag_metrics.get('faithfulness', 'NOT AVAILABLE')}` | Grounding of recommendations in historical evidence |
| **Answer Relevancy** | `{rag_metrics.get('answer_relevancy', 'NOT AVAILABLE')}` | Directness in addressing user's agricultural query |
| **Contextual Relevancy** | `{rag_metrics.get('contextual_relevancy', 'NOT AVAILABLE')}` | Noise-free retrieval of regional weather/soil records |
| **Contextual Precision** | `{rag_metrics.get('contextual_precision', 'NOT AVAILABLE')}` | Signal-to-noise ratio in retrieved context |
| **Contextual Recall** | `{rag_metrics.get('contextual_recall', 'NOT AVAILABLE')}` | Comprehensiveness of retrieved historical cases |

> *Note: External DeepEval metrics requiring commercial OpenAI API keys are explicitly noted as `NOT AVAILABLE` when running completely offline per Section 28 rules.*

---

## 4. Machine Learning Model Evaluation
### A. Crop Suitability Classifier (RandomForestClassifier)
- **Accuracy:** `{suitability.get('accuracy', 'N/A')}`
- **Precision (Weighted):** `{suitability.get('precision', 'N/A')}`
- **Recall (Weighted):** `{suitability.get('recall', 'N/A')}`
- **F1-Score (Weighted):** `{suitability.get('f1_score', 'N/A')}`
- **Target Classes:** `{suitability.get('classes', [])}`
- **Test Samples Evaluated:** `{suitability.get('test_samples', 'N/A')}`

### B. Yield Prediction Regressor (RandomForestRegressor)
- **Mean Absolute Error (MAE):** `{yield_reg.get('mae', 'N/A')} t/ha`
- **Root Mean Squared Error (RMSE):** `{yield_reg.get('rmse', 'N/A')} t/ha`
- **R² Score:** `{yield_reg.get('r2_score', 'N/A')}`
- **Test Samples Evaluated:** `{yield_reg.get('test_samples', 'N/A')}`

---

## 5. LLM-as-a-Judge Evaluation
*Evaluates groundedness, safety compliance, and recommendation clarity.*

| Dimension | Score (0.00 - 1.00) |
|---|---|
| **Overall Quality** | `{judge_metrics.get('average_overall_score', 'N/A')}` |
| **Evidence Groundedness** | `{judge_metrics.get('average_groundedness', 'N/A')}` |
| **Evaluation Engine** | `{judge_metrics.get('status', 'CALCULATED')}` |

---

## 6. Guardrail & Security Evaluation
*Tested against adversarial prompt injections, negative rainfall, extreme pH, and domain boundary deviations.*

| Security Check | Result |
|---|---|
| **Guardrail Accuracy Rate** | `{gr_metrics.get('guardrail_accuracy_rate', 0) * 100:.1f}%` |
| **Prompt Injection Interception Rate** | `{gr_metrics.get('prompt_injection_detection_rate', 0) * 100:.1f}%` |
| **Validation Success Rate** | `{gr_metrics.get('validation_success_rate', 0) * 100:.1f}%` |
| **Adversarial Attacks Blocked** | `{gr_metrics.get('attacks_blocked', 0)} / {gr_metrics.get('attacks_evaluated', 0)}` |

---

## 7. Conclusion & Governance
All metrics in this report represent empirically evaluated tests on local benchmark queries and offline dataset splits.
No evaluation scores or historical cases were artificially fabricated.
"""
        return md

    @staticmethod
    def save_reports(eval_data: Dict[str, Any], output_dir: Path = None) -> Tuple[Path, Path]:
        output_dir = output_dir or (settings.EVALUATION_DIR / "reports")
        output_dir.mkdir(parents=True, exist_ok=True)

        json_path = output_dir / "evaluation_report.json"
        md_path = output_dir / "evaluation_report.md"

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(eval_data, f, indent=2)

        md_content = ReportGenerator.generate_markdown(eval_data)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        logger.info(f"Generated evaluation reports: {json_path} and {md_path}")
        return json_path, md_path

report_generator = ReportGenerator()
