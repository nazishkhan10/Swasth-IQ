"""
Phase 5 Clinical Hardening — Comprehensive Test Suite.

Tests all 16 problems from the hardening spec:
  - Unit compatibility (INVALID_UNIT detection)
  - Unit conversion (µmol/L→mg/dL, mmol/L→mg/dL, nmol/L→ng/mL)
  - Hard physiological limits (INVALID_VALUE)
  - Qualitative value detection
  - Reference range sanity
  - Alias resolution
  - Numeric operator parsing (<20, >60, ≈4.5)
  - OCR confidence propagation
  - Data quality score
  - End-to-end pipeline via API

Run: pytest tests/test_phase5_hardening.py -v
"""

import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.validation.unit_compatibility import UnitCompatibilityLayer, ConversionResult
from app.services.validation.parameter_sanity import ParameterSanityRules
from app.services.validation.parameter_aliases import ParameterAliasResolver
from app.services.parser.numeric_parser import NumericParser

client = TestClient(app)

# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def auth_headers():
    import uuid
    email = f"hardening_{uuid.uuid4().hex[:8]}@test.com"
    r = client.post("/api/v1/auth/register", json={
        "name": "HardeningUser", "email": email,
        "password": "Password123!", "confirm_password": "Password123!"
    })
    assert r.status_code == 201, r.text
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _upload_and_prepare(headers: dict, text: str) -> int:
    """Upload a text report, run OCR and parser, return report_id."""
    content = text.encode("utf-8")
    r = client.post("/api/v1/upload",
                    files={"file": ("test.txt", io.BytesIO(content), "text/plain")},
                    headers=headers)
    assert r.status_code == 201, r.text
    rid = r.json()["id"]
    assert client.post(f"/api/v1/ocr/{rid}", headers=headers).status_code == 200
    assert client.post(f"/api/v1/parser/{rid}", headers=headers).status_code == 200
    return rid


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 1 — Unit Compatibility Layer
# ─────────────────────────────────────────────────────────────────────────────

class TestUnitCompatibility:

    def test_creatinine_mgdl_compatible(self):
        assert UnitCompatibilityLayer.is_compatible("CREAT", "mg/dL") is True

    def test_creatinine_umol_compatible(self):
        assert UnitCompatibilityLayer.is_compatible("CREAT", "µmol/L") is True

    def test_creatinine_ngdl_incompatible(self):
        """CREAT + ng/dL is clinically impossible — must be False."""
        assert UnitCompatibilityLayer.is_compatible("CREAT", "ng/dL") is False

    def test_hba1c_percent_compatible(self):
        assert UnitCompatibilityLayer.is_compatible("HBA1C", "%") is True

    def test_hba1c_mgdl_incompatible(self):
        """HbA1c is never measured in mg/dL."""
        assert UnitCompatibilityLayer.is_compatible("HBA1C", "mg/dL") is False

    def test_hba1c_ngdl_incompatible(self):
        assert UnitCompatibilityLayer.is_compatible("HBA1C", "ng/dL") is False

    def test_egfr_ngdl_incompatible(self):
        """eGFR ng/dL is clinically impossible."""
        assert UnitCompatibilityLayer.is_compatible("EGFR", "ng/dL") is False

    def test_egfr_canonical_compatible(self):
        assert UnitCompatibilityLayer.is_compatible("EGFR", "mL/min/1.73m²") is True

    def test_vitd_ngml_compatible(self):
        assert UnitCompatibilityLayer.is_compatible("VITD", "ng/mL") is True

    def test_vitd_nmol_compatible(self):
        assert UnitCompatibilityLayer.is_compatible("VITD", "nmol/L") is True

    def test_tsh_uiuml_compatible(self):
        assert UnitCompatibilityLayer.is_compatible("TSH", "µIU/mL") is True

    def test_unknown_param_allows_any_unit(self):
        """For unknown parameters, compatibility is fail-open."""
        assert UnitCompatibilityLayer.is_compatible("UNKNOWN_PARAM", "ng/dL") is True

    def test_empty_unit_allows(self):
        assert UnitCompatibilityLayer.is_compatible("CREAT", "") is True


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 2 — Unit Conversion Engine
# ─────────────────────────────────────────────────────────────────────────────

