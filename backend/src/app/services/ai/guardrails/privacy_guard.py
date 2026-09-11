"""
Privacy Guardrail Engine (Phase 7 AI Guardrails).
Detects and masks Personally Identifiable Information (PII) like phone numbers, SSNs, or addresses
before structured contexts are transmitted to the LLM.
"""

import re
from typing import Dict, Any


class PrivacyGuardrail:
    """Masks PII elements in patient metadata contexts."""

    @classmethod
    def mask_pii(cls, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Returns metadata with PII fields masked or sanitized."""
        masked = dict(metadata)
        if "phone" in masked:
            masked["phone"] = "[MASKED PHONE]"
        if "address" in masked:
            masked["address"] = "[MASKED ADDRESS]"
        if "ssn" in masked:
            masked["ssn"] = "[MASKED SSN]"
        return masked
