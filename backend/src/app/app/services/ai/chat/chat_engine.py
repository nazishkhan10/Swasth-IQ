"""
Master Chat Engine (Phase 7 — Medical AI Assistant & RAG Engine - Architecture v8.0).
Orchestrates entire pipeline:
User Question -> Rate Limiter -> Session Manager -> Input Guardrail -> RAG Retrieval ->
Prompt Builder -> Provider Manager (OpenAI GPT-5-Nano) -> Medical Guardrails -> Session DB.
"""

import json
import time
from typing import Dict, Any, Generator, List
from sqlalchemy.orm import Session

from app.models.chat import ChatMessage, ChatSession
from app.services.analysis.medical_analysis_engine import MedicalAnalysisEngine
from app.services.rag.retrieval.retriever import HybridRetriever
from app.services.ai.provider.provider_manager import ProviderManager
from app.services.ai.guardrails.input_guard import InputGuardrail
from app.services.ai.guardrails.rate_limiter import RateLimiter
from app.services.ai.guardrails.privacy_guard import PrivacyGuardrail
from app.services.ai.guardrails.retrieval_guard import RetrievalGuardrail
from app.services.ai.guardrails.medical_guard import MedicalGuardrail
from app.services.ai.chat.session_manager import SessionManager
from app.services.ai.chat.query_rewriter import QueryRewriter
from app.services.ai.chat.prompt_builder import PromptBuilder, PromptSanitizer
from app.services.ai.chat.citation_verifier import CitationVerifier
from app.services.ai.chat.analytics import AnalyticsTracker


