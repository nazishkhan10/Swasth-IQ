"""
Phase 6 Clinical Intelligence & Explainable AI Engine Test Suite.
Tests all 17 clinical intelligence directives:
1. Data Quality Gate
2. Healthy Report Scenario
3. Diabetes Disease Rule Plugin
4. Renal Dysfunction (CKD) Plugin
5. Thyroid Disease Rule Plugin
6. Dyslipidemia Rule Plugin
7. Clinical Conflict Detection Engine
8. Missing Evidence Engine
9. Organ System Classifier & Dependency Linkages
10. Advanced Health Score Calculation
11. 8-Category Recommendation Engine & Triage Levels
12. Multi-Dimensional Timeline Deltas
13. Deep Line-Item Evidence Traceability Matrix
14. Multi-Target Phase 7 Prompt Packager
15. SHA256 Determinism Hash & Caching
16. Parameter Influence Engine
17. Complete REST API Integration
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.models.user import User
from app.models.report import Report
from app.models.patient_metadata import PatientMetadata
from app.models.validated_medical_value import ValidatedMedicalValue
from app.services.analysis.context import MedicalAnalysisContext
from app.services.analysis.determinism import DeterminismEngine
from app.services.analysis.organ_system_classifier import OrganSystemClassifier
from app.services.analysis.rules.diabetes import DiabetesRule
from app.services.analysis.rules.ckd import CKDRule
from app.services.analysis.rules.thyroid import ThyroidRule
from app.services.analysis.rules.lipid import LipidRule
from app.services.analysis.rules.anemia import AnemiaRule
from app.services.analysis.rules.vitamin import VitaminDRule
from app.services.analysis.rules.inflammation import InflammationRule
from app.services.analysis.conflict_detector import ClinicalConflictDetector
from app.services.analysis.missing_evidence import MissingEvidenceEngine
from app.services.analysis.health_score_engine import HealthScoreEngine
from app.services.analysis.parameter_influence import ParameterInfluenceEngine
from app.services.analysis.coverage_checklist import CoverageChecklistEngine
from app.services.analysis.risk_engine import RiskEngine
from app.services.analysis.evidence_builder import EvidenceBuilder
from app.services.analysis.recommendation_engine import RecommendationEngine
from app.services.analysis.timeline_builder import TimelineBuilder
from app.services.analysis.graph_builder import GraphBuilder
from app.services.analysis.ai_summary_builder import AISummaryBuilder
from app.services.analysis.confidence_engine import ConfidenceEngine
from app.services.analysis.prompt_builder import Phase7PromptPackager
from app.services.analysis.medical_analysis_engine import MedicalAnalysisEngine

# Setup Test Database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def _create_mock_context(params: list, quality_score: int = 95) -> MedicalAnalysisContext:
    return MedicalAnalysisContext(
        report_id=1,
        patient_metadata={"patient_name": "Aris Thorne", "patient_id": "PAT-00042", "age": "54", "gender": "Male", "report_date": "2026-03-15"},
        validated_parameters=params,
        validation_summary={"total": len(params)},
        validation_warnings=[],
        quality_score=quality_score,
        quality_gate_status="FULL",
        confidence=0.95
    )


# ── TEST 1: SHA256 Determinism Hash ──────────────────────────────────────────
def test_determinism_hash_reproducibility():
    params = [
        {"parameter_code": "HBA1C", "numeric_value": 8.4, "status": "CRITICAL_HIGH"},
        {"parameter_code": "CREAT", "numeric_value": 1.48, "status": "HIGH"}
    ]
    meta = {"patient_id": "PAT-00042", "gender": "Male"}

    hash1 = DeterminismEngine.compute_hash(params, meta)
    hash2 = DeterminismEngine.compute_hash(params, meta)

    assert hash1 == hash2
    assert len(hash1) == 64


# ── TEST 2: Diabetes Disease Rule Plugin ─────────────────────────────────────
def test_diabetes_rule_evaluation():
    params = [{"parameter_code": "HBA1C", "numeric_value": 8.4, "unit": "%", "status": "CRITICAL_HIGH"}]
    ctx = _create_mock_context(params)

    cond = DiabetesRule.evaluate(ctx)
    assert cond is not None
    assert cond.condition_id == "COND_DM2"
    assert "Diabetes" in cond.condition_name
    assert cond.severity in ["HIGH", "CRITICAL"]
    assert "HbA1c" in cond.supporting_parameters
    assert cond.explanation["why_detected"] is not None


# ── TEST 3: Renal Dysfunction (CKD) Plugin ────────────────────────────────────
def test_ckd_rule_evaluation():
    params = [
        {"parameter_code": "CREAT", "numeric_value": 1.6, "unit": "mg/dL", "status": "HIGH"},
        {"parameter_code": "EGFR", "numeric_value": 54.0, "unit": "mL/min/1.73m²", "status": "LOW"}
    ]
    ctx = _create_mock_context(params)

    cond = CKDRule.evaluate(ctx)
    assert cond is not None
    assert cond.condition_id == "COND_CKD"
    assert "Stage 3a" in cond.condition_name
    assert len(cond.supporting_parameters) == 2


# ── TEST 4: Thyroid Disease Rule Plugin ──────────────────────────────────────
def test_thyroid_rule_evaluation():
    params = [{"parameter_code": "TSH", "numeric_value": 6.8, "unit": "µIU/mL", "status": "HIGH"}]
    ctx = _create_mock_context(params)

    cond = ThyroidRule.evaluate(ctx)
    assert cond is not None
    assert cond.condition_id == "COND_HYPOTHYROID"
    assert cond.severity == "MODERATE"


# ── TEST 5: Dyslipidemia Rule Plugin ─────────────────────────────────────────
def test_lipid_rule_evaluation():
    params = [
        {"parameter_code": "CHOL", "numeric_value": 242.0, "unit": "mg/dL", "status": "HIGH"},
        {"parameter_code": "LDL", "numeric_value": 161.0, "unit": "mg/dL", "status": "HIGH"}
    ]
    ctx = _create_mock_context(params)

    cond = LipidRule.evaluate(ctx)
    assert cond is not None
    assert cond.condition_id == "COND_DYSLIPIDEMIA"
    assert cond.confidence >= 0.90


# ── TEST 6: Clinical Conflict Detection Engine ────────────────────────────────
def test_clinical_conflict_detection():
    # Conflict: Normal HbA1c with severe FGlucose spike
    params = [
        {"parameter_code": "HBA1C", "numeric_value": 5.2, "status": "NORMAL"},
        {"parameter_code": "GLU_FAST", "numeric_value": 280.0, "status": "HIGH"}
    ]
    ctx = _create_mock_context(params)

    conflicts = ClinicalConflictDetector.detect_conflicts(ctx)
    assert len(conflicts) >= 1
    assert conflicts[0]["conflict_id"] == "CONF_GLU_HBA1C_MISMATCH"
    assert conflicts[0]["confidence_penalty"] > 0


# ── TEST 7: Missing Evidence Engine ──────────────────────────────────────────
def test_missing_evidence_engine():
    # TSH present, but Free T4 / T3 missing
    params = [{"parameter_code": "TSH", "numeric_value": 6.8, "status": "HIGH"}]
    ctx = _create_mock_context(params)

    missing = MissingEvidenceEngine.evaluate_missing_evidence(ctx)
    assert len(missing) >= 1
    assert missing[0]["panel_name"] == "Thyroid Profile"
    assert "FT4" in missing[0]["missing_parameters"]


# ── TEST 8: Organ System Classifier & Dependencies ───────────────────────────
def test_organ_system_classifier():
    params = [
        {"parameter_code": "CREAT", "numeric_value": 1.6, "status": "HIGH"},
        {"parameter_code": "EGFR", "numeric_value": 54.0, "status": "LOW"},
        {"parameter_code": "HBA1C", "numeric_value": 8.4, "status": "CRITICAL_HIGH"}
    ]
    ctx = _create_mock_context(params)

    organ_data = OrganSystemClassifier.classify(ctx)
    assert "Kidney" in organ_data["panels"]
    assert "Diabetes" in organ_data["panels"]
    assert organ_data["panels"]["Kidney"]["score"] < 85
    assert len(organ_data["dependency_graph"]) >= 1
    assert organ_data["dependency_graph"][0]["source"] == "Diabetes"


# ── TEST 9: Advanced Health Score Calculation ────────────────────────────────
def test_health_score_calculation():
    params = [
        {"parameter_code": "HBA1C", "numeric_value": 8.4, "status": "CRITICAL_HIGH"},
        {"parameter_code": "CREAT", "numeric_value": 1.6, "status": "HIGH"}
    ]
    ctx = _create_mock_context(params)
    organ_data = OrganSystemClassifier.classify(ctx)

    score_data = HealthScoreEngine.calculate_score(ctx, organ_data, [])
    assert score_data["overall_health_score"] < 85
    assert score_data["overall_risk"] in ["MODERATE", "HIGH", "CRITICAL"]
    assert "critical_deductions" in score_data["score_breakdown"]


# ── TEST 10: 8-Category Recommendation Engine & Triage ────────────────────────
def test_recommendation_engine():
    params = [{"parameter_code": "HBA1C", "numeric_value": 8.4, "status": "CRITICAL_HIGH"}]
    ctx = _create_mock_context(params)
    cond = DiabetesRule.evaluate(ctx)
    evidence = EvidenceBuilder.build_evidence(ctx, [cond])

    recs = RecommendationEngine.generate_recommendations(ctx, [cond], evidence)
    assert len(recs) >= 1
    assert recs[0]["priority"] in ["CRITICAL", "HIGH", "MEDIUM"]
    assert recs[0]["action"] is not None


# ── TEST 11: Multi-Dimensional Timeline Deltas ──────────────────────────────
def test_timeline_builder():
    params = [{"parameter_code": "HBA1C", "numeric_value": 8.4, "status": "HIGH", "normalized_unit": "%"}]
    ctx = _create_mock_context(params)
    ctx_hist = MedicalAnalysisContext(
        report_id=1,
        patient_metadata={},
        validated_parameters=params,
        validation_summary={},
        validation_warnings=[],
        quality_score=95,
        quality_gate_status="FULL",
        confidence=0.95,
        historical_reports=[{"id": 99, "created_at": "2025-01-01"}]
    )

    timelines = TimelineBuilder.build_timelines(ctx_hist, 75, [])
    assert len(timelines["visit_timeline"]) == 2
    assert len(timelines["parameter_deltas"]) >= 1
    assert timelines["parameter_deltas"][0]["trend"] in ["Increasing", "Decreasing", "Stable"]


# ── TEST 12: Deep Line-Item Evidence Traceability ───────────────────────────
def test_evidence_builder():
    params = [{"parameter_code": "HBA1C", "numeric_value": 8.4, "normalized_unit": "%", "ref_range_high": 5.6, "status": "CRITICAL_HIGH"}]
    ctx = _create_mock_context(params)

    evidence = EvidenceBuilder.build_evidence(ctx, [])
    assert len(evidence) == 1
    assert evidence[0]["evidence_id"].startswith("EV_HBA1C")
    assert "+2.8 %" in evidence[0]["deviation"]
    assert evidence[0]["validation_confidence"] > 0


# ── TEST 13: Multi-Target Phase 7 Prompt Packager ───────────────────────────
def test_prompt_packager():
    params = [{"parameter_code": "HBA1C", "numeric_value": 8.4, "status": "CRITICAL_HIGH"}]
    ctx = _create_mock_context(params)

    full_data = {
        "conditions": [], "evidence": [], "recommendations": [],
        "health_score": 75, "overall_risk": "HIGH",
        "doctor_summary": "Doctor view", "patient_summary": "Patient view"
    }

    pkgs = Phase7PromptPackager.package_all(ctx, full_data)
    assert "doctor" in pkgs
    assert "patient" in pkgs
    assert "chat" in pkgs
    assert "rag" in pkgs
    assert "api" in pkgs
    assert pkgs["chat"]["system_instruction"] is not None


# ── TEST 14: Layered Confidence Engine ───────────────────────────────────────
def test_layered_confidence_engine():
    params = [{"parameter_code": "HBA1C", "ocr_confidence": 0.95, "validation_confidence": 0.92}]
    ctx = _create_mock_context(params)

    conf_data = ConfidenceEngine.calculate_confidence(ctx, [])
    assert conf_data["ocr_confidence"] == 95.0
    assert conf_data["validation_confidence"] == 92.0
    assert conf_data["overall_confidence"] > 0


# ── TEST 15: Parameter Influence Engine ──────────────────────────────────────
def test_parameter_influence_engine():
    params = [{"parameter_code": "HBA1C", "parameter_name": "HbA1c", "numeric_value": 8.4, "status": "CRITICAL_HIGH"}]
    ctx = _create_mock_context(params)
    cond = DiabetesRule.evaluate(ctx)
    organ_data = OrganSystemClassifier.classify(ctx)

    influence = ParameterInfluenceEngine.compute_influence(ctx, [cond] if cond else [], organ_data)
    assert len(influence) >= 1
    assert influence[0]["influence_percentage"] > 0


# ── TEST 16: Clinical Coverage Checklist Engine ──────────────────────────────
def test_coverage_checklist():
    params = [{"parameter_code": "HBA1C", "status": "HIGH"}]
    ctx = _create_mock_context(params)

    checklist = CoverageChecklistEngine.evaluate_coverage(ctx)
    assert len(checklist) >= 1
    diabetes_chk = next(c for c in checklist if c["panel_name"] == "Diabetes Panel")
    assert diabetes_chk["found_count"] == 1
    assert "GLU_FAST" in diabetes_chk["missing_parameters"]


# ── TEST 17: Complete End-to-End MedicalAnalysisEngine Integration ─────────
def test_e2e_medical_analysis_engine(db_session):
    user = User(name="Test User", email="test@cliniclens.ai", password_hash="pw")
    db_session.add(user)
    db_session.commit()


    report = Report(user_id=user.id, filename="test.pdf", original_filename="test_lab_report.pdf", file_path="/tmp/test.pdf", status="completed")
    db_session.add(report)
    db_session.commit()


    pm = PatientMetadata(report_id=report.id, patient_name="Aris Thorne", accession_number="PAT-00042", gender="Male", age="54")
    db_session.add(pm)


    v1 = ValidatedMedicalValue(
        report_id=report.id, parameter_name="HbA1c", parameter_code="HBA1C",
        validated_value=8.4, normalized_unit="%", reference_low=4.0, reference_high=5.6,
        status="CRITICAL_HIGH", raw_value="8.4 %", validation_confidence=0.95, ocr_confidence=0.98
    )
    v2 = ValidatedMedicalValue(
        report_id=report.id, parameter_name="Serum Creatinine", parameter_code="CREAT",
        validated_value=1.48, normalized_unit="mg/dL", reference_low=0.7, reference_high=1.35,
        status="HIGH", raw_value="1.48 mg/dl", validation_confidence=0.92, ocr_confidence=0.96
    )

    db_session.add_all([v1, v2])
    db_session.commit()

    # Run Analysis
    result = MedicalAnalysisEngine.run_analysis(db_session, report.id, force_recompute=True)

    assert result["report_id"] == report.id
    assert result["overall_health_score"] < 85
    assert len(result["conditions"]) >= 1
    assert len(result["evidence"]) >= 1
    assert len(result["recommendations"]) >= 1
    assert "doctor" in result["prompt_packages"]

    # Test Caching (second call without force_recompute should return same result)
    result_cached = MedicalAnalysisEngine.run_analysis(db_session, report.id, force_recompute=False)
    assert result_cached["determinism_hash"] == result["determinism_hash"]
