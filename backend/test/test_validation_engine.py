"""
Phase 5 Medical Validation Engine Test Suite.
Tests reference range priority rules, demographic lookups, critical value detection, unit normalization,
status calculation, API endpoints, and CSV/JSON dataset exports.
"""

import io
import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

from app.services.validation.reference_ranges import ReferenceRangeService
from app.services.validation.critical_rules import CriticalRulesEngine

client = TestClient(app)


def _register_and_login() -> str:
    email = f"val_eng_{uuid.uuid4().hex[:8]}@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"name": "Validation Suite User", "email": email, "password": "Password123!", "confirm_password": "Password123!"}
    )
    res = client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
    return res.json()["access_token"]


def get_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ── 1. Reference Ranges & Demographics Tests ──────────────────────────────────

def test_reference_range_demographics():
    # Adult Male Creatinine
    r_male = ReferenceRangeService.get_fallback_reference("CREAT", age_str="45 Years", gender_str="Male")
    assert r_male["low"] == 0.74 and r_male["high"] == 1.35

    # Adult Female Creatinine
    r_female = ReferenceRangeService.get_fallback_reference("CREAT", age_str="32 Years", gender_str="Female")
    assert r_female["low"] == 0.59 and r_female["high"] == 1.04

    # Child Creatinine
    r_child = ReferenceRangeService.get_fallback_reference("CREAT", age_str="8 Years", gender_str="Male")
    assert r_child["low"] == 0.30 and r_child["high"] == 0.70


# ── 2. Critical Rules Engine Tests ───────────────────────────────────────────

def test_critical_rules_engine():
    # HbA1c >= 10.0
    c1 = CriticalRulesEngine.evaluate("HBA1C", 11.4)
    assert c1 is not None and c1["status"] == "CRITICAL_HIGH"

    # Potassium >= 6.0
    c2 = CriticalRulesEngine.evaluate("K", 6.2)
    assert c2 is not None and c2["status"] == "CRITICAL_HIGH"

    # eGFR < 15
    c3 = CriticalRulesEngine.evaluate("EGFR", 12.0)
    assert c3 is not None and c3["status"] == "CRITICAL_LOW"

    # Troponin I >= 50
    c4 = CriticalRulesEngine.evaluate("TROP_I", 148.5)
    assert c4 is not None and c4["status"] == "CRITICAL_HIGH"

    # Normal value should not trigger critical alert
    c5 = CriticalRulesEngine.evaluate("CREAT", 1.1)
    assert c5 is None


# ── 3. Full End-to-End Validation Engine API Flow ────────────────────────────

def test_validation_engine_full_flow():
    headers = get_headers(_register_and_login())

    report_text = """APEX SPECIALTY HEALTHCARE - EMERGENCY LABS
Patient Name    : Marcus Vance                       Barcode ID          : *HL-20260731-0099*
Patient ID      : PAT-00099                          Report Number       : RPT-2026-88412
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

    # 1. Upload & OCR
    files = {"file": ("marcus_vance_val.txt", io.BytesIO(report_text.encode("utf-8")), "text/plain")}
    up_res = client.post("/api/v1/upload", files=files, headers=headers)
    assert up_res.status_code == 201
    r_id = up_res.json()["id"]

    client.post(f"/api/v1/ocr/{r_id}", headers=headers)
    client.post(f"/api/v1/parser/{r_id}", headers=headers)

    # 2. Run Phase 5 Validation Engine
    val_res = client.post(f"/api/v1/validation/validate/{r_id}", headers=headers)
    assert val_res.status_code == 200
    v_data = val_res.json()

    assert v_data["status"] == "completed"
    assert v_data["total_parameters"] == 9
    assert v_data["summary"]["critical"] >= 5

    # 3. Fetch Critical Alerts API Endpoint
    crit_res = client.get(f"/api/v1/validation/validate/{r_id}/critical", headers=headers)
    assert crit_res.status_code == 200
    crit_items = crit_res.json()
    assert len(crit_items) >= 5
    crit_codes = [c["parameter_code"] for c in crit_items]
    assert "HBA1C" in crit_codes
    assert "K" in crit_codes
    assert "TROP_I" in crit_codes

    # 4. Test Export API Endpoint (CSV Format)
    csv_res = client.get(f"/api/v1/validation/export/{r_id}?format=csv", headers=headers)
    assert csv_res.status_code == 200
    csv_text = csv_res.text
    assert "Parameter Name" in csv_text
    assert "Marcus Vance" not in csv_text  # CSV has medical parameters
    assert "HbA1c" in csv_text
    assert "11.4" in csv_text
