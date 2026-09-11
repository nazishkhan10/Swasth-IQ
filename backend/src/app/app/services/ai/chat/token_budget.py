"""
Token Budget Manager (Phase 7 Chat Engine).
Allocates strict token budgets across prompt sections:
Patient: 600, Timeline: 500, Knowledge: 1500, Evidence: 800, Memory: 600, Question: 200.
Prevents context window overflow.
"""

from typing import Dict, Any, List


class TokenBudgetManager:
    """Manages prompt section token budgets."""

    BUDGETS = {
        "system": 500,
        "patient": 600,
        "validated_data": 1200,
        "analysis": 1000,
        "knowledge": 1500,
        "evidence": 800,
        "memory": 600,
        "question": 200
    }

    @classmethod
    def truncate_str(cls, text: str, max_chars: int) -> str:
        if len(text) <= max_chars:
            return text
        return text[:max_chars] + "... [TRUNCATED]"

    @classmethod
    def fit_section(cls, section_name: str, content: str) -> str:
        budget_tokens = cls.BUDGETS.get(section_name, 800)
        max_chars = budget_tokens * 4  # approx 4 chars/token
        return cls.truncate_str(content, max_chars)
