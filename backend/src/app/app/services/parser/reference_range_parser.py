"""
Reference Range Parser Service.
Parses reference range strings into lower/upper numeric bounds and contextual qualifiers.
"""

import re
from typing import Dict, Any, Optional

class ReferenceRangeParser:
    """Extracts raw range, context (e.g., Male, Female, Adult), reference_low, and reference_high."""

    @classmethod
    def parse(cls, raw_range: str) -> Dict[str, Any]:
        result = {
            "raw": raw_range.strip() if raw_range else "",
            "context": "General",
            "low": None,
            "high": None
        }

        if not raw_range:
            return result

        clean = raw_range.strip()
        clean_lower = clean.lower()

        # 1. Check contextual qualifier (Male/Female/Adult/Child)
        if "male" in clean_lower and "female" not in clean_lower:
            result["context"] = "Adult Male"
        elif "female" in clean_lower:
            result["context"] = "Adult Female"
        elif "child" in clean_lower or "pediatric" in clean_lower:
            result["context"] = "Child"

        # 2. Check Range hyphen/to (e.g., "13.5 - 17.5" or "13.5 to 17.5" or "4.0–10.0")
        range_match = re.search(r"([\d\.]+)\s*(?:-|–|to)\s*([\d\.]+)", clean)
        if range_match:
            try:
                result["low"] = float(range_match.group(1))
                result["high"] = float(range_match.group(2))
                return result
            except ValueError:
                pass

        # 3. Check upper threshold (e.g., "< 150", "<150", "up to 150", "<= 200")
        less_match = re.search(r"(?:<|<=|up\s*to)\s*([\d\.]+)", clean_lower)
        if less_match:
            try:
                result["high"] = float(less_match.group(1))
                return result
            except ValueError:
                pass

        # 4. Check lower threshold (e.g., "> 5", ">= 50", "more than 5")
        more_match = re.search(r"(?:>|>=|more\s*than)\s*([\d\.]+)", clean_lower)
        if more_match:
            try:
                result["low"] = float(more_match.group(1))
                return result
            except ValueError:
                pass

        return result
