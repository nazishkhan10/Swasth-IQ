"""
Unit Compatibility Layer (Phase 5 Hardening).
Provides:
  1. Per-parameter allowed unit lookup table
  2. Unit compatibility check (prevents CREAT 164 ng/dL → CRITICAL)
  3. Unit conversion engine (µmol/L→mg/dL, mmol/L→mg/dL, nmol/L→ng/mL, etc.)
"""

from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple, Any

# ─────────────────────────────────────────────────────────────────────────────
# Conversion result
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class ConversionResult:
    original_value: float
    original_unit: str
    converted_value: float
    canonical_unit: str
    conversion_factor: float
    was_converted: bool
    note: str = ""


# ─────────────────────────────────────────────────────────────────────────────
# Per-parameter unit compatibility table
# Structure: param_code → {
#   "canonical": canonical unit string (what the reference range is in),
#   "allowed": [list of normalized unit strings that are compatible],
#   "conversions": {from_unit → (factor, target_unit)}
#                  converted_value = original_value * factor
# }
# ─────────────────────────────────────────────────────────────────────────────
UNIT_COMPATIBILITY: Dict[str, Dict[str, Any]] = {

    "HBA1C": {
        "canonical": "%",
        "allowed": ["%", "mmol/mol"],
        "conversions": {
            "mmol/mol": (0.0915, "%"),   # mmol/mol ÷ 10.929 ≈ × 0.0915
        }
    },

    "GLU_FAST": {
        "canonical": "mg/dL",
        "allowed": ["mg/dL", "mmol/L"],
        "conversions": {
            "mmol/L": (18.018, "mg/dL"),   # mmol/L × 18.018 = mg/dL
        }
    },
    "GLU_PP": {
        "canonical": "mg/dL",
        "allowed": ["mg/dL", "mmol/L"],
        "conversions": {"mmol/L": (18.018, "mg/dL")}
    },
    "GLU_RAND": {
        "canonical": "mg/dL",
        "allowed": ["mg/dL", "mmol/L"],
        "conversions": {"mmol/L": (18.018, "mg/dL")}
    },

    "CREAT": {
        "canonical": "mg/dL",
        "allowed": ["mg/dL", "µmol/L"],
        "conversions": {
            "µmol/L": (0.011312, "mg/dL"),  # ÷ 88.4
        }
    },

    "EGFR": {
        "canonical": "mL/min/1.73m²",
        # Some labs report without body-surface-area denominator; accept mL/min as fallback
        "allowed": ["mL/min/1.73m²", "mL/min"],
        "conversions": {}
    },

    "BUN": {
        "canonical": "mg/dL",
        "allowed": ["mg/dL", "mmol/L"],
        "conversions": {
            "mmol/L": (2.8011, "mg/dL"),   # × 2.8011
        }
    },

    "UREA": {
        "canonical": "mg/dL",
        "allowed": ["mg/dL", "mmol/L"],
        "conversions": {
            "mmol/L": (6.006, "mg/dL"),    # × 6.006
        }
    },

    "URIC": {
        "canonical": "mg/dL",
        "allowed": ["mg/dL", "µmol/L", "mmol/L"],
        "conversions": {
            "µmol/L": (0.016812, "mg/dL"),  # ÷ 59.48
            "mmol/L": (16.812, "mg/dL"),
        }
    },

    "NA": {
        "canonical": "mmol/L",
        "allowed": ["mmol/L", "mEq/L"],
        "conversions": {
            "mEq/L": (1.0, "mmol/L"),   # 1:1 for monovalent
        }
    },

    "K": {
        "canonical": "mmol/L",
        "allowed": ["mmol/L", "mEq/L"],
        "conversions": {
            "mEq/L": (1.0, "mmol/L"),
        }
    },

    "CL": {
        "canonical": "mmol/L",
        "allowed": ["mmol/L", "mEq/L"],
        "conversions": {"mEq/L": (1.0, "mmol/L")}
    },

    "TROP_I": {
        "canonical": "pg/mL",
        "allowed": ["pg/mL", "ng/L"],
        "conversions": {
            "ng/L": (1.0, "pg/mL"),  # 1 ng/L = 1 pg/mL
        }
    },

    "HS_CRP": {
        "canonical": "mg/L",
        "allowed": ["mg/L", "mg/dL"],
        "conversions": {
            "mg/dL": (10.0, "mg/L"),   # × 10
        }
    },

    "CHOL": {
        "canonical": "mg/dL",
        "allowed": ["mg/dL", "mmol/L"],
        "conversions": {
            "mmol/L": (38.67, "mg/dL"),
        }
    },

    "HDL": {
        "canonical": "mg/dL",
        "allowed": ["mg/dL", "mmol/L"],
        "conversions": {"mmol/L": (38.67, "mg/dL")}
    },

    "LDL": {
        "canonical": "mg/dL",
        "allowed": ["mg/dL", "mmol/L"],
        "conversions": {"mmol/L": (38.67, "mg/dL")}
    },

    "TRIG": {
        "canonical": "mg/dL",
        "allowed": ["mg/dL", "mmol/L"],
        "conversions": {
            "mmol/L": (88.57, "mg/dL"),
        }
    },

    "VLDL": {
        "canonical": "mg/dL",
        "allowed": ["mg/dL", "mmol/L"],
        "conversions": {"mmol/L": (38.67, "mg/dL")}
    },

    "HGB": {
        "canonical": "g/dL",
        "allowed": ["g/dL", "g/L"],
        "conversions": {
            "g/L": (0.1, "g/dL"),    # ÷ 10
        }
    },

    "RBC": {
        "canonical": "10^6/µL",
        "allowed": ["10^6/µL", "cells/µL"],
        "conversions": {
            "cells/µL": (1e-6, "10^6/µL"),
        }
    },

    "WBC": {
        "canonical": "10^3/µL",
        "allowed": ["10^3/µL", "cells/µL"],
        "conversions": {
            "cells/µL": (0.001, "10^3/µL"),
        }
    },

    "PLT": {
        "canonical": "10^3/µL",
        "allowed": ["10^3/µL", "cells/µL"],
        "conversions": {
            "cells/µL": (0.001, "10^3/µL"),
        }
    },

    "TSH": {
        "canonical": "µIU/mL",
        "allowed": ["µIU/mL", "mIU/L"],
        "conversions": {
            "mIU/L": (1.0, "µIU/mL"),   # numerically equivalent
        }
    },

    "VITD": {
        "canonical": "ng/mL",
        "allowed": ["ng/mL", "nmol/L"],
        "conversions": {
            "nmol/L": (0.40067, "ng/mL"),   # ÷ 2.496
        }
    },

    "VITB12": {
        "canonical": "pg/mL",
        "allowed": ["pg/mL", "pmol/L"],
        "conversions": {
            "pmol/L": (1.3551, "pg/mL"),   # × 1.3551
        }
    },
}


