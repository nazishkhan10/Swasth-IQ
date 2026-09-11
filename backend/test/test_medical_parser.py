import io
import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

from app.services.parser.report_classifier import ReportClassifier
from app.services.parser.parameter_resolver import ParameterResolver
from app.services.parser.patient_parser import PatientParser
from app.services.parser.duplicate_resolver import DuplicateResolver
from app.services.parser.parser_rules import ParserRules
from app.services.parser.timeline_parser import TimelineParser

client = TestClient(app)


def _register_and_login() -> str:
    email = f"parser_user_{uuid.uuid4().hex[:8]}@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"name": "Parser Tester", "email": email, "password": "Password123!", "confirm_password": "Password123!"}
    )
    res = client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
    return res.json()["access_token"]


def get_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ── Unit Tests for Modular Parser Services ───────────────────────────────────

def test_report_classifier():
    assert ReportClassifier.classify("Complete Blood Count Hemoglobin Platelets WBC") == "CBC"
    assert ReportClassifier.classify("Liver Function Test SGPT SGOT Bilirubin Albumin") == "LFT"
    assert ReportClassifier.classify("Kidney Function Serum Creatinine Blood Urea Uric Acid") == "KFT"
    assert "Mixed Panel" in ReportClassifier.classify("COMPREHENSIVE METABOLIC PROFILE & TSH")
    assert ReportClassifier.classify("Swasth-IQ LONGITUDINAL PATIENT TRACKING REPORT [VISIT 1]") == "Longitudinal Patient Tracking Report"


def test_timeline_parser_multi_visit():
    sample_text = """Swasth-IQ LONGITUDINAL PATIENT TRACKING REPORT

Patient ID : PAT-00842
Patient Name : Aris Thorne
Tracking Period: 2024-06-18 to 2026-06-12 (24 Months)
Total Visits : 4 Diagnostic Encounters

[VISIT 1] Baseline Encounter - 2024-06-19

Facility : Metro General Diagnostics
HbA1c : 6.8 % (Elevated)
FGlucose : 122 mg/dl (Elevated)
Total Chol : 218 mg/dl (Borderline)
Creatinine : 1.18 mg/dl (Normal)
Vit D : 22.0 ng/ml (Insufficient)
Health Score : 74/100 (Moderate Risk)

[VISIT 2] Follow-Up Encounter - 2025-01-14

Facility : PathQuest Precision Labs
HbA1c : 7.4 % (Worsening)
FGlucose : 146 mg/dl (Elevated)
Total Chol : 225 mg/dl (High)

[VISIT 3] Acute Escalation - 2025-11-20

Facility : Apex Specialty Healthcare
HbA1c : 9.1 % (Critical Escalation)
Creatinine : 1.6 mg/dl (Renal Strain Elevated)

[VISIT 4] Current Evaluation - 2026-06-12

Facility : PathQuest Precision Labs
HbA1c : 8.4 % (Partial Improvement)
Creatinine : 1.48 mg/dl (Elevated)
"""

    pages = [{"page": 1, "text": sample_text}]
    extracted, warnings = TimelineParser.parse(pages)
    assert len(extracted) == 13

    visit_codes = [p["parameter_code"] for p in extracted]
    assert "HBA1C_V1" in visit_codes
    assert "HBA1C_V2" in visit_codes
    assert "HBA1C_V3" in visit_codes
    assert "HBA1C_V4" in visit_codes


def test_idempotent_parser_rerun():
    headers = get_headers(_register_and_login())

    report_text = """Swasth-IQ Diagnostics
COMPREHENSIVE METABOLIC PROFILE & TSH

PATIENT NAME: Aris Thorne
PATIENT ID: PAT-00042
AGE/SEX: 54 Yrs / Male
COLLECTION TIME: 2026-03-15 07:15 CST

TEST PARAMETER RESULT UNIT REFERENCE RANGE STATUS
HbA1c 8.4 % 4.0 - 5.6 CRITICAL_HIGH
eGFR (CKD-EPI 2021) 54 mL/min/1.73m2 > 60 LOW
Serum Creatinine 1.48 mg/dL < 60 HIGH
    """

    files = {"file": ("idempotency_test.txt", io.BytesIO(report_text.encode("utf-8")), "text/plain")}
    up_res = client.post("/api/v1/upload", files=files, headers=headers)
    assert up_res.status_code == 201
    report_id = up_res.json()["id"]

    # Run OCR first
    client.post(f"/api/v1/ocr/{report_id}", headers=headers)

    # Re-run parser 5 times sequentially to verify idempotency (no UNIQUE constraint errors)
    for run in range(5):
        parse_res = client.post(f"/api/v1/parser/{report_id}", headers=headers)
        assert parse_res.status_code == 200, f"Failed on run #{run+1}"
        p_data = parse_res.json()
        assert p_data["patient"]["patient_name"] == "Aris Thorne"
        assert p_data["total_parameters"] == 3


def test_longitudinal_tracking_full_api_flow():
    headers = get_headers(_register_and_login())

    longitudinal_text = """Swasth-IQ LONGITUDINAL PATIENT TRACKING REPORT

Patient ID : PAT-00842
Patient Name : Aris Thorne
Tracking Period: 2024-06-18 to 2026-06-12 (24 Months)
Total Visits : 4 Diagnostic Encounters

[VISIT 1] Baseline Encounter - 2024-06-19

Facility : Metro General Diagnostics
HbA1c : 6.8 % (Elevated)
FGlucose : 122 mg/dl (Elevated)
Total Chol : 218 mg/dl (Borderline)
Creatinine : 1.18 mg/dl (Normal)
Vit D : 22.0 ng/ml (Insufficient)
Health Score : 74/100 (Moderate Risk)

[VISIT 2] Follow-Up Encounter - 2025-01-14

Facility : PathQuest Precision Labs
HbA1c : 7.4 % (Worsening)
FGlucose : 146 mg/dl (Elevated)

[VISIT 3] Acute Escalation - 2025-11-20

Facility : Apex Specialty Healthcare
HbA1c : 9.1 % (Critical Escalation)

[VISIT 4] Current Evaluation - 2026-06-12

Facility : PathQuest Precision Labs
HbA1c : 8.4 % (Partial Improvement)
"""

    files = {"file": ("longitudinal_report.txt", io.BytesIO(longitudinal_text.encode("utf-8")), "text/plain")}
    up_res = client.post("/api/v1/upload", files=files, headers=headers)
    assert up_res.status_code == 201
    report_id = up_res.json()["id"]

    client.post(f"/api/v1/ocr/{report_id}", headers=headers)

    parse_res = client.post(f"/api/v1/parser/{report_id}", headers=headers)
    assert parse_res.status_code == 200
    p_data = parse_res.json()

    assert p_data["detected_report_type"] == "Longitudinal Patient Tracking Report"
    assert p_data["patient"]["patient_name"] == "Aris Thorne"
    assert p_data["patient"]["accession_number"] == "PAT-00842"
    assert p_data["total_parameters"] == 10