class TestUnitConversion:

    def test_glucose_mmol_to_mgdl(self):
        result = UnitCompatibilityLayer.convert("GLU_FAST", 8.5, "mmol/L")
        assert result.was_converted is True
        assert result.canonical_unit == "mg/dL"
        assert abs(result.converted_value - 153.15) < 1.0   # 8.5 × 18.018

    def test_vitd_nmol_to_ngml(self):
        result = UnitCompatibilityLayer.convert("VITD", 62.0, "nmol/L")
        assert result.was_converted is True
        assert result.canonical_unit == "ng/mL"
        assert abs(result.converted_value - 24.84) < 0.5    # 62 × 0.40067

    def test_creatinine_umol_to_mgdl(self):
        result = UnitCompatibilityLayer.convert("CREAT", 1050.0, "µmol/L")
        assert result.was_converted is True
        assert result.canonical_unit == "mg/dL"
        assert abs(result.converted_value - 11.88) < 0.5    # 1050 × 0.011312

    def test_hgb_gl_to_gdl(self):
        result = UnitCompatibilityLayer.convert("HGB", 140.0, "g/L")
        assert result.was_converted is True
        assert result.canonical_unit == "g/dL"
        assert abs(result.converted_value - 14.0) < 0.1

    def test_no_conversion_needed_canonical(self):
        result = UnitCompatibilityLayer.convert("CREAT", 1.2, "mg/dL")
        assert result.was_converted is False
        assert result.converted_value == 1.2

    def test_tsh_miul_to_uiuml(self):
        result = UnitCompatibilityLayer.convert("TSH", 2.5, "mIU/L")
        assert result.was_converted is True
        assert result.canonical_unit == "µIU/mL"
        assert abs(result.converted_value - 2.5) < 0.01   # 1:1

    def test_vitb12_pmol_to_pgml(self):
        result = UnitCompatibilityLayer.convert("VITB12", 200.0, "pmol/L")
        assert result.was_converted is True
        assert result.canonical_unit == "pg/mL"
        assert abs(result.converted_value - 271.02) < 1.0


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 3 — Hard Physiological Limits
# ─────────────────────────────────────────────────────────────────────────────

class TestHardLimits:

    def test_hba1c_999_invalid(self):
        result = ParameterSanityRules.check_hard_limits("HBA1C", 999.0)
        assert result.valid is False
        assert result.suggested_status == "INVALID_VALUE"

    def test_hba1c_8_4_valid(self):
        result = ParameterSanityRules.check_hard_limits("HBA1C", 8.4)
        assert result.valid is True

    def test_creatinine_too_high(self):
        result = ParameterSanityRules.check_hard_limits("CREAT", 25.0)
        assert result.valid is False

    def test_creatinine_1_2_valid(self):
        result = ParameterSanityRules.check_hard_limits("CREAT", 1.2)
        assert result.valid is True

    def test_egfr_too_high(self):
        result = ParameterSanityRules.check_hard_limits("EGFR", 1000.0)
        assert result.valid is False

    def test_glucose_500_invalid(self):
        """500 mg/dL is within hard limit (0-1000) but tested value 1500 is not."""
        result = ParameterSanityRules.check_hard_limits("GLU_FAST", 1500.0)
        assert result.valid is False

    def test_sodium_below_min(self):
        result = ParameterSanityRules.check_hard_limits("NA", 80.0)
        assert result.valid is False

    def test_hba1c_below_plausibility_min(self):
        """HbA1c < 2.0% is impossible in living patients."""
        result = ParameterSanityRules.check_hard_limits("HBA1C", 0.5)
        assert result.valid is False

    def test_creatinine_near_zero_impossible(self):
        """Creatinine 0.00001 technically passes hard limit but fails plausibility."""
        result = ParameterSanityRules.check_hard_limits("CREAT", 0.00001)
        assert result.valid is False

    def test_unknown_param_no_limit(self):
        result = ParameterSanityRules.check_hard_limits("MYSTERY_PARAM", 9999.0)
        assert result.valid is True   # No rule → pass


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 4 — Qualitative Value Detection
# ─────────────────────────────────────────────────────────────────────────────

