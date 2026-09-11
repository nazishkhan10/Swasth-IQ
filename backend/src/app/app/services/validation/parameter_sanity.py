"""
Parameter Sanity Rules (Phase 5 Hardening).
Provides:
  1. Hard physiological limits per parameter (HbA1c 0-25%, Glucose 0-1000 mg/dL, etc.)
  2. Qualitative value detection (Negative, Trace, Reactive, etc.)
  3. Reference range sanity check (low < high, both valid)
  4. Clinical plausibility check (combined value+unit impossibilities)
"""

from dataclasses import dataclass
from typing import Optional, Dict, Tuple, Set

# ─────────────────────────────────────────────────────────────────────────────
# Hard physiological limits
# Values outside these ranges are physically impossible and indicate OCR error.
# All values are in the canonical unit for each parameter.
# ─────────────────────────────────────────────────────────────────────────────
HARD_LIMITS: Dict[str, Tuple[float, float]] = {
    "HBA1C":    (0.0,    25.0),      # %
    "GLU_FAST": (0.0,   1000.0),     # mg/dL
    "GLU_PP":   (0.0,   1500.0),     # mg/dL
    "GLU_RAND": (0.0,   1500.0),     # mg/dL
    "CREAT":    (0.0,    20.0),      # mg/dL
    "EGFR":     (0.0,   200.0),      # mL/min/1.73m²
    "BUN":      (0.0,   300.0),      # mg/dL
    "UREA":     (0.0,   500.0),      # mg/dL
    "URIC":     (0.0,    25.0),      # mg/dL
    "NA":       (100.0, 180.0),      # mmol/L
    "K":        (0.0,    15.0),      # mmol/L
    "CL":       (50.0,  150.0),      # mmol/L
    "TROP_I":   (0.0, 50000.0),      # pg/mL
    "HS_CRP":   (0.0,   500.0),      # mg/L
    "CHOL":     (0.0,   800.0),      # mg/dL
    "HDL":      (0.0,   200.0),      # mg/dL
    "LDL":      (0.0,   600.0),      # mg/dL
    "TRIG":     (0.0,  5000.0),      # mg/dL
    "VLDL":     (0.0,   300.0),      # mg/dL
    "HGB":      (0.0,    25.0),      # g/dL
    "RBC":      (0.0,    15.0),      # 10^6/µL
    "WBC":      (0.0,   500.0),      # 10^3/µL
    "PLT":      (0.0,  3000.0),      # 10^3/µL
    "TSH":      (0.0,   200.0),      # µIU/mL
    "VITD":     (0.0,   400.0),      # ng/mL
    "VITB12":   (0.0, 10000.0),      # pg/mL
}

# ─────────────────────────────────────────────────────────────────────────────
# Soft plausibility lower bounds (near-zero values that are biologically impossible)
# These catch OCR errors like "0.000001" that pass hard limits but are impossible.
# ─────────────────────────────────────────────────────────────────────────────
PLAUSIBILITY_MIN: Dict[str, float] = {
    "HBA1C":    2.0,     # HbA1c < 2% is impossible in living patients
    "CREAT":    0.1,     # Creatinine < 0.1 mg/dL is impossible
    "HGB":      2.0,     # Hgb < 2 g/dL is incompatible with life
    "PLT":      5.0,     # PLT < 5 × 10³/µL extremely rare, likely OCR error
    "WBC":      0.1,     # WBC < 0.1 × 10³/µL is impossible
    "NA":       110.0,   # Sodium < 110 incompatible with life
    "K":        1.5,     # Potassium < 1.5 mmol/L incompatible with life
    "TSH":      0.001,   # TSH < 0.001 µIU/mL — virtually impossible
}

# ─────────────────────────────────────────────────────────────────────────────
# Qualitative value strings
# ─────────────────────────────────────────────────────────────────────────────
QUALITATIVE_VALUES: Set[str] = {
    "negative", "neg", "–ve", "-ve", "not detected", "nd", "absent",
    "nil", "trace", "tr",
    "positive", "pos", "+ve", "reactive", "r",
    "present", "detected",
    "weak positive", "weak +ve", "weakly positive",
    "non reactive", "non-reactive", "nonreactive",
    "borderline", "equivocal",
    "indeterminate",
}

# Operator-prefixed qualitative (e.g., "<20" treated as qualitative for some params)
QUALITATIVE_PARAMS: Set[str] = {"TROP_I", "HS_CRP"}   # Often reported as "<0.04"


@dataclass
class SanityResult:
    valid: bool
    reason: str
    suggested_status: str = "INVALID_VALUE"


class ParameterSanityRules:
    """Hard physiological limit checker and qualitative value detector."""

    @classmethod
    def check_hard_limits(cls, param_code: str, value: float) -> SanityResult:
        """
        Returns SanityResult(valid=False) if value is outside physiological bounds.
        """
        code = param_code.upper().split("_V")[0]
        limits = HARD_LIMITS.get(code)
        if limits is None:
            return SanityResult(valid=True, reason="No hard limits defined")

        lo, hi = limits
        if value < lo or value > hi:
            return SanityResult(
                valid=False,
                reason=f"Value {value} outside hard physiological limit [{lo}, {hi}] for {code}",
                suggested_status="INVALID_VALUE"
            )

        # Soft plausibility check
        soft_min = PLAUSIBILITY_MIN.get(code)
        if soft_min is not None and value < soft_min:
            return SanityResult(
                valid=False,
                reason=f"Value {value} below biological plausibility minimum {soft_min} for {code}",
                suggested_status="INVALID_VALUE"
            )

        return SanityResult(valid=True, reason="Within physiological range")

    @classmethod
    def is_qualitative(cls, raw_value: str) -> bool:
        """Returns True if the raw OCR value is a qualitative string (not numeric)."""
        if not raw_value:
            return False
        clean = raw_value.strip().lower()
        # Direct match
        if clean in QUALITATIVE_VALUES:
            return True
        # Any qualitative keyword contained within
        for q in QUALITATIVE_VALUES:
            if q in clean and len(q) > 2:
                return True
        return False

    @classmethod
    def validate_report_reference(
        cls,
        ref_low: Optional[float],
        ref_high: Optional[float],
        param_code: Optional[str] = None
    ) -> SanityResult:
        """
        Checks if a report-supplied reference range is clinically sane.
        Returns valid=False if the range should be discarded and replaced with STANDARD_DATABASE.
        """
        # Both None → not a range, just missing
        if ref_low is None and ref_high is None:
            return SanityResult(valid=False, reason="Both bounds missing")

        # If both present: low must be less than high
        if ref_low is not None and ref_high is not None:
            if ref_low >= ref_high:
                return SanityResult(
                    valid=False,
                    reason=f"Reference range invalid: low ({ref_low}) >= high ({ref_high})",
                    suggested_status="INVALID_VALUE"
                )
            if ref_low < 0:
                return SanityResult(
                    valid=False,
                    reason=f"Reference range invalid: low ({ref_low}) is negative",
                )

        # Cross-check against hard limits if param_code known
        if param_code:
            code = param_code.upper().split("_V")[0]
            limits = HARD_LIMITS.get(code)
            if limits:
                lo, hi = limits
                if ref_low is not None and ref_low > hi:
                    return SanityResult(
                        valid=False,
                        reason=f"Report ref_low {ref_low} exceeds hard physiological maximum {hi}"
                    )
                if ref_high is not None and ref_high > hi * 2:
                    return SanityResult(
                        valid=False,
                        reason=f"Report ref_high {ref_high} grossly exceeds physiological limit"
                    )

        return SanityResult(valid=True, reason="Reference range is sane")
