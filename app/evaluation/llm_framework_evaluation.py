"""Single-query LLM evaluation using Ragas and DeepEval with the configured judge."""

import asyncio
import re
from typing import Any, Dict, List

from app.config.settings import settings

_PROXY_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "by", "can", "during",
    "for", "from", "has", "have", "how", "i", "in", "is", "it", "me", "my", "of",
    "on", "or", "our", "the", "their", "this", "to", "under", "was", "were", "what",
    "which", "with", "would", "you", "your", "case", "cases", "crop", "crops", "yield",
}


def _content_tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", (text or "").casefold())
            if len(token) > 2 and token not in _PROXY_STOP_WORDS}


def _proxy_scores(query: str, response: str, contexts: List[str]) -> Dict[str, Dict[str, float | None]]:
    """Local lexical estimates. These are explicitly not RAGAS/DeepEval scores."""
    query_tokens = _content_tokens(query)
    context_tokens = _content_tokens(" ".join(contexts))
    answer_tokens = _content_tokens(response)
    query_coverage = (len(query_tokens & context_tokens) / len(query_tokens)) if query_tokens else None
    answer_support = (len(answer_tokens & context_tokens) / len(answer_tokens)) if answer_tokens else None
    relevant_contexts = sum(
        bool(query_tokens & _content_tokens(context)) for context in contexts
    )
    context_utilization = relevant_contexts / len(contexts) if contexts else None
    return {
        "ragas": {"faithfulness": answer_support, "context_utilization": context_utilization},
        "deepeval": {"faithfulness": answer_support, "contextual_relevancy": query_coverage},
    }


def _add_proxy_fallback(result: Dict[str, Any], fallback: Dict[str, float | None]) -> Dict[str, Any]:
    metrics = dict(result.get("metrics") or {})
    used_proxy = False
    for name, estimate in fallback.items():
        metric = dict(metrics.get(name) or {})
        if metric.get("value") is None and estimate is not None:
            metric["value"] = None
            metric.update({
                "proxy_value": round(float(estimate), 4),
                "source": "proxy estimate — lexical overlap; not an official framework score",
                "reason": "Estimated from query, retrieved text, and answer token overlap.",
            })
            used_proxy = True
        metrics[name] = metric
    if used_proxy:
        official_values = [item.get("value") for item in metrics.values() if isinstance(item, dict)]
        result = dict(result)
        result["status"] = "PARTIAL" if any(value is not None for value in official_values) else "PROXY"
        result["reason"] = "Judge unavailable; showing labeled local proxy estimates where calculable."
    result = dict(result)
    result["metrics"] = metrics
    return result


def _framework_result(status: str, reason: str, metrics: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return {"status": status, "reason": reason, "metrics": metrics or {}}


def _score_value(result: Any) -> float:
    value = getattr(result, "value", getattr(result, "score", result))
    return round(float(value), 4)


def _is_connection_error(exc: Exception) -> bool:
    lowered = f"{type(exc).__name__} {exc}".casefold()
    return any(marker in lowered for marker in (
        "apiconnectionerror", "connectionerror", "connecterror", "retryerror",
        "network is unreachable", "name or service not known", "connection refused",
        "timed out", "timeout",
    ))


def _connection_error_message() -> str:
    return (
        "The configured LLM judge provider could not be reached. Retrieval results are still valid, "
        "but no judge score was produced. Check the provider URL and server network access, then retry."
    )


def _error_summary(exc: Exception) -> str:
    """Return an actionable, bounded provider error without dumping response metadata."""
    message = str(exc)
    lowered = message.casefold()
    if _is_connection_error(exc):
        return _connection_error_message()
    if "in_flight_budget" in lowered or "in-flight budget" in lowered:
        return "The judge provider's concurrent-request limit was reached. Evaluations are now run one at a time; retry this query."
    if (
        "402" in lowered
        or "more credits" in lowered
        or "insufficient_quota" in lowered
        or ("credit" in lowered and ("insufficient" in lowered or "exhausted" in lowered))
        or "billing_hard_limit_reached" in lowered
        or "payment_required" in lowered
    ):
        return (
            "The configured judge provider has insufficient or exhausted credits. "
            "Retrieval results are still valid, but no judge score was produced. "
            "Add provider credits or configure a funded compatible provider, then retry."
        )
    if "max_tokens" in lowered or ("incomplete" in lowered and "output" in lowered):
        return "The judge response was truncated at its output-token limit."
    return message[:500]


def _run_ragas(query: str, response: str, contexts: List[str]) -> Dict[str, Any]:
    try:
        from openai import AsyncOpenAI
        from ragas.llms import llm_factory
        from ragas.metrics.collections import ContextUtilization, Faithfulness
    except ImportError as exc:
        return _framework_result("NOT INSTALLED", f"Install the Ragas dependency: {exc}")

    async def evaluate() -> Dict[str, Any]:
        client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            # Evaluations should fail promptly when a judge endpoint is down.
            timeout=max(1, min(settings.LLM_TIMEOUT, 8)),
            max_retries=0,
        )
        try:
            llm = llm_factory(settings.LLM_MODEL, provider="openai", client=client, max_tokens=1536)
            metrics = {
                "faithfulness": Faithfulness(llm=llm),
                "context_utilization": ContextUtilization(llm=llm),
            }
            outputs = []
            # A single OpenRouter-compatible account may have a strict in-flight
            # request budget. Avoid overlapping judge calls from RAGAS.
            connection_failed = False
            for metric in metrics.values():
                if connection_failed:
                    outputs.append(ConnectionError(_connection_error_message()))
                    continue
                try:
                    outputs.append(await metric.ascore(
                        user_input=query, response=response, retrieved_contexts=contexts
                    ))
                except Exception as exc:
                    outputs.append(exc)
                    connection_failed = _is_connection_error(exc)
            values: Dict[str, Any] = {}
            errors = []
            for (name, _), result in zip(metrics.items(), outputs):
                if isinstance(result, Exception):
                    reason = _error_summary(result)
                    values[name] = {"value": None, "reason": reason}
                    errors.append(f"{name}: {reason}")
                else:
                    values[name] = {"value": _score_value(result), "reason": str(getattr(result, "reason", ""))}
            scored = sum(item["value"] is not None for item in values.values())
            status = "COMPLETED" if scored == len(values) else "PARTIAL" if scored else "ERROR"
            return _framework_result(status, "; ".join(errors) if errors else "Ragas metrics completed.", values)
        except Exception as exc:
            return _framework_result("ERROR", _error_summary(exc))
        finally:
            await client.close()

    try:
        return asyncio.run(evaluate())
    except Exception as exc:
        return _framework_result("ERROR", _error_summary(exc))


