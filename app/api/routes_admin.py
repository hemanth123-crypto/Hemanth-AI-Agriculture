"""Administration endpoints guarded by the existing user role field."""

import json
import sqlite3
import time
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field

from app.auth.database import get_connection, get_user_by_email
from app.auth.security import decode_access_token
from app.config.settings import settings
from app.feedback.feedback_processor import feedback_processor
from app.feedback.feedback_store import feedback_store
from app.ml.model_loader import model_manager
from app.rag.retriever import case_retriever

router = APIRouter(prefix="/api/admin", tags=["Admin"])


class RetrievalQueryEvaluationRequest(BaseModel):
    benchmark_id: str = Field(min_length=1, max_length=40)
    top_k: int = Field(default=5, ge=1, le=20)


def calculate_query_retrieval_metrics(retrieved: List[Any], relevant_crops: List[str], top_k: int) -> Dict[str, Any]:
    """Calculate ranking metrics against the explicit ground-truth labels supplied by the evaluator."""
    relevant = {crop.strip().casefold() for crop in relevant_crops if crop and crop.strip()}
    hits = [str(getattr(case, "crop", "")).casefold() in relevant for case in retrieved[:top_k]]
    matched = {str(getattr(case, "crop", "")).casefold() for case, is_relevant in zip(retrieved[:top_k], hits) if is_relevant}
    has_labels = bool(relevant)
    reciprocal_rank = next((1.0 / rank for rank, is_relevant in enumerate(hits, 1) if is_relevant), 0.0)
    return {
        "ground_truth_available": has_labels,
        "ground_truth_note": None if has_labels else "N/A — ground truth unavailable",
        "precision_at_1": round(float(hits[0]) if hits else 0.0, 4) if has_labels else None,
        "precision_at_3": round(sum(hits[:3]) / min(3, len(hits)), 4) if hits and has_labels else (0.0 if has_labels else None),
        "precision_at_k": round(sum(hits) / top_k, 4) if has_labels else None,
        "recall_at_k": round(len(matched) / len(relevant), 4) if has_labels else None,
        "mrr": round(reciprocal_rank, 4) if has_labels else None,
        "hit_rate_at_k": float(any(hits)) if has_labels else None,
        "retrieved_count": len(hits),
        "relevant_crops": sorted(relevant),
        "relevant_crops_found": sorted(matched),
    }


def require_admin(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Require a valid session and the current database role to be exactly admin."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")
    payload = decode_access_token(authorization.split(" ", 1)[1])
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired authentication token.")
    user = get_user_by_email(payload["sub"])
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account not found.")
    if str(user.get("role", "")).lower() != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access required.")
    return user


def _latest_evaluation() -> Optional[Dict[str, Any]]:
    for path in (settings.EVALUATION_DIR / "reports" / "retrieval_evaluation_report.json",
                 settings.EVALUATION_DIR / "reports" / "evaluation_report.json"):
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
    return None


def _dataset_info() -> Dict[str, Any]:
    candidates = [settings.PROCESSED_CSV_FILE, settings.RAW_CSV_FILE, settings.SAMPLE_CSV_FILE]
    path = next((candidate for candidate in candidates if candidate.exists()), None)
    if path is None:
        return {"available": False, "reason": "No processed, raw, or sample dataset file is available."}
    try:
        df = pd.read_csv(path)
        crop_columns = [column for column in df.columns if column.strip().lower() in {"crop", "crop_name", "label"}]
        crops = sorted(str(value) for value in df[crop_columns[0]].dropna().unique()) if crop_columns else []
        return {
            "available": True,
            "record_count": int(len(df)),
            "columns": [str(column) for column in df.columns],
            "crop_types": crops,
            "source": path.name,
            "missing_values": {str(column): int(count) for column, count in df.isna().sum().items()},
            "updated_at": pd.Timestamp(path.stat().st_mtime, unit="s", tz="UTC").isoformat(),
        }
    except Exception:
        return {"available": False, "reason": "The available dataset could not be inspected."}


