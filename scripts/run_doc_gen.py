"""
scripts/run_doc_gen.py  — thin wrapper that sets UTF-8 stdout then runs the generator
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from pathlib import Path
import importlib.util

spec = importlib.util.spec_from_file_location(
    "generate_submission_docs",
    Path(__file__).parent / "generate_submission_docs.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.main()