class UnitCompatibilityLayer:
    """
    Clinical unit validation and conversion service.

    Usage:
        ok = UnitCompatibilityLayer.is_compatible("CREAT", "mg/dL")   # True
        ok = UnitCompatibilityLayer.is_compatible("CREAT", "ng/dL")   # False → INVALID_UNIT

        result = UnitCompatibilityLayer.convert("VITD", 62.0, "nmol/L")
        # result.converted_value = 24.84, result.canonical_unit = "ng/mL"
    """

    @classmethod
    def get_entry(cls, param_code: str) -> Optional[Dict]:
        return UNIT_COMPATIBILITY.get(param_code.upper().split("_V")[0])

    @classmethod
    def get_allowed_units(cls, param_code: str) -> List[str]:
        entry = cls.get_entry(param_code)
        return entry["allowed"] if entry else []

    @classmethod
    def get_canonical_unit(cls, param_code: str) -> Optional[str]:
        entry = cls.get_entry(param_code)
        return entry["canonical"] if entry else None

    @classmethod
    def is_compatible(cls, param_code: str, normalized_unit: str) -> bool:
        """
        Returns True if the normalized unit is clinically valid for this parameter.
        Returns True for unknown parameters (no entry) — conservative fail-open.
        Returns False only when we KNOW the unit is wrong.
        """
        if not param_code or not normalized_unit:
            return True   # can't determine → allow, emit warning separately

        entry = cls.get_entry(param_code)
        if not entry:
            return True   # unknown parameter → don't block

        unit_clean = normalized_unit.strip()
        # Case-insensitive match against allowed list
        allowed_lower = [u.lower() for u in entry["allowed"]]
        return unit_clean.lower() in allowed_lower

    @classmethod
    def convert(cls, param_code: str, value: float, normalized_unit: str) -> ConversionResult:
        """
        If the unit is compatible but not canonical, convert to canonical unit.
        If already canonical, returns as-is (was_converted=False).
        """
        entry = cls.get_entry(param_code)
        canonical = entry["canonical"] if entry else normalized_unit

        if not entry or normalized_unit.lower() == canonical.lower():
            return ConversionResult(
                original_value=value, original_unit=normalized_unit,
                converted_value=value, canonical_unit=canonical,
                conversion_factor=1.0, was_converted=False
            )

        conversions = entry.get("conversions", {})
        # Find conversion rule (case-insensitive key match)
        factor_info = None
        for from_unit, info in conversions.items():
            if normalized_unit.lower() == from_unit.lower():
                factor_info = info
                break

        if factor_info is None:
            # Compatible but no conversion rule — return as-is
            return ConversionResult(
                original_value=value, original_unit=normalized_unit,
                converted_value=value, canonical_unit=normalized_unit,
                conversion_factor=1.0, was_converted=False,
                note="No conversion rule; value used as-is"
            )

        factor, target_unit = factor_info
        converted = round(value * factor, 4)
        return ConversionResult(
            original_value=value, original_unit=normalized_unit,
            converted_value=converted, canonical_unit=target_unit,
            conversion_factor=factor, was_converted=True,
            note=f"{value} {normalized_unit} × {factor} = {converted} {target_unit}"
        )