def _health_info() -> Dict[str, Any]:
    db_ok = False
    conn = None
    try:
        conn = get_connection()
        conn.execute("SELECT 1").fetchone()
        db_ok = True
    except sqlite3.Error:
        pass
    finally:
        if conn:
            conn.close()
    return {
        "api": "available",
        "user_database": "available" if db_ok else "unavailable",
        "vector_store": "available" if case_retriever._is_ready else "unavailable",
        "suitability_model": "loaded" if model_manager.suitability_model and model_manager.suitability_model.is_trained else "unavailable",
        "yield_model": "loaded" if model_manager.yield_model and model_manager.yield_model.is_trained else "unavailable",
        "llm_provider": "configured" if settings.has_openai() else "not configured",
        "request_latency": "unavailable: request telemetry is not stored",
        "application_logs": "unavailable: no persistent application log store is configured",
    }


@router.get("/overview")
def admin_overview(_: Dict[str, Any] = Depends(require_admin)) -> Dict[str, Any]:
    conn = None
    try:
        conn = get_connection()
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    except sqlite3.Error:
        total_users = None
    finally:
        if conn:
            conn.close()
    return {
        "total_registered_users": total_users,
        "total_agricultural_queries": None,
        "total_crop_recommendations": None,
        "total_yield_predictions": None,
        "recent_activity": None,
        "health": _health_info(),
        "latest_evaluation": _latest_evaluation(),
        "unavailable_reason": "Query, recommendation, prediction, and activity events are not persisted by this application.",
    }


@router.get("/users")
def admin_users(_: Dict[str, Any] = Depends(require_admin)) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT email, name, role, created_at, last_login FROM users ORDER BY created_at DESC").fetchall()
    finally:
        conn.close()
    return [
        {"email": row["email"], "name": row["name"], "role": row["role"],
         "created_at": row["created_at"], "last_login": row["last_login"], "status": "unknown (not tracked)"}
        for row in rows
    ]


@router.get("/feedback")
def admin_feedback(_: Dict[str, Any] = Depends(require_admin)) -> Dict[str, Any]:
    return {"summary": feedback_processor.analyze_feedback(), "records": feedback_store.get_all_feedback()}


@router.get("/evaluation")
def admin_evaluation(_: Dict[str, Any] = Depends(require_admin)) -> Dict[str, Any]:
    return {"latest": _latest_evaluation(), "history": [item for item in [_latest_evaluation()] if item]}


@router.get("/evaluation/queries")
def admin_evaluation_queries(_: Dict[str, Any] = Depends(require_admin)) -> Dict[str, Any]:
    """Return the existing labeled benchmark queries for single-query evaluation."""
    benchmark_path = settings.EVALUATION_DIR / "test_queries.json"
    try:
        queries = json.loads(benchmark_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=503, detail="The labeled retrieval benchmark is unavailable.") from exc
    return {"queries": [{"id": item["id"], "query": item["query"], "relevant_crops": item.get("relevant_crops", [])}
                        for item in queries if item.get("id") and item.get("query")]}


@router.post("/evaluation/run")
def run_admin_evaluation(_: Dict[str, Any] = Depends(require_admin)) -> Dict[str, Any]:
    """Run the local labeled-crop retrieval benchmark and save its ranking metrics."""
    from app.evaluation.retrieval_metrics import retrieval_evaluator
    started = time.perf_counter()
    metrics = retrieval_evaluator.evaluate_retrieval()
    report = {
        "evaluation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "evaluation_duration_seconds": round(time.perf_counter() - started, 2),
        "total_benchmark_queries": metrics.get("total_benchmark_queries", 0),
        "retrieval_metrics": metrics,
    }
    report_dir = settings.EVALUATION_DIR / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "retrieval_evaluation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


