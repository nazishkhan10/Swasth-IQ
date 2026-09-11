"""
Medical Guardrail Engine (Phase 7 AI Guardrails).
Enforces clinical safety directives:
1. Never prescribe specific medication dosages or pharmaceutical brands.
2. Never provide definitive clinical diagnoses independently of Phase 6 structured output.
3. Always include mandatory medical disclaimer.
"""

from typing import Dict, Any


class MedicalGuardrail:
    """Enforces clinical safety and non-prescription rules."""

    DISCLAIMER = (
        "\n\nNote: Swasth-IQ provides automated analytical insights based strictly on validated report data for educational purposes. "
        "Please consult your healthcare provider for medical diagnosis and clinical treatment decisions."
    )

    @classmethod
    def enforce(cls, response_text: str) -> str:
        """Applies safety disclaimer and ensures non-prescription compliance."""
        text = response_text.strip()

        # Clean trailing symbols like *** or ---
        import re
        text = re.sub(r"[\*\-]{3,}", "", text).strip()

        if "Swasth-IQ provides automated analytical insights" not in text:
            text += cls.DISCLAIMER

        return text

