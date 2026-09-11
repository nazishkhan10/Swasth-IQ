"""
Numeric Value Parser (Phase 5 Hardening).
Normalizes OCR-extracted value strings into (numeric_value, operator) pairs.

Examples:
  "<20"     → NormalizedValue(value=20.0, operator="LT",    raw="<20")
  ">60"     → NormalizedValue(value=60.0, operator="GT",    raw=">60")
  "≈4.5"    → NormalizedValue(value=4.5,  operator="APPROX",raw="≈4.5")
  "~4.2"    → NormalizedValue(value=4.2,  operator="APPROX",raw="~4.2")
  "Approx 5"→ NormalizedValue(value=5.0,  operator="APPROX",raw="Approx 5")
  "8.4"     → NormalizedValue(value=8.4,  operator="EQ",    raw="8.4")
  "164"     → NormalizedValue(value=164.0,operator="EQ",    raw="164")
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class NormalizedValue:
    value: Optional[float]          # Extracted numeric value (None if non-numeric)
    operator: str                   # EQ | LT | LTE | GT | GTE | APPROX
    raw: str                        # Original OCR string
    is_numeric: bool                # True if a valid number was extracted
    note: str = ""


class NumericParser:
    """Parses OCR value strings into normalized (value, operator) pairs."""

    # Regex patterns ordered by specificity
    _PATTERNS = [
        # Approximate: ≈4.5, ~4.2, Approx 5, approximately 5
        (r"^(?:approx(?:imately)?\.?\s*|~|≈)\s*([\d,]+\.?\d*)\s*$", "APPROX"),
        # Less-than-or-equal: <=20, ≤20, =<20
        (r"^(?:<=|=<|≤)\s*([\d,]+\.?\d*)\s*$", "LTE"),
        # Greater-than-or-equal: >=60, =>60, ≥60
        (r"^(?:>=|=>|≥)\s*([\d,]+\.?\d*)\s*$", "GTE"),
        # Less-than: <20, < 20
        (r"^<\s*([\d,]+\.?\d*)\s*$", "LT"),
        # Greater-than: >60, > 60
        (r"^>\s*([\d,]+\.?\d*)\s*$", "GT"),
        # Plain number (possibly with commas as thousands separator)
        (r"^([\d,]+\.?\d*)\s*$", "EQ"),
        # Number with unit-like suffix: "8.4 %" — extract just the number
        (r"^([\d,]+\.?\d*)\s+[a-zA-Z%/µ°]", "EQ"),
    ]

    @classmethod
    def parse(cls, raw_value: str) -> NormalizedValue:
        """Parse a raw OCR value string into a NormalizedValue."""
        if not raw_value:
            return NormalizedValue(value=None, operator="EQ", raw="", is_numeric=False, note="Empty value")

        cleaned = raw_value.strip()

        for pattern, operator in cls._PATTERNS:
            m = re.match(pattern, cleaned, re.IGNORECASE)
            if m:
                num_str = m.group(1).replace(",", "")
                try:
                    val = float(num_str)
                    return NormalizedValue(
                        value=val, operator=operator,
                        raw=raw_value, is_numeric=True,
                        note=f"Parsed '{cleaned}' as {operator} {val}"
                    )
                except ValueError:
                    pass

        # No numeric match
        return NormalizedValue(
            value=None, operator="EQ", raw=raw_value, is_numeric=False,
            note=f"Non-numeric value: '{cleaned}'"
        )

    @classmethod
    def normalize_for_comparison(cls, parsed: NormalizedValue) -> Optional[float]:
        """
        Returns the best float value for range comparison.
        For LT/LTE: use the value directly (conservative — it's the stated threshold).
        For GT/GTE: same.
        For APPROX/EQ: use directly.
        """
        return parsed.value