class MedicalChatEngine:
    """Master AI Medical Assistant Orchestrator (Architecture Freeze v8.0)."""

    _provider_mgr = ProviderManager()

    @classmethod
    def get_starter_chips(cls, db: Session, report_id: int) -> List[Dict[str, str]]:
        """Generates dynamic conversation starter chips based on Phase 6 deterministic analysis."""
        try:
            analysis = MedicalAnalysisEngine.run_analysis(db, report_id)
            conditions = analysis.get("conditions") or []
            params = analysis.get("validated_parameters") or []

            starters = [
                {"label": "Explain my overall report", "query": "Can you explain my blood test results in simple terms?"},
                {"label": "Explain my Health Score", "query": "Explain my health score and risk category."}
            ]

            # Parameter specific chips
            abnormal_params = [p for p in params if p.get("status") in ["HIGH", "LOW", "CRITICAL_HIGH", "CRITICAL_LOW"]]
            if abnormal_params:
                p = abnormal_params[0]
                p_name = p.get("parameter_name") or p.get("parameter_code")
                starters.append({
                    "label": f"Why is {p_name} abnormal?",
                    "query": f"Why is my {p_name} {p.get('status','abnormal')} and what does it mean?"
                })

            if conditions:
                cond = conditions[0]
                c_name = cond.get("condition_name") if isinstance(cond, dict) else str(cond)
                starters.append({
                    "label": f"Explain {c_name}",
                    "query": f"What is {c_name} and what recommendations are provided?"
                })

            starters.append({
                "label": "What should I ask my doctor?",
                "query": "What key questions should I discuss with my doctor regarding this report?"
            })
            return starters[:5]
        except Exception:
            return [
                {"label": "Explain my report", "query": "Can you explain my blood test results in simple terms?"},
                {"label": "Explain Health Score", "query": "Explain my health score and risk category."},
                {"label": "Questions for Doctor", "query": "What key questions should I ask my doctor?"}
            ]

    @classmethod
    def ask(
        cls,
        db: Session,
        report_id: int,
        question: str,
        user_id: int = 1
    ) -> Dict[str, Any]:
        """Synchronous chat processing using Report-Scoped ChatSession."""
        # 1. Enforce Rate Limiting
        RateLimiter.check_rate_limit(report_id, user_id)

        # 2. Get active Report-Scoped ChatSession
        session = SessionManager.get_active_session(db, report_id, user_id)
        start_time = time.time()

        # 3. Fetch Phase 6 Analysis
        analysis_res = MedicalAnalysisEngine.run_analysis(db, report_id)

        # 4. Input Sanitization & Domain Check
        clean_q = PromptSanitizer.sanitize(question)

        # 5. Save User Message
        user_msg = ChatMessage(
            session_id=session.id,
            report_id=report_id,
            user_id=user_id,
            role="user",
            content=clean_q
        )
        db.add(user_msg)
        db.commit()

        # 6. Fetch Conversation Memory scoped to session
        past_msgs = db.query(ChatMessage).filter(ChatMessage.session_id == session.id).order_by(ChatMessage.id.asc()).all()
        past_dicts = [{"role": m.role, "content": m.content} for m in past_msgs[:-1]]

        # 7. Query Rewriter & Intent Classifier
        query_info = QueryRewriter.rewrite_and_classify(clean_q)
        intent = query_info["intent"]

        # 8. Hybrid RAG Retrieval
        rag_res = HybridRetriever.retrieve(report_id=report_id, question=clean_q, intent=intent)
        passages = RetrievalGuardrail.filter_passages(rag_res["passages"])
        masked_meta = PrivacyGuardrail.mask_pii(analysis_res.get("patient_metadata", {}))

        val_params = analysis_res.get("validated_parameters") or []

        # 9. Prompt Builder
        prompt_pkg = PromptBuilder.build_prompt(
            patient_meta=masked_meta,
            validated_params=val_params,
            analysis_data=analysis_res,
            retrieved_passages=passages,
            question=clean_q,
            chat_history=past_dicts[-4:]
        )

        # 10. LLM Generation via OpenAI GPT-5 Nano Provider Gateway
        try:
            llm_res = cls._provider_mgr.generate(
                messages=prompt_pkg["messages"],
                temperature=0.2,
                max_tokens=4096
            )
        except Exception as e:
            # Graceful degradation if OpenAI API is unavailable
            safe_content = (
                "AI Assistant is temporarily unavailable. Your deterministic medical analysis and clinical validation data remain available.\n\n"
                "Please try again shortly."
            )
            llm_res = {
                "content": safe_content,
                "provider": "System Fallback",
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "tokens_used": 0,
                "estimated_cost": 0.0,
                "latency_ms": 0.0
            }

        safe_content = MedicalGuardrail.enforce(llm_res["content"])
        citations = CitationVerifier.verify_and_build(passages, analysis_res.get("evidence", []))

        # Parse & Enhance for Structured React Cards (Freeze v8.2)
        from app.services.medical_ai.json_validator import JSONSchemaValidator
        from app.services.medical_ai.response_formatter import ResponseFormatter
        from app.services.medical_ai.response_enhancer import ResponseEnhancer

        _, parsed_json, _ = JSONSchemaValidator.validate_insight(safe_content)
        fmt_data = ResponseFormatter.format_response(parsed_json, val_params)
        enhanced_json = ResponseEnhancer.enhance(fmt_data, val_params)

        # 11. Save Assistant Response Message
        assist_msg = ChatMessage(
            session_id=session.id,
            report_id=report_id,
            user_id=user_id,
            role="assistant",
            content=safe_content,
            intent=intent,
            provider_used=llm_res["provider"],
            prompt_tokens=llm_res.get("prompt_tokens", 0),
            completion_tokens=llm_res.get("completion_tokens", 0),
            total_tokens=llm_res.get("tokens_used", 0),
            estimated_cost=llm_res.get("estimated_cost", 0.0)
        )
        db.add(assist_msg)
        db.commit()

        total_latency = round((time.time() - start_time) * 1000, 2)
        trace_data = {
            "query": clean_q,
            "intent": intent,
            "provider": llm_res["provider"],
            "prompt_version": PromptBuilder.VERSION,
            "estimated_cost_usd": llm_res.get("estimated_cost", 0.0),
            "tokens": llm_res.get("tokens_used", 0)
        }

        return {
            "message_id": assist_msg.id,
            "session_id": session.id,
            "role": "assistant",
            "content": safe_content,
            "content_json": enhanced_json,
            "intent": intent,
            "provider_used": llm_res["provider"],
            "prompt_tokens": llm_res.get("prompt_tokens", 0),
            "completion_tokens": llm_res.get("completion_tokens", 0),
            "total_tokens": llm_res.get("tokens_used", 0),
            "estimated_cost": llm_res.get("estimated_cost", 0.0),
            "confidence_score": analysis_res.get("confidence_scores", {}).get("overall_confidence", 0.95),
            "latency_ms": total_latency,
            "citations": citations,
            "execution_trace": trace_data
        }