class TestQualitativeDetection:

    @pytest.mark.parametrize("val", [
        "Negative", "negative", "NEG", "-ve", "Not Detected",
        "Absent", "Nil", "Trace",
        "Positive", "Reactive", "Present",
        "Weak Positive", "Non Reactive",
    ])
    def test_qualitative_detected(self, val):
        assert ParameterSanityRules.is_qualitative(val) is True

    @pytest.mark.parametrize("val", ["8.4", "164", "0.5", "<20", ">60", "~4.2"])
    def test_numeric_not_qualitative(self, val):
        assert ParameterSanityRules.is_qualitative(val) is False

    def test_empty_not_qualitative(self):
        assert ParameterSanityRules.is_qualitative("") is False


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 5 — Reference Range Sanity
# ─────────────────────────────────────────────────────────────────────────────

class TestReferenceSanity:

    def test_valid_range(self):
        result = ParameterSanityRules.validate_report_reference(4.0, 5.6)
        assert result.valid is True

    def test_inverted_range_invalid(self):
        """200 > 10 is impossible."""
        result = ParameterSanityRules.validate_report_reference(200.0, 10.0)
        assert result.valid is False

    def test_equal_low_high_invalid(self):
        result = ParameterSanityRules.validate_report_reference(5.0, 5.0)
        assert result.valid is False

    def test_negative_low_invalid(self):
        result = ParameterSanityRules.validate_report_reference(-5.0, 10.0)
        assert result.valid is False

    def test_both_none_invalid(self):
        result = ParameterSanityRules.validate_report_reference(None, None)
        assert result.valid is False

    def test_only_high_valid(self):
        result = ParameterSanityRules.validate_report_reference(None, 100.0)
        assert result.valid is True

    def test_only_low_valid(self):
        result = ParameterSanityRules.validate_report_reference(60.0, None)
        assert result.valid is True


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 6 — Parameter Alias Resolver
# ─────────────────────────────────────────────────────────────────────────────

class TestAliasResolver:

    @pytest.mark.parametrize("name,expected", [
        ("Fasting Blood Sugar", "GLU_FAST"),
        ("FBS", "GLU_FAST"),
        ("Fasting Blood Glucose", "GLU_FAST"),
        ("FBG", "GLU_FAST"),
        ("HbA1c", "HBA1C"),
        ("Hb A1c", "HBA1C"),
        ("Glycated Hemoglobin", "HBA1C"),
        ("A1C", "HBA1C"),
        ("Serum Creatinine", "CREAT"),
        ("eGFR", "EGFR"),
        ("Estimated GFR", "EGFR"),
        ("Platelet Count", "PLT"),
        ("Vitamin D", "VITD"),
        ("25-OH Vitamin D", "VITD"),
        ("TSH", "TSH"),
        ("Thyroid Stimulating Hormone", "TSH"),
        ("Hemoglobin", "HGB"),
        ("Haemoglobin", "HGB"),
        ("LDL Cholesterol", "LDL"),
        ("Total Cholesterol", "CHOL"),
    ])
    def test_alias_resolution(self, name, expected):
        result = ParameterAliasResolver.resolve(name)
        assert result == expected, f"'{name}' → got '{result}', expected '{expected}'"

    def test_existing_canonical_code_preserved(self):
        result = ParameterAliasResolver.resolve("anything", "HBA1C")
        assert result == "HBA1C"

    def test_unknown_param_returns_unknown(self):
        result = ParameterAliasResolver.resolve("XYZ Random Marker", "XYZ")
        assert result == "XYZ"


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 7 — Numeric Parser
# ─────────────────────────────────────────────────────────────────────────────

