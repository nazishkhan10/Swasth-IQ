"""
Parameter Alias Resolver (Phase 5 Hardening).
Maps all known OCR name variants, abbreviations, and synonyms to canonical parameter codes.
Ensures 'FBS', 'Fasting Blood Sugar', 'Glucose Fasting' all resolve to 'GLU_FAST'.
"""

from typing import Optional, Dict, List

# ─────────────────────────────────────────────────────────────────────────────
# Alias → Canonical Code map
# Keys are lowercase stripped aliases; values are canonical codes matching
# STANDARD_REFERENCE_RANGES keys.
# ─────────────────────────────────────────────────────────────────────────────
_ALIAS_MAP: Dict[str, str] = {
    # ── HbA1c ──────────────────────────────────────────────────────────────
    "hba1c": "HBA1C", "hb a1c": "HBA1C", "a1c": "HBA1C",
    "glycated haemoglobin": "HBA1C", "glycated hemoglobin": "HBA1C",
    "glycosylated hemoglobin": "HBA1C", "glycosylated haemoglobin": "HBA1C",
    "glycohaemoglobin": "HBA1C", "glycohemoglobin": "HBA1C",
    "haemoglobin a1c": "HBA1C", "hemoglobin a1c": "HBA1C",
    "hgba1c": "HBA1C",

    # ── Fasting Glucose ──────────────────────────────────────────────────
    "fasting blood sugar": "GLU_FAST", "fbs": "GLU_FAST",
    "fasting blood glucose": "GLU_FAST", "fbg": "GLU_FAST",
    "glucose fasting": "GLU_FAST", "fasting glucose": "GLU_FAST",
    "blood sugar fasting": "GLU_FAST", "blood glucose fasting": "GLU_FAST",
    "f. blood sugar": "GLU_FAST", "f.b.s": "GLU_FAST",
    "f blood glucose": "GLU_FAST",

    # ── Post-Prandial Glucose ────────────────────────────────────────────
    "post prandial blood sugar": "GLU_PP", "ppbs": "GLU_PP",
    "postprandial glucose": "GLU_PP", "2hr ppbs": "GLU_PP",
    "pp blood sugar": "GLU_PP", "pp glucose": "GLU_PP",
    "2h post glucose": "GLU_PP",

    # ── Random Glucose ───────────────────────────────────────────────────
    "random blood sugar": "GLU_RAND", "rbs": "GLU_RAND",
    "random glucose": "GLU_RAND", "blood sugar random": "GLU_RAND",
    "glucose random": "GLU_RAND", "casual glucose": "GLU_RAND",
    "glucose": "GLU_RAND",

    # ── Creatinine ───────────────────────────────────────────────────────
    "serum creatinine": "CREAT", "creatinine": "CREAT",
    "s. creatinine": "CREAT", "s creatinine": "CREAT",
    "creat": "CREAT", "blood creatinine": "CREAT",

    # ── eGFR ─────────────────────────────────────────────────────────────
    "egfr": "EGFR", "gfr": "EGFR",
    "estimated gfr": "EGFR", "estimated glomerular filtration rate": "EGFR",
    "egfr (ckd-epi)": "EGFR", "egfr (mdrd)": "EGFR",
    "egfr ckd-epi 2021": "EGFR", "ckd-epi egfr": "EGFR",
    "glomerular filtration rate": "EGFR",

    # ── BUN ──────────────────────────────────────────────────────────────
    "blood urea nitrogen": "BUN", "bun": "BUN",
    "serum urea nitrogen": "BUN",

    # ── Urea ─────────────────────────────────────────────────────────────
    "urea": "UREA", "serum urea": "UREA", "blood urea": "UREA",
    "s. urea": "UREA",

    # ── Uric Acid ────────────────────────────────────────────────────────
    "uric acid": "URIC", "serum uric acid": "URIC",
    "s. uric acid": "URIC", "sua": "URIC",

    # ── Sodium ───────────────────────────────────────────────────────────
    "sodium": "NA", "serum sodium": "NA", "s. sodium": "NA", "na+": "NA",

    # ── Potassium ────────────────────────────────────────────────────────
    "potassium": "K", "serum potassium": "K", "s. potassium": "K", "k+": "K",

    # ── Chloride ─────────────────────────────────────────────────────────
    "chloride": "CL", "serum chloride": "CL", "cl-": "CL",

    # ── Troponin I ───────────────────────────────────────────────────────
    "troponin i": "TROP_I", "cardiac troponin i": "TROP_I",
    "high-sensitivity troponin i": "TROP_I", "hs troponin i": "TROP_I",
    "hs-tni": "TROP_I", "ctni": "TROP_I", "trop i": "TROP_I",

    # ── hs-CRP ───────────────────────────────────────────────────────────
    "hs-crp": "HS_CRP", "high sensitivity crp": "HS_CRP",
    "high-sensitivity c-reactive protein": "HS_CRP", "hscrp": "HS_CRP",

    # ── Total Cholesterol ────────────────────────────────────────────────
    "total cholesterol": "CHOL", "cholesterol": "CHOL",
    "serum cholesterol": "CHOL", "t. cholesterol": "CHOL",
    "t cholesterol": "CHOL", "tc": "CHOL",

    # ── HDL ──────────────────────────────────────────────────────────────
    "hdl cholesterol": "HDL", "hdl": "HDL",
    "high density lipoprotein": "HDL", "hdl-c": "HDL",
    "good cholesterol": "HDL",

    # ── LDL ──────────────────────────────────────────────────────────────
    "ldl cholesterol": "LDL", "ldl": "LDL",
    "low density lipoprotein": "LDL", "ldl-c": "LDL",
    "bad cholesterol": "LDL",

    # ── Triglycerides ────────────────────────────────────────────────────
    "triglycerides": "TRIG", "triglyceride": "TRIG",
    "serum triglycerides": "TRIG", "tg": "TRIG", "trigs": "TRIG",

    # ── VLDL ─────────────────────────────────────────────────────────────
    "vldl cholesterol": "VLDL", "vldl": "VLDL",
    "very low density lipoprotein": "VLDL", "vldl-c": "VLDL",

    # ── Hemoglobin ───────────────────────────────────────────────────────
    "hemoglobin": "HGB", "haemoglobin": "HGB", "hgb": "HGB", "hb": "HGB",
    "serum hemoglobin": "HGB",

    # ── RBC ──────────────────────────────────────────────────────────────
    "rbc count": "RBC", "red blood cell count": "RBC",
    "red cell count": "RBC", "erythrocyte count": "RBC", "rbc": "RBC",

    # ── WBC ──────────────────────────────────────────────────────────────
    "wbc count": "WBC", "white blood cell count": "WBC",
    "leukocyte count": "WBC", "wbc": "WBC", "tlc": "WBC",
    "total leucocyte count": "WBC", "total wbc": "WBC",

    # ── Platelets ────────────────────────────────────────────────────────
    "platelet count": "PLT", "platelets": "PLT",
    "thrombocyte count": "PLT", "plt": "PLT", "plts": "PLT",

    # ── RBC Indices ──────────────────────────────────────────────────────
    "mean corpuscular volume": "MCV", "mcv": "MCV",
    "mean corpuscular hemoglobin": "MCH", "mch": "MCH", "mean cell haemoglobin": "MCH",
    "mean corpuscular hemoglobin concentration": "MCHC", "mchc": "MCHC", "mean cell haemoglobin con": "MCHC", "mean cell haemoglobin concentration": "MCHC",
    "hematocrit": "HCT", "pcv": "HCT", "packed cell volume": "HCT", "hct": "HCT",
    "neutrophils": "NEUT", "neutrophil": "NEUT", "neut": "NEUT",
    "lymphocytes": "LYMPH", "lymphocyte": "LYMPH", "lymph": "LYMPH",
    "eosinophils": "EO", "eosinophil": "EO", "eo": "EO", "eos": "EO",
    "monocytes": "MONO", "monocyte": "MONO", "mono": "MONO",
    "basophils": "BASO", "basophil": "BASO", "baso": "BASO",

    # ── TSH ──────────────────────────────────────────────────────────────
    "tsh": "TSH", "thyroid stimulating hormone": "TSH",
    "thyrotropin": "TSH", "s. tsh": "TSH",

    # ── Vitamin D ────────────────────────────────────────────────────────
    "vitamin d": "VITD", "vit d": "VITD", "vitamin d3": "VITD",
    "25-oh vitamin d": "VITD", "25 hydroxy vitamin d": "VITD",
    "25-hydroxyvitamin d": "VITD", "25(oh)d": "VITD",
    "25 oh vit d": "VITD",

    # ── Vitamin B12 ──────────────────────────────────────────────────────
    "vitamin b12": "VITB12", "vit b12": "VITB12", "b12": "VITB12",
    "cobalamin": "VITB12", "cyanocobalamin": "VITB12",
    "serum vitamin b12": "VITB12",
}

