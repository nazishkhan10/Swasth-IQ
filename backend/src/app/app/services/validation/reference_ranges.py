"""
Standard Clinical Reference Database (Phase 5).
Provides fallback evidence-based reference ranges segmented by parameter code, age category, and gender.
Used ONLY when the medical report does not contain an explicit reference range.
"""

from typing import Dict, Any, Optional

# Standard reference range entries keyed by parameter code
# Each entry contains fallback ranges categorized by demographic groups
STANDARD_REFERENCE_RANGES: Dict[str, Dict[str, Any]] = {
    # ── Blood Sugar / Diabetes ────────────────────────────────────────────────
    "HBA1C": {
        "unit": "%",
        "default": {"low": 4.0, "high": 5.6, "text": "4.0 - 5.6 %"},
        "demographics": {
            "adult_male": {"low": 4.0, "high": 5.6, "text": "4.0 - 5.6 %"},
            "adult_female": {"low": 4.0, "high": 5.6, "text": "4.0 - 5.6 %"},
            "senior": {"low": 4.0, "high": 6.0, "text": "4.0 - 6.0 %"},
            "child": {"low": 4.0, "high": 5.5, "text": "4.0 - 5.5 %"}
        }
    },
    "GLU_FAST": {
        "unit": "mg/dL",
        "default": {"low": 70.0, "high": 99.0, "text": "70 - 99 mg/dL"},
        "demographics": {
            "adult_male": {"low": 70.0, "high": 99.0, "text": "70 - 99 mg/dL"},
            "adult_female": {"low": 70.0, "high": 99.0, "text": "70 - 99 mg/dL"},
            "senior": {"low": 70.0, "high": 105.0, "text": "70 - 105 mg/dL"},
            "child": {"low": 60.0, "high": 95.0, "text": "60 - 95 mg/dL"}
        }
    },
    "GLU_PP": {
        "unit": "mg/dL",
        "default": {"low": 70.0, "high": 140.0, "text": "< 140 mg/dL"}
    },
    "GLU_RAND": {
        "unit": "mg/dL",
        "default": {"low": 70.0, "high": 140.0, "text": "70 - 140 mg/dL"}
    },

    # ── KFT / Renal & Electrolytes ─────────────────────────────────────────────
    "CREAT": {
        "unit": "mg/dL",
        "default": {"low": 0.74, "high": 1.35, "text": "0.74 - 1.35 mg/dL"},
        "demographics": {
            "adult_male": {"low": 0.74, "high": 1.35, "text": "0.74 - 1.35 mg/dL"},
            "adult_female": {"low": 0.59, "high": 1.04, "text": "0.59 - 1.04 mg/dL"},
            "senior": {"low": 0.60, "high": 1.40, "text": "0.60 - 1.40 mg/dL"},
            "child": {"low": 0.30, "high": 0.70, "text": "0.30 - 0.70 mg/dL"}
        }
    },
    "BUN": {
        "unit": "mg/dL",
        "default": {"low": 7.0, "high": 20.0, "text": "7.0 - 20.0 mg/dL"},
        "demographics": {
            "adult_male": {"low": 8.0, "high": 24.0, "text": "8.0 - 24.0 mg/dL"},
            "adult_female": {"low": 6.0, "high": 21.0, "text": "6.0 - 21.0 mg/dL"},
            "senior": {"low": 8.0, "high": 23.0, "text": "8.0 - 23.0 mg/dL"}
        }
    },
    "EGFR": {
        "unit": "mL/min/1.73m²",
        "default": {"low": 60.0, "high": None, "text": "> 60 mL/min/1.73m²"}
    },
    "UREA": {
        "unit": "mg/dL",
        "default": {"low": 15.0, "high": 45.0, "text": "15.0 - 45.0 mg/dL"}
    },
    "URIC": {
        "unit": "mg/dL",
        "default": {"low": 3.5, "high": 7.2, "text": "3.5 - 7.2 mg/dL"},
        "demographics": {
            "adult_male": {"low": 3.5, "high": 7.2, "text": "3.5 - 7.2 mg/dL"},
            "adult_female": {"low": 2.6, "high": 6.0, "text": "2.6 - 6.0 mg/dL"}
        }
    },
    "NA": {
        "unit": "mmol/L",
        "default": {"low": 136.0, "high": 145.0, "text": "136 - 145 mmol/L"}
    },
    "K": {
        "unit": "mmol/L",
        "default": {"low": 3.5, "high": 5.1, "text": "3.5 - 5.1 mmol/L"}
    },
    "CL": {
        "unit": "mmol/L",
        "default": {"low": 98.0, "high": 107.0, "text": "98 - 107 mmol/L"}
    },

    # ── Cardiac Markers ────────────────────────────────────────────────────────
    "TROP_I": {
        "unit": "pg/mL",
        "default": {"low": None, "high": 19.0, "text": "< 19.0 pg/mL"}
    },
    "HS_CRP": {
        "unit": "mg/L",
        "default": {"low": None, "high": 1.0, "text": "< 1.0 mg/L"}
    },

    # ── Lipid Profile ──────────────────────────────────────────────────────────
    "CHOL": {
        "unit": "mg/dL",
        "default": {"low": None, "high": 200.0, "text": "< 200 mg/dL"}
    },
    "HDL": {
        "unit": "mg/dL",
        "default": {"low": 40.0, "high": None, "text": "> 40 mg/dL"},
        "demographics": {
            "adult_male": {"low": 40.0, "high": None, "text": "> 40 mg/dL"},
            "adult_female": {"low": 50.0, "high": None, "text": "> 50 mg/dL"}
        }
    },
    "LDL": {
        "unit": "mg/dL",
        "default": {"low": None, "high": 100.0, "text": "< 100 mg/dL"}
    },
    "TRIG": {
        "unit": "mg/dL",
        "default": {"low": None, "high": 150.0, "text": "< 150 mg/dL"}
    },
    "VLDL": {
        "unit": "mg/dL",
        "default": {"low": 5.0, "high": 30.0, "text": "5.0 - 30.0 mg/dL"}
    },

    # ── CBC ────────────────────────────────────────────────────────────────────
    "HGB": {
        "unit": "g/dL",
        "default": {"low": 13.5, "high": 17.5, "text": "13.5 - 17.5 g/dL"},
        "demographics": {
            "adult_male": {"low": 13.8, "high": 17.2, "text": "13.8 - 17.2 g/dL"},
            "adult_female": {"low": 12.1, "high": 15.1, "text": "12.1 - 15.1 g/dL"},
            "child": {"low": 11.0, "high": 14.5, "text": "11.0 - 14.5 g/dL"}
        }
    },
    "RBC": {
        "unit": "10^6/µL",
        "default": {"low": 4.5, "high": 5.9, "text": "4.5 - 5.9 10^6/µL"},
        "demographics": {
            "adult_male": {"low": 4.7, "high": 6.1, "text": "4.7 - 6.1 10^6/µL"},
            "adult_female": {"low": 4.2, "high": 5.4, "text": "4.2 - 5.4 10^6/µL"}
        }
    },
    "WBC": {
        "unit": "10^3/µL",
        "default": {"low": 4.5, "high": 11.0, "text": "4.5 - 11.0 10^3/µL"}
    },
    "PLT": {
        "unit": "10^3/µL",
        "default": {"low": 150.0, "high": 450.0, "text": "150 - 450 10^3/µL"}
    },

    # ── Thyroid ────────────────────────────────────────────────────────────────
    "TSH": {
        "unit": "µIU/mL",
        "default": {"low": 0.4, "high": 4.5, "text": "0.4 - 4.5 µIU/mL"}
    },

    # ── Vitamins ──────────────────────────────────────────────────────────────
    "VITD": {
        "unit": "ng/mL",
        "default": {"low": 30.0, "high": 100.0, "text": "30.0 - 100.0 ng/mL"}
    },
    "VITB12": {
        "unit": "pg/mL",
        "default": {"low": 200.0, "high": 900.0, "text": "200.0 - 900.0 pg/mL"}
    }
}


