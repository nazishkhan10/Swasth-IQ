"""
App Database Models Package.
Exports all SQLAlchemy models for automatic table creation.
"""

from app.database.base import Base
from app.models.user import User
from app.models.report import Report
from app.models.ocr_result import OCRResult
from app.models.medical_value import MedicalValue
from app.models.patient_metadata import PatientMetadata
from app.models.parse_warning import ParseWarning
from app.models.validated_medical_value import ValidatedMedicalValue
from app.models.medical_analysis import MedicalAnalysis
from app.models.chat import ChatMessage, ChatExecution

__all__ = [
    "Base",
    "User",
    "Report",
    "OCRResult",
    "MedicalValue",
    "PatientMetadata",
    "ParseWarning",
    "ValidatedMedicalValue",
    "MedicalAnalysis",
    "ChatMessage",
    "ChatExecution",
]