# Pre-compute sorted alias list (longest first to avoid partial matches)
_SORTED_ALIASES: List[str] = sorted(_ALIAS_MAP.keys(), key=len, reverse=True)

# Canonical code set for fast lookup
_CANONICAL_CODES = set(_ALIAS_MAP.values())


class ParameterAliasResolver:
    """Resolves parameter names (including OCR variants) to canonical codes."""

    @classmethod
    def resolve(cls, parameter_name: str, existing_code: Optional[str] = None) -> Optional[str]:
        if existing_code and existing_code.upper() in _CANONICAL_CODES:
            return existing_code.upper()

        if parameter_name:
            resolved = cls._lookup(parameter_name)
            if resolved:
                return resolved

        return (existing_code or "UNKNOWN").upper()

    @classmethod
    def _lookup(cls, name: str) -> Optional[str]:
        clean = name.strip().lower()
        if clean in _ALIAS_MAP:
            return _ALIAS_MAP[clean]
        for alias in _SORTED_ALIASES:
            if alias in clean:
                return _ALIAS_MAP[alias]
        return None

    @classmethod
    def is_known_code(cls, code: str) -> bool:
        return code.upper() in _CANONICAL_CODES

    @classmethod
    def get_all_aliases(cls, canonical_code: str) -> List[str]:
        code = canonical_code.upper()
        return [alias for alias, c in _ALIAS_MAP.items() if c == code]