class ReferenceRangeService:
    """Retrieves standard reference range bounds by parameter code and demographic metadata."""

    @classmethod
    def get_fallback_reference(cls, param_code: str, age_str: Optional[str] = None, gender_str: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if not param_code or param_code not in STANDARD_REFERENCE_RANGES:
            return None

        entry = STANDARD_REFERENCE_RANGES[param_code]
        demographic_key = cls._determine_demographic_key(age_str, gender_str)

        if demographic_key and "demographics" in entry and demographic_key in entry["demographics"]:
            range_info = entry["demographics"][demographic_key]
        else:
            range_info = entry["default"]

        return {
            "low": range_info.get("low"),
            "high": range_info.get("high"),
            "text": range_info.get("text"),
            "unit": entry.get("unit"),
            "source": "STANDARD_DATABASE"
        }

    @classmethod
    def _determine_demographic_key(cls, age_str: Optional[str], gender_str: Optional[str]) -> Optional[str]:
        if not age_str and not gender_str:
            return None

        gender = (gender_str or "").lower()
        age_num = None
        if age_str:
            import re
            m = re.search(r"(\d+)", age_str)
            if m:
                age_num = int(m.group(1))

        if age_num is not None and age_num < 18:
            return "child"
        if age_num is not None and age_num >= 65:
            return "senior"
        if "female" in gender or gender == "f":
            return "adult_female"
        if "male" in gender or gender == "m":
            return "adult_male"

        return None
