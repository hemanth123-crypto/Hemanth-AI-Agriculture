"""
app/agents/orchestrator.py
Deterministic Multi-Agent Pipeline Orchestrator.
Coordinates: Guardrails -> Query Understanding -> Retrieval -> Recommendation ->
             Risk Analysis -> Yield ML -> Impact Analysis -> Validation -> LLM-as-Judge -> Final Advisory.
Conforms to Section 21 of project specification.
"""

import time
from typing import Dict, Any, Optional
from app.config.settings import settings
from app.utils.logging import get_logger
from app.models.schemas import AdvisoryRequest, AdvisoryResponse, QueryIntent, InterpretedConditions
from app.guardrails.input_validation import input_guardrail
from app.guardrails.prompt_injection import prompt_injection_guardrail
from app.guardrails.scope_guardrail import scope_guardrail
from app.agents.query_classifier import query_classifier
from app.agents.retrieval_agent import retrieval_agent
from app.agents.crop_recommendation_agent import crop_recommendation_agent
from app.agents.risk_analysis_agent import risk_analysis_agent
from app.agents.yield_prediction_agent import yield_prediction_agent
from app.agents.agricultural_analysis_agent import agricultural_analysis_agent
from app.agents.validation_agent import validation_agent
from app.agents.final_advisor_agent import final_advisor_agent
from app.evaluation.llm_judge import llm_judge

logger = get_logger("orchestrator")

