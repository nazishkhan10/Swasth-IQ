"""
MedicalAnalysisContext (Phase 6 Engine Input).
Immutable data container providing all Phase 5 validated data, patient metadata,
validation summaries, warnings, historical reports, and quality scores to all reasoning modules.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass(frozen=True)
class MedicalAnalysisContext:
    report_id: int
    patient_metadata: Dict[str, Any]
    validated_parameters: List[Dict[str, Any]]
    validation_summary: Dict[str, Any]
    validation_warnings: List[Dict[str, Any]]
    quality_score: int
    quality_gate_status: str  # FULL, WARNING, LIMITED, BLOCKED
    confidence: float
    report_type: str = "Diagnostic Lab Report"
    visit_number: int = 1
    historical_reports: List[Dict[str, Any]] = field(default_factory=list)