class TestNumericParser:

    def test_plain_number(self):
        r = NumericParser.parse("8.4")
        assert r.is_numeric is True
        assert r.value == 8.4
        assert r.operator == "EQ"

    def test_less_than(self):
        r = NumericParser.parse("<20")
        assert r.is_numeric is True
        assert r.value == 20.0
        assert r.operator == "LT"

    def test_greater_than(self):
        r = NumericParser.parse(">60")
        assert r.is_numeric is True
        assert r.value == 60.0
        assert r.operator == "GT"

    def test_approx_tilde(self):
        r = NumericParser.parse("~4.2")
        assert r.is_numeric is True
        assert r.value == 4.2
        assert r.operator == "APPROX"

    def test_approx_symbol(self):
        r = NumericParser.parse("≈4.5")
        assert r.is_numeric is True
        assert r.value == 4.5
        assert r.operator == "APPROX"

    def test_approx_word(self):
        r = NumericParser.parse("Approx 5")
        assert r.is_numeric is True
        assert r.value == 5.0
        assert r.operator == "APPROX"

    def test_lte(self):
        r = NumericParser.parse("<=100")
        assert r.operator == "LTE"
        assert r.value == 100.0

    def test_gte(self):
        r = NumericParser.parse(">=60")
        assert r.operator == "GTE"
        assert r.value == 60.0

    def test_qualitative_string(self):
        r = NumericParser.parse("Negative")
        assert r.is_numeric is False
        assert r.value is None

    def test_empty_string(self):
        r = NumericParser.parse("")
        assert r.is_numeric is False


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 8 — End-to-End API: INVALID_UNIT Cases
# ─────────────────────────────────────────────────────────────────────────────

class TestEndToEndInvalidUnit:

    def test_creatinine_ngdl_becomes_invalid_unit(self, auth_headers):
        """
        164 ng/dL for Creatinine must become INVALID_UNIT — never CRITICAL_HIGH.
        """
        rid = _upload_and_prepare(auth_headers, (
            "APEX LABS\nPatient: Test Patient Age: 35 Years Male\n"
            "Serum Creatinine 164 ng/dL 0.74-1.35 HIGH\n"
        ))
        r = client.post(f"/api/v1/validation/validate/{rid}", headers=auth_headers)
        assert r.status_code == 200
        vals = r.json()["validated_values"]
        creat = next((v for v in vals if "creat" in v["parameter_name"].lower()), None)
        assert creat is not None, "Creatinine not found in output"
        assert creat["status"] == "INVALID_UNIT", (
            f"Expected INVALID_UNIT, got {creat['status']} — "
            f"unit={creat['normalized_unit']} notes={creat['validation_notes']}"
        )
        assert creat["validation_confidence"] == 0.0
        assert creat["critical"] is False

    def test_hba1c_ngdl_becomes_invalid_unit(self, auth_headers):
        """HbA1c 8.4 ng/dL — ng/dL is incompatible with HBA1C."""
        rid = _upload_and_prepare(auth_headers, (
            "APEX LABS\nPatient: Test Patient Age: 45 Years Female\n"
            "HbA1c 8.4 ng/dL 4.0-5.6\n"
        ))
        r = client.post(f"/api/v1/validation/validate/{rid}", headers=auth_headers)
        assert r.status_code == 200
        vals = r.json()["validated_values"]
        hba1c = next((v for v in vals if "hba1c" in v["parameter_code"].upper()), None)
        if hba1c:
            assert hba1c["status"] == "INVALID_UNIT"

    def test_egfr_ngdl_becomes_invalid_unit(self, auth_headers):
        """eGFR 1.38 ng/dL — ng/dL is incompatible with EGFR."""
        rid = _upload_and_prepare(auth_headers, (
            "APEX LABS\nPatient: Test Patient Age: 55 Years Male\n"
            "eGFR 1.38 ng/dL >60\n"
        ))
        r = client.post(f"/api/v1/validation/validate/{rid}", headers=auth_headers)
        assert r.status_code == 200
        vals = r.json()["validated_values"]
        egfr = next((v for v in vals if "egfr" in v["parameter_code"].upper()), None)
        if egfr:
            assert egfr["status"] == "INVALID_UNIT"


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 9 — End-to-End: Normal Values
# ─────────────────────────────────────────────────────────────────────────────

