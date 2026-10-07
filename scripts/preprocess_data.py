"""
scripts/preprocess_data.py
CLI script to preprocess agricultural dataset and generate data quality report.
"""

import sys
from pathlib import Path

# Add root directory to python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.utils.preprocessing import run_preprocessing

def main():
    print("=" * 60)
    print("AI Agriculture Advisory - Data Preprocessing Pipeline")
    print("=" * 60)
    try:
        proc_csv, report_json = run_preprocessing()
        print(f"[SUCCESS] Processed CSV: {proc_csv}")
        print(f"[SUCCESS] Quality Report: {report_json}")
    except Exception as e:
        print(f"[ERROR] Preprocessing failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