def _run_deepeval(query: str, response: str, contexts: List[str]) -> Dict[str, Any]:
    try:
        from deepeval.metrics import ContextualRelevancyMetric, FaithfulnessMetric
        from deepeval.test_case import LLMTestCase
    except ImportError as exc:
        return _framework_result("NOT INSTALLED", f"Install the DeepEval dependency: {exc}")

    try:
        from deepeval.models import OpenAIModel
    except ImportError:
        # DeepEval 3.x exposes the OpenAI-compatible implementation as GPTModel.
        try:
            from deepeval.models.llms.openai_model import GPTModel as OpenAIModel
        except ImportError as exc:
            return _framework_result("NOT INSTALLED", f"DeepEval OpenAI model adapter is unavailable: {exc}")

    try:
        judge = OpenAIModel(
            model=settings.LLM_MODEL,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            temperature=0,
            # Some OpenAI-compatible providers advertise a large default completion
            # limit that exceeds a user's remaining credit balance. Keep judge
            # responses concise while leaving ample room for structured reasoning.
            generation_kwargs={"timeout": settings.LLM_TIMEOUT, "max_tokens": 1024},
        )
        test_case = LLMTestCase(input=query, actual_output=response, retrieval_context=contexts)
        metric_instances = {
            "faithfulness": FaithfulnessMetric(model=judge, include_reason=False),
            "contextual_relevancy": ContextualRelevancyMetric(model=judge, include_reason=False),
        }
        values: Dict[str, Any] = {}
        errors = []
        for name, metric in metric_instances.items():
            try:
                metric.measure(test_case)
                values[name] = {
                    "value": _score_value(metric.score),
                    "reason": str(getattr(metric, "reason", "") or ""),
                }
            except Exception as exc:
                reason = _error_summary(exc)
                values[name] = {"value": None, "reason": reason}
                errors.append(f"{name}: {reason}")
        scored = sum(item["value"] is not None for item in values.values())
        status = "COMPLETED" if scored == len(values) else "PARTIAL" if scored else "ERROR"
        return _framework_result(status, "; ".join(errors) if errors else "DeepEval metrics completed.", values)
    except Exception as exc:
        return _framework_result("ERROR", _error_summary(exc))


def evaluate_with_ragas_and_deepeval(query: str, response: str, contexts: List[str]) -> Dict[str, Any]:
    """Run both judge frameworks serially; return scores and honest error states."""
    if not settings.has_openai():
        reason = "Configure OPENAI_API_KEY in .env to run LLM-as-a-judge metrics."
        results = {
            "ragas": _framework_result("NOT CONFIGURED", reason),
            "deepeval": _framework_result("NOT CONFIGURED", reason),
        }
        proxies = _proxy_scores(query, response, contexts)
        return {name: _add_proxy_fallback(results[name], proxies[name]) for name in results}
    if not response.strip():
        reason = "The advisory pipeline did not return an answer to evaluate."
        return {
            "ragas": _framework_result("NOT AVAILABLE", reason),
            "deepeval": _framework_result("NOT AVAILABLE", reason),
        }
    # Both frameworks use the same configured endpoint. If Ragas establishes
    # that it is unreachable, don't spend another long retry sequence on it.
    ragas_result = _run_ragas(query, response, contexts)
    if "could not be reached" in ragas_result.get("reason", "").casefold():
        reason = _connection_error_message()
        deepeval_result = _framework_result("ERROR", reason, {
            name: {"value": None, "reason": reason}
            for name in ("faithfulness", "contextual_relevancy")
        })
    else:
        deepeval_result = _run_deepeval(query, response, contexts)
    proxies = _proxy_scores(query, response, contexts)
    return {
        "ragas": _add_proxy_fallback(ragas_result, proxies["ragas"]),
        "deepeval": _add_proxy_fallback(deepeval_result, proxies["deepeval"]),
    }