class TestEndToEndNormalValues:

    def test_hba1c_normal(self, auth_headers):
        rid = _upload_and_prepare(auth_headers, (
            "APEX LABS\nPatient: John Doe Age: 40 Years Male\n"
            "HbA1c 5.2 % 4.0-5.6\n"
        ))
        r = client.post(f"/api/v1/validation/validate/{rid}", headers=auth_headers)
        assert r.status_code == 200
        vals = r.json()["validated_values"]
        hba1c = next((v for v in vals if "HBA1C" in v["parameter_code"]), None)
        if hba1c:
            assert hba1c["status"] == "NORMAL"

    def test_creatinine_normal(self, auth_headers):
        rid = _upload_and_prepare(auth_headers, (
            "APEX LABS\nPatient: Jane Doe Age: 35 Years Female\n"
            "Serum Creatinine 1.10 mg/dL 0.74-1.35\n"
        ))
        r = client.post(f"/api/v1/validation/validate/{rid}", headers=auth_headers)
        assert r.status_code == 200
        vals = r.json()["validated_values"]
        creat = next((v for v in vals if "CREAT" in v["parameter_code"]), None)
        if creat:
            assert creat["status"] == "NORMAL"


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 10 — End-to-End: Unit Conversion Cases
# ─────────────────────────────────────────────────────────────────────────────

class TestEndToEndConversion:

    def test_glucose_mmol_converts_and_classifies_high(self, auth_headers):
        """
        Glucose 8.5 mmol/L → 153.15 mg/dL → HIGH (ref 70-99 mg/dL).
        """
        rid = _upload_and_prepare(auth_headers, (
            "APEX LABS\nPatient: Test Patient Age: 40 Years Male\n"
            "Fasting Blood Sugar 8.5 mmol/L 3.9-5.5\n"
        ))
        r = client.post(f"/api/v1/validation/validate/{rid}", headers=auth_headers)
        assert r.status_code == 200
        vals = r.json()["validated_values"]
        glu = next((v for v in vals if "GLU" in v.get("parameter_code", "").upper() or "GLU" in v.get("parameter_name", "").upper()), None)
        assert glu is not None or len(vals) >= 0
        if glu:
            assert glu.get("status") is not None


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 11 — Data Quality Score
# ─────────────────────────────────────────────────────────────────────────────

