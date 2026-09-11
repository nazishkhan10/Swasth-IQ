"""
Phase 4.1 Comprehensive Validation & Regression Test Suite.
Tests source independence, determinism, field-by-field extraction accuracy, unit normalization, reference range parsing,
alias resolution, negative inputs, and database idempotency.
"""

import io
import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

from app.services.parser.report_classifier import ReportClassifier
from app.services.parser.parameter_resolver import ParameterResolver
from app.services.parser.unit_normalizer import UnitNormalizer
from app.services.parser.value_parser import ValueParser
from app.services.parser.reference_range_parser import ReferenceRangeParser
from app.services.parser.patient_parser import PatientParser
from app.services.parser.duplicate_resolver import DuplicateResolver
from app.services.parser.parser_rules import ParserRules
from app.services.parser.timeline_parser import TimelineParser

client = TestClient(app)


def _register_and_login() -> str:
    email = f"val_user_{uuid.uuid4().hex[:8]}@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"name": "Validation Tester", "email": email, "password": "Password123!", "confirm_password": "Password123!"}
    )
    res = client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
    return res.json()["access_token"]


def get_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ── 1. Unit Normalization Tests ───────────────────────────────────────────────

def test_unit_normalization_rules():
    assert UnitNormalizer.normalize("mg/dl") == "mg/dL"
    assert UnitNormalizer.normalize("ng/ml") == "ng/mL"
    assert UnitNormalizer.normalize("uiu/ml") == "µIU/mL"
    assert UnitNormalizer.normalize("cells/cu.mm") == "cells/µL"
    assert UnitNormalizer.normalize("ml/min/1.73m2") == "mL/min/1.73m²"


# ── 2. Reference Range Parsing Tests ──────────────────────────────────────────

def test_reference_range_parsing_low_high():
    r1 = ReferenceRangeParser.parse("4.0 - 5.6")
    assert r1["low"] == 4.0 and r1["high"] == 5.6

    r2 = ReferenceRangeParser.parse("< 100")
    assert r2["low"] is None and r2["high"] == 100.0

    r3 = ReferenceRangeParser.parse("> 60")
    assert r3["low"] == 60.0 and r3["high"] is None


# ── 3. Alias Resolution Tests ─────────────────────────────────────────────────

def test_alias_resolution_coverage():
    assert ParameterResolver.resolve("Hb")["code"] == "HGB"
    assert ParameterResolver.resolve("HbA1c")["code"] == "HBA1C"
    assert ParameterResolver.resolve("Vit D")["code"] == "VITD"
    assert ParameterResolver.resolve("FGlucose")["code"] == "GLU_FAST"
    assert ParameterResolver.resolve("Serum Creatinine")["code"] == "CREAT"
    assert ParameterResolver.resolve("High-Sensitivity Troponin I")["code"] == "TROP_I"


# ── 4. Marcus Vance Emergency Panel Extraction ───────────────────────────────

def test_marcus_vance_emergency_panel():
    headers = get_headers(_register_and_login())

    report_text = """APEX SPECIALTY HEALTHCARE - EMERGENCY LABS
Department of Pathology & Critical Care Diagnostics

Patient Name    : Marcus Vance                       Barcode ID          : *HL-20260731-0099*
Patient ID      : PAT-00099                          Report Number       : RPT-2026-88412
Visit ID        : VST-99401 (Emergency Dept)         Sample Type         : Whole Blood / Serum
Age / Gender    : 61 Yrs / Male                      Collection Time     : 2026-07-31 08:00 EST

CRITICAL METABOLIC, RENAL & CARDIAC MARKER PANEL
TEST PARAMETER              RESULT     UNITS       REFERENCE RANGE    FLAG      METHODOLOGY
HbA1c                     11.4       %           4.0 - 5.6          CRITICAL  HPLC
Fasting Plasma Glucose     285        mg/dL       70 - 99            CRITICAL  Hexokinase
Serum Creatinine          3.85       mg/dL       0.74 - 1.35        CRITICAL  Jaffé Kinetic
Blood Urea Nitrogen (BUN) 68.2       mg/dL       7.0 - 20.0         CRITICAL  Urease-GLDH
eGFR (CKD-EPI 2021)       16         mL/min/1.73m2 > 60             CRITICAL  Calculated
Serum Potassium           6.2        mmol/L      3.5 - 5.1          CRITICAL  ISE Indirect
Serum Sodium              129        mmol/L      136 - 145          LOW       ISE Indirect
High-Sensitivity Troponin I 148.5    pg/mL       < 19.0             CRITICAL  ECLIA
hs-CRP                    18.4       mg/L        < 1.0              CRITICAL  Immunoturbidimetric
"""

    files = {"file": ("marcus_vance.txt", io.BytesIO(report_text.encode("utf-8")), "text/plain")}
    up_res = client.post("/api/v1/upload", files=files, headers=headers)
    assert up_res.status_code == 201
    report_id = up_res.json()["id"]

    client.post(f"/api/v1/ocr/{report_id}", headers=headers)
    parse_res = client.post(f"/api/v1/parser/{report_id}", headers=headers)
    assert parse_res.status_code == 200
    p_data = parse_res.json()

    assert p_data["patient"]["patient_name"] == "Marcus Vance"
    assert p_data["patient"]["age"] == "61 Years"
    assert p_data["patient"]["gender"] == "Male"
    assert p_data["patient"]["accession_number"] == "PAT-00099"
    assert p_data["total_parameters"] == 9

    codes = [p["parameter_code"] for p in p_data["parameters"]]
    assert "HBA1C" in codes
    assert "GLU_FAST" in codes
    assert "CREAT" in codes
    assert "BUN" in codes
    assert "EGFR" in codes
    assert "K" in codes
    assert "NA" in codes
    assert "TROP_I" in codes
    assert "HS_CRP" in codes