class MultiAgentOrchestrator:
    def process_query(self, req: AdvisoryRequest, allow_remote_judge: bool = True) -> AdvisoryResponse:
        start_time = time.time()
        logger.info(f"Starting multi-agent workflow for query: '{req.query}'")

        # -------------------------------------------------------------
        # 1. Input Guardrails & Security
        # -------------------------------------------------------------
        # A. Query text validation
        valid_query, query_err = input_guardrail.validate_query_text(req.query)
        if not valid_query:
            return self._build_error_response(req.query, f"Input Guardrail Error: {query_err}", start_time)

        # B. Prompt Injection check
        is_safe, injection_err = prompt_injection_guardrail.inspect(req.query)
        if not is_safe:
            return self._build_error_response(req.query, f"Security Alert: {injection_err}", start_time)

        # C. Domain Scope Guardrail
        in_scope, scope_err = scope_guardrail.check_scope(req.query)
        if not in_scope:
            return self._build_error_response(req.query, f"Scope Guardrail: {scope_err}", start_time)

        # D. Agronomic parameter limits validation
        param_dict = {
            "ph": req.ph, "humidity": req.humidity, "rainfall": req.rainfall,
            "n": req.n, "p": req.p, "k": req.k, "temperature": req.temperature
        }
        valid_params, param_err = input_guardrail.validate_environmental_inputs(param_dict)
        if not valid_params:
            return self._build_error_response(req.query, f"Parameter Error: {param_err}", start_time)

        # -------------------------------------------------------------
        # 2. Query Understanding Agent (Classification & Extraction)
        # -------------------------------------------------------------
        user_overrides = {
            "crop": req.crop, "state": req.state, "season": req.season,
            "n": req.n, "p": req.p, "k": req.k, "ph": req.ph,
            "temperature": req.temperature, "rainfall": req.rainfall,
            "humidity": req.humidity
        }
        classif_result = query_classifier.classify_and_extract(req.query, user_overrides=user_overrides)
        conditions = classif_result.interpreted_conditions
        intent = classif_result.intent

        # -------------------------------------------------------------
        # 3. Retrieval Agent (Hybrid Search)
        # -------------------------------------------------------------
        retrieved_cases = retrieval_agent.execute_retrieval(
            query=req.query,
            conditions=conditions,
            top_k=req.top_k or 5
        )

        # -------------------------------------------------------------
        # 4. Crop Recommendation Agent
        # -------------------------------------------------------------
        is_alt = (intent == QueryIntent.ALTERNATIVE_CROP)
        recommendations = crop_recommendation_agent.recommend(
            conditions=conditions,
            retrieved_cases=retrieved_cases,
            is_alternative_request=is_alt
        )

        # -------------------------------------------------------------
        # 5. Risk Analysis Agent
        # -------------------------------------------------------------
        risk_result = risk_analysis_agent.analyze_risk(conditions)

        # -------------------------------------------------------------
        # 6. Yield Prediction Agent (ML Model)
        # -------------------------------------------------------------
        target_crop = recommendations[0].crop if recommendations else (conditions.crop or "Rice")
        yield_result = yield_prediction_agent.predict(conditions, target_crop=target_crop)

        # -------------------------------------------------------------
        # 7. Agricultural Analysis Agent (Impacts & Correlations)
        # -------------------------------------------------------------
        impact_result = agricultural_analysis_agent.analyze_factors(crop=target_crop)

        # -------------------------------------------------------------
        # 8. Validation Agent (Output Guardrail & Grounding)
        # -------------------------------------------------------------
        is_valid, validation_errors = validation_agent.validate(
            recommendations=recommendations,
            retrieved_cases=retrieved_cases
        )

        # -------------------------------------------------------------
        # 9. LLM-as-a-Judge Evaluation
        # -------------------------------------------------------------
        draft_advisory = final_advisor_agent.assemble_advisory(
            conditions=conditions,
            recommendations=recommendations,
            similar_cases=retrieved_cases,
            yield_prediction=yield_result,
            risk_analysis=risk_result,
            impact_analysis=impact_result,
            judge_result=None
        )

        judge_scores = llm_judge.evaluate(
            query=req.query,
            recommendations=recommendations,
            retrieved_cases=retrieved_cases,
            advisory_text=draft_advisory,
            allow_remote=allow_remote_judge,
        )

        # Re-assemble final advisory with judge scores included
        final_text = final_advisor_agent.assemble_advisory(
            conditions=conditions,
            recommendations=recommendations,
            similar_cases=retrieved_cases,
            yield_prediction=yield_result,
            risk_analysis=risk_result,
            impact_analysis=impact_result,
            judge_result=judge_scores
        )

        elapsed_ms = round((time.time() - start_time) * 1000.0, 2)
        logger.info(f"Multi-agent workflow completed in {elapsed_ms}ms with {len(recommendations)} recommendations.")

        limitations = [
            "Recommendations reflect empirical historical patterns in the agricultural dataset.",
            "Field results may diverge due to extreme local weather anomalies or localized pest pressures.",
            "Soil testing by an accredited laboratory is recommended before large-scale fertilizer application."
        ]

        return AdvisoryResponse(
            query=req.query,
            intent=intent,
            interpreted_conditions=conditions,
            recommendations=recommendations,
            similar_cases=retrieved_cases,
            risk_analysis=risk_result,
            yield_prediction=yield_result,
            impact_analysis=impact_result,
            validation=judge_scores,
            formatted_advisory=final_text,
            limitations=limitations,
            execution_time_ms=elapsed_ms
        )

    def _build_error_response(self, query: str, message: str, start_time: float) -> AdvisoryResponse:
        elapsed_ms = round((time.time() - start_time) * 1000.0, 2)
        advisory_text = (
            "AGRICULTURAL ADVISORY - NOTICE\n\n"
            f"{message}\n\n"
            "Please refine your query with specific agricultural, crop, state, or soil parameters."
        )
        return AdvisoryResponse(
            query=query,
            intent=QueryIntent.UNSUPPORTED,
            interpreted_conditions=InterpretedConditions(),
            recommendations=[],
            similar_cases=[],
            risk_analysis=None,
            yield_prediction=None,
            impact_analysis=None,
            validation=None,
            formatted_advisory=advisory_text,
            limitations=[message],
            execution_time_ms=elapsed_ms
        )

orchestrator = MultiAgentOrchestrator()