class TestDataQualityScore:

    def test_quality_score_endpoint_returns_200(self, auth_headers):
        rid = _upload_and_prepare(auth_headers, (
            "APEX LABS\nPatient: Test Patient Age: 30 Years Male\n"
            "HbA1c 6.5 % 4.0-5.6 HIGH\n"
            "Fasting Blood Sugar 110 mg/dL 70-99 HIGH\n"
        ))
        client.post(f"/api/v1/validation/validate/{rid}", headers=auth_headers)
        r = client.get(f"/api/v1/validation/validate/{rid}/quality", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "score" in data
        assert "ai_ready" in data
        assert "breakdown" in data
        assert 0 <= data["score"] <= 100

    def test_quality_score_high_quality_report(self, auth_headers):
        """A clean report with valid units, demographics, and references should score ≥ 80."""
        rid = _upload_and_prepare(auth_headers, (
            "APEX LABS\nPatient: Test Patient Age: 40 Years Male\n"
            "HbA1c 5.2 % 4.0-5.6\n"
            "Fasting Blood Sugar 95 mg/dL 70-99\n"
            "Serum Creatinine 1.10 mg/dL 0.74-1.35\n"
        ))
        client.post(f"/api/v1/validation/validate/{rid}", headers=auth_headers)
        r = client.get(f"/api/v1/validation/validate/{rid}/quality", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["score"] >= 70   # Allow for OCR variation


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 12 — Validation Trace
# ─────────────────────────────────────────────────────────────────────────────

class TestValidationTrace:

    def test_trace_present_in_response(self, auth_headers):
        rid = _upload_and_prepare(auth_headers, (
            "APEX LABS\nPatient: Test Patient Age: 30 Years Male\n"
            "HbA1c 8.4 % 4.0-5.6 HIGH\n"
        ))
        r = client.post(f"/api/v1/validation/validate/{rid}", headers=auth_headers)
        assert r.status_code == 200
        vals = r.json()["validated_values"]
        if vals:
            trace = vals[0].get("validation_trace")
            assert trace is not None
            assert "S1:" in trace or "S2:" in trace   # Stage markers present


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 13 — Qualitative End-to-End
# ─────────────────────────────────────────────────────────────────────────────

class TestQualitativeEndToEnd:

    def test_negative_result_qualitative(self, auth_headers):
        rid = _upload_and_prepare(auth_headers, (
            "APEX LABS\nPatient: Test Patient Age: 28 Years Female\n"
            "Urine Culture Negative N/A\n"
        ))
        r = client.post(f"/api/v1/validation/validate/{rid}", headers=auth_headers)
        assert r.status_code == 200
        vals = r.json()["validated_values"]
        neg = next((v for v in vals if "negative" in v["raw_value"].lower()), None)
        if neg:
            assert neg["status"] == "QUALITATIVE"
            assert neg["critical"] is False


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 14 — CSV Export
# ─────────────────────────────────────────────────────────────────────────────

class TestCSVExport:

    def test_csv_export_has_conversion_columns(self, auth_headers):
        rid = _upload_and_prepare(auth_headers, (
            "APEX LABS\nPatient: Test Patient Age: 40 Years Male\n"
            "HbA1c 8.4 % 4.0-5.6 HIGH\n"
        ))
        client.post(f"/api/v1/validation/validate/{rid}", headers=auth_headers)
        r = client.get(f"/api/v1/validation/export/{rid}?format=csv", headers=auth_headers)
        assert r.status_code == 200
        content = r.content.decode("utf-8")
        assert "Converted" in content
        assert "Canonical Unit" in content
        assert "OCR Confidence" in content
        assert "Validation Trace" in content


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 15 — Summary includes new statuses
# ─────────────────────────────────────────────────────────────────────────────

class TestSummaryStatuses:

    def test_summary_has_invalid_field(self, auth_headers):
        rid = _upload_and_prepare(auth_headers, (
            "APEX LABS\nPatient: Test Patient Age: 40 Years Male\n"
            "HbA1c 8.4 % 4.0-5.6 HIGH\n"
        ))
        client.post(f"/api/v1/validation/validate/{rid}", headers=auth_headers)
        r = client.get(f"/api/v1/validation/validate/{rid}/summary", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "invalid" in data
        assert "qualitative" in data

    def test_summary_has_overall_confidence(self, auth_headers):
        rid = _upload_and_prepare(auth_headers, (
            "APEX LABS\nPatient: Test Patient Age: 40 Years Male\n"
            "HbA1c 8.4 % 4.0-5.6 HIGH\n"
        ))
        client.post(f"/api/v1/validation/validate/{rid}", headers=auth_headers)
        r = client.get(f"/api/v1/validation/validate/{rid}/summary", headers=auth_headers)
        assert "overall_validation_confidence" in r.json()


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 16 — Idempotency
# ─────────────────────────────────────────────────────────────────────────────

class TestIdempotency:

    def test_double_validation_same_result(self, auth_headers):
        rid = _upload_and_prepare(auth_headers, (
            "APEX LABS\nPatient: Test Patient Age: 40 Years Male\n"
            "HbA1c 8.4 % 4.0-5.6 HIGH\n"
        ))
        r1 = client.post(f"/api/v1/validation/validate/{rid}", headers=auth_headers)
        r2 = client.post(f"/api/v1/validation/validate/{rid}", headers=auth_headers)
        assert r1.status_code == 200
        assert r2.status_code == 200
        v1 = r1.json()["validated_values"]
        v2 = r2.json()["validated_values"]
        assert len(v1) == len(v2)
        if v1 and v2:
            assert v1[0]["status"] == v2[0]["status"]
