from types import SimpleNamespace
import json

from app.api import routes_admin
from app.agents.orchestrator import orchestrator
from app.config.settings import settings
from app.evaluation import llm_framework_evaluation as framework_evaluation
from app.evaluation.llm_framework_evaluation import _add_proxy_fallback, _proxy_scores


def _case(crop):
    return SimpleNamespace(crop=crop)


def test_query_retrieval_metrics_use_actual_labels_and_k():
    metrics = routes_admin.calculate_query_retrieval_metrics(
        [_case("Rice"), _case("Wheat"), _case("Maize")], ["rice", "maize"], 3
    )

    assert metrics["ground_truth_available"] is True
    assert metrics["precision_at_k"] == 0.6667
    assert metrics["recall_at_k"] == 1.0
    assert metrics["mrr"] == 1.0
    assert metrics["hit_rate_at_k"] == 1.0
    assert metrics["retrieved_count"] == 3


def test_query_retrieval_metrics_do_not_invent_labels():
    metrics = routes_admin.calculate_query_retrieval_metrics([_case("Rice")], [], 5)

    assert metrics["ground_truth_available"] is False
    assert metrics["ground_truth_note"] == "N/A — ground truth unavailable"
    assert metrics["precision_at_k"] is None
    assert metrics["recall_at_k"] is None
    assert metrics["mrr"] is None
    assert metrics["hit_rate_at_k"] is None
    assert metrics["retrieved_count"] == 1


def test_proxy_scores_are_deterministic_and_bounded():
    query = "Rice in Andhra Pradesh during Kharif"
    contexts = ["Rice grew well in Andhra Pradesh during Kharif season.", "Wheat in Punjab during Rabi."]
    answer = "Rice performed well in Andhra Pradesh during Kharif."

    scores = _proxy_scores(query, answer, contexts)
    assert scores == _proxy_scores(query, answer, contexts)
    assert round(scores["ragas"]["faithfulness"], 4) == 0.8333
    assert scores["ragas"]["context_utilization"] == 0.5
    assert 0 <= scores["deepeval"]["contextual_relevancy"] <= 1


def test_proxy_fallback_is_not_marked_as_an_official_score():
    result = _add_proxy_fallback(
        {"status": "ERROR", "reason": "private provider error", "metrics": {"faithfulness": {"value": None}}},
        {"faithfulness": 0.75},
    )

    metric = result["metrics"]["faithfulness"]
    assert result["status"] == "PROXY"
    assert metric["value"] is None
    assert metric["proxy_value"] == 0.75
    assert "not an official" in metric["source"]


def test_unreachable_judge_uses_proxies_and_skips_duplicate_provider_calls(monkeypatch):
    monkeypatch.setattr(framework_evaluation.settings, "has_openai", lambda: True)
    monkeypatch.setattr(
        framework_evaluation,
        "_run_ragas",
        lambda *_: {"status": "ERROR", "reason": "provider could not be reached", "metrics": {}},
    )
    monkeypatch.setattr(
        framework_evaluation,
        "_run_deepeval",
        lambda *_: (_ for _ in ()).throw(AssertionError("duplicate provider call")),
    )

    results = framework_evaluation.evaluate_with_ragas_and_deepeval(
        "Rice in Andhra Pradesh", "Rice performed well.", ["Rice in Andhra Pradesh"]
    )

    assert results["ragas"]["status"] == "PROXY"
    assert results["deepeval"]["status"] == "PROXY"
    assert results["ragas"]["metrics"]["faithfulness"]["value"] is None
    assert results["deepeval"]["metrics"]["contextual_relevancy"]["proxy_value"] == 1.0


def test_query_endpoint_returns_current_k_metrics_without_remote_advisory_judge(monkeypatch, tmp_path):
    evaluation_dir = tmp_path / "evaluation"
    evaluation_dir.mkdir()
    (evaluation_dir / "test_queries.json").write_text(json.dumps([{
        "id": "Q-test", "query": "Rice in Andhra Pradesh"
    }]), encoding="utf-8")
    monkeypatch.setattr(settings, "EVALUATION_DIR", evaluation_dir)
    case = SimpleNamespace(
        case_id="CASE-1", crop="Rice", state="Andhra Pradesh", season="Kharif", year=2024,
        yield_val=3.5, n=80, p=40, k=40, ph=6.5, rainfall=1000, temperature=28,
        relevance_score=0.9,
    )
    captured = {}

    def fake_process_query(request, allow_remote_judge=True):
        captured["top_k"] = request.top_k
        captured["allow_remote_judge"] = allow_remote_judge
        return SimpleNamespace(similar_cases=[case], formatted_advisory="Rice is supported by the retrieved case.")

    monkeypatch.setattr(orchestrator, "process_query", fake_process_query)
    monkeypatch.setattr(
        framework_evaluation, "evaluate_with_ragas_and_deepeval",
        lambda **_: {"ragas": {"status": "PROXY", "reason": "", "metrics": {}},
                     "deepeval": {"status": "PROXY", "reason": "", "metrics": {}}},
    )

    result = routes_admin.evaluate_retrieval_query(
        routes_admin.RetrievalQueryEvaluationRequest(benchmark_id="Q-test", top_k=1), {}
    )

    assert captured == {"top_k": 1, "allow_remote_judge": False}
    assert result["retrieval_metrics"]["precision_at_k"] is None
    assert result["retrieval_metrics"]["ground_truth_note"] == "N/A — ground truth unavailable"
    assert result["retrieval_metrics"]["retrieved_count"] == 1
    assert result["retrieved_cases"][0]["is_relevant"] is False
