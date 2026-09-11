"""
Modular Disease Rule Registry.
Aggregates all clinical disease rule plugins.
"""

from typing import List, Type
from app.services.analysis.rules.base_rule import BaseDiseaseRule, DetectedCondition
from app.services.analysis.rules.diabetes import DiabetesRule
from app.services.analysis.rules.ckd import CKDRule
from app.services.analysis.rules.thyroid import ThyroidRule
from app.services.analysis.rules.lipid import LipidRule
from app.services.analysis.rules.anemia import AnemiaRule
from app.services.analysis.rules.vitamin import VitaminDRule
from app.services.analysis.rules.inflammation import InflammationRule

ALL_DISEASE_RULES: List[Type[BaseDiseaseRule]] = [
    DiabetesRule,
    CKDRule,
    ThyroidRule,
    LipidRule,
    AnemiaRule,
    VitaminDRule,
    InflammationRule,
]

__all__ = [
    "BaseDiseaseRule",
    "DetectedCondition",
    "DiabetesRule",
    "CKDRule",
    "ThyroidRule",
    "LipidRule",
    "AnemiaRule",
    "VitaminDRule",
    "InflammationRule",
    "ALL_DISEASE_RULES",
]
