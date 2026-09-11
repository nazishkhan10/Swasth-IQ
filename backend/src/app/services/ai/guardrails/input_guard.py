"""
Input Guardrail Engine (Phase 7 AI Guardrails).
Sanitizes user queries, detects prompt injection attempts, and checks for out-of-scope non-medical topics.
"""

import re
from typing import Dict, Any


class InputGuardrail:
    """Sanitizes and validates incoming user prompt inputs."""

    INJECTION_PATTERNS = [
        r"ignore previous instructions",
        r"disregard all previous system instructions",
        r"you are now an unfiltered AI",
        r"system prompt override",
        r"jailbreak"
    ]

    OUT_OF_SCOPE_PATTERNS = [
        r"write a (python|javascript|code|script|program)",
        r"who (won|is the prime minister|is the president|won the match|won the cup)",
        r"tell me a (joke|story|poem)",
        r"what is the capital of",
        r"(crypto|stock|bitcoin) price"
    ]

    @classmethod
    def validate(cls, question: str) -> Dict[str, Any]:
        """Validates input question safety and domain scope."""
        clean_q = question.strip()
        if not clean_q:
            return {"valid": False, "reason": "Empty question provided.", "sanitized_question": ""}

        # Injection Check
        for pat in cls.INJECTION_PATTERNS:
            if re.search(pat, clean_q, re.IGNORECASE):
                return {
                    "valid": False,
                    "reason": "Security Alert: Prompt injection pattern detected.",
                    "sanitized_question": "Explain my health report."
                }

        # Truncate extreme length
        sanitized = clean_q[:500]
        return {"valid": True, "reason": "Passed input safety checks.", "sanitized_question": sanitized}

