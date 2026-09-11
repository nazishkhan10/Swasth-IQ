"""
Analytics Tracker (Phase 7 Chat Engine).
Records execution metrics, latencies, provider fallbacks, and token usage into ChatExecution database table.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.chat import ChatExecution


class AnalyticsTracker:
    """Logs detailed execution trace metrics to database."""

    @classmethod
    def log_execution(
        cls,
        db: Session,
        message_id: int,
        report_id: int,
        prompt_info: Dict[str, Any],
        provider_info: Dict[str, Any],
        funnel_metrics: Dict[str, Any],
        citations: list,
        trace_data: Dict[str, Any]
    ) -> ChatExecution:
        import json

        exec_record = ChatExecution(
            message_id=message_id,
            report_id=report_id,
            prompt_id=prompt_info.get("prompt_id"),
            prompt_version=prompt_info.get("prompt_version", "1.0.0"),
            prompt_hash=prompt_info.get("prompt_hash"),
            knowledge_version="2026.1",
            provider=provider_info.get("provider", "Sarvam-105B"),
            is_fallback=provider_info.get("is_fallback", False),
            latency_ms=provider_info.get("latency_ms", 0.0),
            tokens_used=provider_info.get("tokens_used", 0),
            candidates_retrieved=funnel_metrics.get("retrieved", 0),
            candidates_filtered=funnel_metrics.get("filtered", 0),
            candidates_reranked=funnel_metrics.get("reranked", 0),
            candidates_used=funnel_metrics.get("used", 0),
            execution_trace_json=json.dumps(trace_data),
            citations_json=json.dumps(citations),
            confidence_json=json.dumps(trace_data.get("confidence_scores", {})),
            analytics_json=json.dumps(funnel_metrics)
        )
        db.add(exec_record)
        db.commit()
        return exec_record
