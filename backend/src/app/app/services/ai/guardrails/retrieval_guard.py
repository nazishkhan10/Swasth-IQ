"""
Retrieval Guardrail Engine (Phase 7 AI Guardrails).
Verifies relevance of retrieved guideline passages before context assembly.
"""

from typing import List, Dict, Any


class RetrievalGuardrail:
    """Filters out low-relevance guideline passages."""

    @classmethod
    def filter_passages(cls, passages: List[Dict[str, Any]], min_score: float = 0.1) -> List[Dict[str, Any]]:
        """Filters retrieved passages below min_score threshold."""
        return [p for p in passages if p.get("rerank_score", p.get("score", 0.5)) >= min_score]
