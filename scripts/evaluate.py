"""
scripts/evaluate.py
CLI script to run end-to-end evaluation and generate:
- evaluation/reports/evaluation_report.json
- evaluation/reports/evaluation_report.md
Conforms to Section 28 of project specification.
"""

import sys
from pathlib import Path

# Add root directory to python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.evaluation.end_to_end_evaluation import end_to_end_evaluator
from app.evaluation.report_generator import report_generator

def main():
    print("=" * 65)
    print("AI Agriculture Advisory - Automated End-to-End Evaluation")
    print("=" * 65)
    try:
        eval_data = end_to_end_evaluator.run_full_evaluation()
        json_file, md_file = report_generator.save_reports(eval_data)
        print("[SUCCESS] Evaluation benchmark finished successfully!")
        print(f"JSON Report:     {json_file}")
        print(f"Markdown Report: {md_file}")
        print("-" * 65)
        print(f"Average Latency: {eval_data['system_performance']['average_latency_ms']} ms")
        print(f"Precision@5:     {eval_data['retrieval_metrics'].get('precision_at_5')}")
        print(f"MRR:             {eval_data['retrieval_metrics'].get('mrr')}")
        print(f"Hit Rate@5:      {eval_data['retrieval_metrics'].get('hit_rate_at_5')}")
        print(f"Yield R^2:       {eval_data['ml_model_metrics']['yield_regressor'].get('r2_score')}")
        print(f"Guardrail Rate:  {eval_data['guardrail_metrics'].get('guardrail_accuracy_rate') * 100:.1f}%")
        print("=" * 65)
    except Exception as e:
        print(f"[ERROR] Evaluation failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
