"""
Base Disease Rule Interface & Data Structures (Phase 6).
Provides DetectedCondition dataclass and BaseDiseaseRule interface.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from app.services.analysis.context import MedicalAnalysisContext


@dataclass
class DetectedCondition:
    condition_id: str
    condition_name: str
    severity: str  # CRITICAL, HIGH, MODERATE, LOW, MILD
    confidence: float  # 0.0 to 1.0
    supporting_parameters: List[str]
    contradicting_parameters: List[str] = field(default_factory=list)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    explanation: Dict[str, str] = field(default_factory=dict)  # why_detected, why_confidence, etc.
    recommendation_ids: List[str] = field(default_factory=list)
    clinical_flags: Dict[str, bool] = field(default_factory=dict)


class BaseDiseaseRule:
    rule_id: str = "BASE"
    rule_name: str = "Base Disease Rule"
    version: str = "1.0.0"
    priority: str = "MEDIUM"
    supported_parameters: List[str] = []

    @classmethod
    def evaluate(cls, ctx: MedicalAnalysisContext) -> Optional[DetectedCondition]:
        raise NotImplementedError