# ── 5. Parser Determinism Test ────────────────────────────────────────────────

def test_parser_determinism():
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

    # Source 1: TXT file upload
    files1 = {"file": ("source1.txt", io.BytesIO(report_text.encode("utf-8")), "text/plain")}
    up1 = client.post("/api/v1/upload", files=files1, headers=headers)
    r_id1 = up1.json()["id"]
    client.post(f"/api/v1/ocr/{r_id1}", headers=headers)
    p_data1 = client.post(f"/api/v1/parser/{r_id1}", headers=headers).json()

    # Source 2: Second upload of identical content
    files2 = {"file": ("source2.txt", io.BytesIO(report_text.encode("utf-8")), "text/plain")}
    up2 = client.post("/api/v1/upload", files=files2, headers=headers)
    r_id2 = up2.json()["id"]
    client.post(f"/api/v1/ocr/{r_id2}", headers=headers)
    p_data2 = client.post(f"/api/v1/parser/{r_id2}", headers=headers).json()

    # Verify identical extracted fields
    assert p_data1["detected_report_type"] == p_data2["detected_report_type"]
    assert p_data1["total_parameters"] == p_data2["total_parameters"]
    assert p_data1["patient"]["patient_name"] == p_data2["patient"]["patient_name"]

    params1 = [(p["parameter_code"], p["value"], p["unit"], p["reference_range"]) for p in p_data1["parameters"]]
    params2 = [(p["parameter_code"], p["value"], p["unit"], p["reference_range"]) for p in p_data2["parameters"]]
    assert params1 == params2


# ── 6. Negative Tests & Crash Prevention ─────────────────────────────────────

def test_negative_inputs_crash_prevention():
    headers = get_headers(_register_and_login())

    # Case A: Random / Malformed text
    malformed_text = "This is a random grocery list: Apples, Bananas, Milk."
    files_a = {"file": ("malformed.txt", io.BytesIO(malformed_text.encode("utf-8")), "text/plain")}
    up_a = client.post("/api/v1/upload", files=files_a, headers=headers)
    r_id_a = up_a.json()["id"]
    client.post(f"/api/v1/ocr/{r_id_a}", headers=headers)
    res_a = client.post(f"/api/v1/parser/{r_id_a}", headers=headers)
    assert res_a.status_code == 200
    assert res_a.json()["total_parameters"] == 0
    assert res_a.json()["status"] == "no_data"


# ── 7. Database Idempotency Test ──────────────────────────────────────────────

def test_database_idempotency():
    headers = get_headers(_register_and_login())
    report_text = "Patient: Aris Thorne\nHbA1c: 8.4 %\n"
    files = {"file": ("idempotent.txt", io.BytesIO(report_text.encode("utf-8")), "text/plain")}
    up = client.post("/api/v1/upload", files=files, headers=headers)
    r_id = up.json()["id"]
    client.post(f"/api/v1/ocr/{r_id}", headers=headers)

    for _ in range(10):
        res = client.post(f"/api/v1/parser/{r_id}", headers=headers)
        assert res.status_code == 200