@router.post("/evaluation/query")
def evaluate_retrieval_query(
    request: RetrievalQueryEvaluationRequest,
    _: Dict[str, Any] = Depends(require_admin),
) -> Dict[str, Any]:
    """Evaluate one live hybrid retrieval query against administrator-supplied relevance labels."""
    benchmark_path = settings.EVALUATION_DIR / "test_queries.json"
    try:
        benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=503, detail="The labeled retrieval benchmark is unavailable.") from exc
    item = next((entry for entry in benchmark if entry.get("id") == request.benchmark_id), None)
    if not item:
        raise HTTPException(status_code=422, detail="Choose a valid benchmark query.")
    query = item["query"].strip()
    relevant_crops = [crop.strip() for crop in (item.get("relevant_crops") or []) if crop and crop.strip()]

    from app.agents.orchestrator import orchestrator
    from app.models.schemas import AdvisoryRequest
    from app.evaluation.llm_framework_evaluation import evaluate_with_ragas_and_deepeval

    started = time.perf_counter()
    # The query calculator needs the real project advisory but shouldn't wait
    # through a second cloud judge call before showing its local retrieval metrics.
    advisory = orchestrator.process_query(AdvisoryRequest(query=query, top_k=request.top_k), allow_remote_judge=False)
    retrieved = advisory.similar_cases or []
    retrieval_metrics = calculate_query_retrieval_metrics(retrieved, relevant_crops, request.top_k)
    contexts = [
        (
            f"Case {case.case_id}: {case.crop} in {case.state}, {case.season} {case.year}; "
            f"yield {case.yield_val:.2f} t/ha; N {case.n}, P {case.p}, K {case.k}, pH {case.ph}; "
            f"rainfall {case.rainfall} mm, temperature {case.temperature} C."
        )
        for case in retrieved[:request.top_k]
    ]
    if contexts:
        llm_framework_metrics = evaluate_with_ragas_and_deepeval(
            query=query,
            response=advisory.formatted_advisory,
            contexts=contexts,
        )
    else:
        no_context = {"status": "NOT AVAILABLE", "reason": "No retrieved context was available for evaluation.", "metrics": {}}
        llm_framework_metrics = {"ragas": no_context, "deepeval": no_context}

    framework_results = list(llm_framework_metrics.values())
    judge_complete = bool(framework_results) and all(
        result.get("status") == "COMPLETED" for result in framework_results
    )
    return {
        # Retrieval can succeed while external LLM judge calls fail. Report that
        # honestly instead of marking the combined evaluation as fully complete.
        "status": "COMPLETED" if judge_complete else "PARTIAL",
        "query": query,
        "benchmark_id": item["id"],
        "top_k": request.top_k,
        "relevant_crops": relevant_crops,
        "evaluation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "evaluation_duration_seconds": round(time.perf_counter() - started, 2),
        "retrieved_count": len(retrieved[:request.top_k]),
        "retrieval_metrics": retrieval_metrics,
        "llm_framework_metrics": llm_framework_metrics,
        "answer": advisory.formatted_advisory,
        "retrieved_cases": [
            {
                "case_id": case.case_id,
                "crop": case.crop,
                "state": case.state,
                "season": case.season,
                "year": case.year,
                "yield_t_ha": case.yield_val,
                "relevance_score": round(case.relevance_score, 4),
                "is_relevant": case.crop.casefold() in {crop.casefold() for crop in relevant_crops},
            }
            for case in retrieved[:request.top_k]
        ],
    }


@router.get("/ml")
def admin_ml(_: Dict[str, Any] = Depends(require_admin)) -> Dict[str, Any]:
    metrics_path = settings.EVALUATION_DIR / "reports" / "ml_metrics.json"
    metrics = None
    if metrics_path.exists():
        try:
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            metrics = None
    return {
        "suitability_model_loaded": bool(model_manager.suitability_model and model_manager.suitability_model.is_trained),
        "yield_model_loaded": bool(model_manager.yield_model and model_manager.yield_model.is_trained),
        "metrics": metrics,
        "reason": None if metrics is not None else "No saved ML evaluation report is available; this view will not retrain models.",
    }


@router.get("/dataset")
def admin_dataset(_: Dict[str, Any] = Depends(require_admin)) -> Dict[str, Any]:
    return _dataset_info()


@router.get("/health")
def admin_health(_: Dict[str, Any] = Depends(require_admin)) -> Dict[str, Any]:
    return _health_info()
