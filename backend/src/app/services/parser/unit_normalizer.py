"""
Unit Normalizer Service.
Standardizes clinical measurement unit strings (including Indian Laboratory Units) into canonical healthcare units.
"""

import re
from typing import Optional

UNIT_MAP = {
    # Hemoglobin / Protein / Cholesterol
    r"^g/dl$|^gm/dl$|^g/100ml$|^g%$|^g/dl\.$": "g/dL",
    r"^g/l$|^gm/l$": "g/L",
    r"^mg/dl$|^mg%$|^mg/100ml$": "mg/dL",
    r"^mg/l$": "mg/L",

    # Cell Counts / Volumes / Filtration Rates (Supports Indian Lab Units & OCR variations)
    r"^cells/cu\.?mm$|^/cu\.?mm$|^/cumm$|^cumm$|^cells/mm3$|^cells/mm³$|^/mm3$|^/mm³$|^/ul$|^/µl$|^cells/ul$|^cells/µl$|^ul$|^µl$": "cells/µL",
    r"^10\^?6/µl$|^10\^?6/ul$|^million/cu\.?mm$|^million/cumm$|^mil-lion/cumm$|^mil-lion/cu\.?mm$|^mil/cu\.?mm$|^mil/cumm$|^millions/cumm$|^million/mm3$|^million/mm³$": "10^6/µL",
    r"^10\^?3/µl$|^10\^?3/ul$|^thou/cu\.?mm$|^thou/cumm$|^thousand/cumm$|^thousand/cu\.?mm$|^k/cumm$|^lakhs/cumm$|^lakh/cumm$|^lac/cumm$|^lacs/cumm$": "10^3/µL",
    r"^fl$|^femtoliters?$": "fL",
    r"^pg$|^picograms?$": "pg",

    # eGFR — handle both ASCII m2 and Unicode m² from OCR
    r"^ml/min/1\.73m\^?2$|^ml/min/1\.73m2$|^ml/min/1\.73m²$|^ml/min$": "mL/min/1.73m²",

    # Enzyme Activities / Hormones
    r"^u/l$|^iu/l$|^units/l$": "U/L",
    r"^uiu/ml$|^µiu/ml$|^miu/l$|^µiu/l$|^uiv/ml$": "µIU/mL",
    r"^ng/ml$|^ng/ml$": "ng/mL",
    r"^ng/dl$": "ng/dL",
    r"^pg/ml$": "pg/mL",
    r"^pg/ml$|^pg/l$": "pg/mL",
    r"^ug/dl$|^µg/dl$": "µg/dL",
    r"^mg/ml$": "mg/mL",

    # Percentages & Molar
    r"^%$|^percent$": "%",
    r"^mmol/l$": "mmol/L",
    r"^umol/l$|^µmol/l$": "µmol/L",
    r"^nmol/l$": "nmol/L",
    r"^pmol/l$": "pmol/L",
    r"^meq/l$": "mEq/L",
    r"^/100$|^score$": "/100",
}

class UnitNormalizer:
    """Normalizes raw OCR unit strings."""

    @classmethod
    def is_known_unit(cls, text: str) -> bool:
        if not text:
            return False
        clean = text.strip().lower()
        # Remove common spaces or hyphens inside unit strings (e.g. "Mil-lion / cumm")
        clean = clean.replace("-", "").replace(" ", "")
        for pattern in UNIT_MAP:
            if re.match(pattern, clean):
                return True
        canonical_outputs = set(UNIT_MAP.values())
        return text.strip() in canonical_outputs

    @classmethod
    def normalize(cls, raw_unit: Optional[str]) -> Optional[str]:
        if not raw_unit:
            return None

        clean = raw_unit.strip().lower()
        clean_no_space = clean.replace("-", "").replace(" ", "")

        if not clean:
            return None

        for pattern, canonical in UNIT_MAP.items():
            if re.match(pattern, clean) or re.match(pattern, clean_no_space):
                return canonical

        # Fallback return trimmed unit
        return raw_unit.strip()
