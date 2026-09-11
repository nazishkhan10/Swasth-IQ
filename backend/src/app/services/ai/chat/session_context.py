"""
Medical Session Context Dataclass (Phase 7 Chat Engine).
Immutable session container for Current Report, Patient, Visit, and Comparison Mode.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional


@dataclass
class MedicalSessionContext:
    """Session state wrapper for a chat turn."""
    report_id: int
    user_id: Optional[int]
    patient_name: str
    patient_id: Optional[str]
    age: Optional[str]
    gender: Optional[str]
    report_date: Optional[str]
    health_score: int
    risk_category: str
    validated_parameters: List[Dict[str, Any]]
    detected_conditions: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    organ_scores: Dict[str, Any]
    timelines: Dict[str, Any]
    evidence: List[Dict[str, Any]]
    quality_score: int
    comparison_mode: bool = False
