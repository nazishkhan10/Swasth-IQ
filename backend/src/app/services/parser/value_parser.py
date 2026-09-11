"""
Value Parser Service.
Extracts numeric values, floats, scientific notation, qualitative descriptors, and Indian lab notation.
"""

import re
from typing import Tuple, Optional

class ValueParser:
    """Extracts raw value strings and converts them to floating point representations when applicable."""

    QUALITATIVE_MAP = {
        "negative": 0.0,
        "nil": 0.0,
        "absent": 0.0,
        "normal": 0.0,
        "trace": 0.1,
        "positive": 1.0,
        "present": 1.0,
        "1+": 1.0,
        "2+": 2.0,
        "3+": 3.0,
        "4+": 4.0,
    }

    @classmethod
    def parse(cls, raw_val: str) -> Tuple[str, Optional[float]]:
        clean = raw_val.strip()
        if not clean:
            return "", None

        clean_lower = clean.lower()

        # 1. Check qualitative descriptors
        if clean_lower in cls.QUALITATIVE_MAP:
            return clean, cls.QUALITATIVE_MAP[clean_lower]

        # 2. Check Indian lab notation (e.g. "5.4 lakh", "2.8 million")
        lakh_match = re.search(r"([\d\.]+)\s*lakh", clean_lower)
        if lakh_match:
            try:
                num = float(lakh_match.group(1)) * 100000.0
                return clean, num
            except ValueError:
                pass

        million_match = re.search(r"([\d\.]+)\s*million", clean_lower)
        if million_match:
            try:
                num = float(million_match.group(1)) * 1000000.0
                return clean, num
            except ValueError:
                pass

        # 3. Check Scientific notation (e.g. "4.5 x 10^6" or "4.5x10^6")
        sci_match = re.search(r"([\d\.]+)\s*x\s*10\^?(\d+)", clean_lower)
        if sci_match:
            try:
                base = float(sci_match.group(1))
                exp = int(sci_match.group(2))
                return clean, base * (10 ** exp)
            except ValueError:
                pass

        # 4. Check prefixed numerical values (e.g. "<0.01", ">500", "<=15")
        pref_match = re.search(r"^[<>=]*\s*([\d\.]+)$", clean)
        if pref_match:
            try:
                num = float(pref_match.group(1))
                return clean, num
            except ValueError:
                pass

        # 5. Generic floating point regex search
        float_match = re.search(r"[-+]?\d*\.\d+|\d+", clean)
        if float_match:
            try:
                return clean, float(float_match.group(0))
            except ValueError:
                pass

        return clean, None
