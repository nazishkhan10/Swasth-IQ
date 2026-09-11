"""
Critical Value Rule Engine (Phase 5).
Evaluates numeric lab values against life-threatening safety thresholds.
Thresholds based on ADA, KDIGO, ACC/AHA, and ACB guidelines.
Never diagnoses; purely performs threshold classification.
"""

from typing import Dict, Any, Optional


class CriticalRulesEngine:
    """Evaluates parameter values against critical safety threshold boundaries."""

    @classmethod
    def evaluate(cls, param_code: str, val: float) -> Optional[Dict[str, Any]]:
        if not param_code or val is None:
            return None

        code = param_code.upper().split("_V")[0]  # Support timeline params e.g. HBA1C_V1 → HBA1C

        # 1. Glycated Hemoglobin (HbA1c) — ADA critical thresholds
        if code == "HBA1C":
            if val >= 9.0:
                return {"status": "CRITICAL_HIGH", "severity": "CRITICAL",
                        "reason": f"Severely uncontrolled diabetes — immediate intervention required (HbA1c {val}% ≥ 9.0%)"}
            elif val >= 8.0:
                return {"status": "CRITICAL_HIGH", "severity": "CRITICAL",
                        "reason": f"Critically elevated HbA1c indicating therapy failure (HbA1c {val}% ≥ 8.0%)"}

        # 2. Fasting / Random / Post-prandial Glucose — ADA
        elif code in ["GLU_FAST", "GLU_RAND", "GLU_PP"]:
            if val >= 400.0:
                return {"status": "CRITICAL_HIGH", "severity": "CRITICAL",
                        "reason": f"Hyperglycaemic crisis / DKA threshold (Glucose {val} mg/dL ≥ 400)"}
            elif val >= 300.0:
                return {"status": "CRITICAL_HIGH", "severity": "CRITICAL",
                        "reason": f"Severe hyperglycaemic emergency (Glucose {val} mg/dL ≥ 300)"}
            elif val <= 50.0:
                return {"status": "CRITICAL_LOW", "severity": "CRITICAL",
                        "reason": f"Severe hypoglycaemic emergency (Glucose {val} mg/dL ≤ 50)"}
            elif val <= 70.0:
                return {"status": "CRITICAL_LOW", "severity": "CRITICAL",
                        "reason": f"Hypoglycaemia — immediate glucose administration required (Glucose {val} mg/dL ≤ 70)"}

        # 3. Serum Creatinine — KDIGO AKI thresholds
        elif code == "CREAT":
            if val >= 3.0:
                return {"status": "CRITICAL_HIGH", "severity": "CRITICAL",
                        "reason": f"Severe acute kidney injury (Creatinine {val} mg/dL ≥ 3.0)"}
            elif val >= 2.0:
                return {"status": "CRITICAL_HIGH", "severity": "CRITICAL",
                        "reason": f"Significant renal impairment — monitor closely (Creatinine {val} mg/dL ≥ 2.0)"}

        # 4. eGFR — KDIGO CKD staging
        elif code == "EGFR":
            if val < 15.0:
                return {"status": "CRITICAL_LOW", "severity": "CRITICAL",
                        "reason": f"Kidney failure — Stage 5 CKD / dialysis threshold (eGFR {val} < 15 mL/min/1.73m²)"}
            elif val < 30.0:
                return {"status": "CRITICAL_LOW", "severity": "CRITICAL",
                        "reason": f"Stage 4 CKD — urgent nephrology referral required (eGFR {val} < 30 mL/min/1.73m²)"}

        # 5. Serum Potassium — ACC/AHA
        elif code == "K":
            if val >= 6.5:
                return {"status": "CRITICAL_HIGH", "severity": "CRITICAL",
                        "reason": f"Severe hyperkalemia — cardiac arrest risk (Potassium {val} mmol/L ≥ 6.5)"}
            elif val >= 6.0:
                return {"status": "CRITICAL_HIGH", "severity": "CRITICAL",
                        "reason": f"Hyperkalemia — cardiac arrhythmia hazard (Potassium {val} mmol/L ≥ 6.0)"}
            elif val <= 2.5:
                return {"status": "CRITICAL_LOW", "severity": "CRITICAL",
                        "reason": f"Severe hypokalemia — respiratory/cardiac arrest risk (Potassium {val} mmol/L ≤ 2.5)"}
            elif val <= 2.8:
                return {"status": "CRITICAL_LOW", "severity": "CRITICAL",
                        "reason": f"Hypokalemia — muscle paralysis hazard (Potassium {val} mmol/L ≤ 2.8)"}

        # 6. Serum Sodium — hyponatraemia/hypernatraemia
        elif code == "NA":
            if val >= 160.0:
                return {"status": "CRITICAL_HIGH", "severity": "CRITICAL",
                        "reason": f"Severe hypernatraemia — neurological crisis risk (Sodium {val} mmol/L ≥ 160)"}
            elif val <= 120.0:
                return {"status": "CRITICAL_LOW", "severity": "CRITICAL",
                        "reason": f"Severe hyponatraemia — seizure/coma risk (Sodium {val} mmol/L ≤ 120)"}
            elif val <= 125.0:
                return {"status": "CRITICAL_LOW", "severity": "CRITICAL",
                        "reason": f"Hyponatraemia — cerebral oedema risk (Sodium {val} mmol/L ≤ 125)"}

        # 7. Cardiac Troponin I
        elif code == "TROP_I":
            if val >= 50.0:
                return {"status": "CRITICAL_HIGH", "severity": "CRITICAL",
                        "reason": f"Acute myocardial injury / ACS alert (Troponin I {val} pg/mL ≥ 50)"}

        # 8. High-Sensitivity CRP
        elif code == "HS_CRP":
            if val >= 20.0:
                return {"status": "CRITICAL_HIGH", "severity": "CRITICAL",
                        "reason": f"Severe systemic inflammation / sepsis alert (hs-CRP {val} mg/L ≥ 20)"}
            elif val >= 15.0:
                return {"status": "CRITICAL_HIGH", "severity": "CRITICAL",
                        "reason": f"High systemic inflammation (hs-CRP {val} mg/L ≥ 15)"}

        # 9. Hemoglobin — transfusion thresholds
        elif code == "HGB":
            if val <= 5.0:
                return {"status": "CRITICAL_LOW", "severity": "CRITICAL",
                        "reason": f"Life-threatening anemia — emergency transfusion required (Hb {val} g/dL ≤ 5.0)"}
            elif val <= 6.5:
                return {"status": "CRITICAL_LOW", "severity": "CRITICAL",
                        "reason": f"Severe anemia — transfusion threshold (Hb {val} g/dL ≤ 6.5)"}
            elif val >= 20.0:
                return {"status": "CRITICAL_HIGH", "severity": "CRITICAL",
                        "reason": f"Severe polycythaemia hyperviscosity (Hb {val} g/dL ≥ 20)"}

        # 10. Platelets
        elif code == "PLT":
            if val <= 20.0:
                return {"status": "CRITICAL_LOW", "severity": "CRITICAL",
                        "reason": f"Life-threatening thrombocytopenia — spontaneous intracranial bleed risk (PLT {val} 10³/µL ≤ 20)"}
            elif val <= 30.0:
                return {"status": "CRITICAL_LOW", "severity": "CRITICAL",
                        "reason": f"Severe thrombocytopenia — spontaneous bleeding hazard (PLT {val} 10³/µL ≤ 30)"}

        # 11. TSH — Thyroid storm / myxoedema
        elif code == "TSH":
            if val >= 20.0:
                return {"status": "CRITICAL_HIGH", "severity": "CRITICAL",
                        "reason": f"Severe hypothyroidism — myxoedema risk (TSH {val} µIU/mL ≥ 20)"}
            elif val < 0.01:
                return {"status": "CRITICAL_LOW", "severity": "CRITICAL",
                        "reason": f"Thyroid storm risk — suppressed TSH (TSH {val} µIU/mL < 0.01)"}

        # 12. Total Cholesterol — cardiovascular emergency
        elif code == "CHOL":
            if val >= 300.0:
                return {"status": "CRITICAL_HIGH", "severity": "CRITICAL",
                        "reason": f"Severe hypercholesterolaemia — familial hypercholesterolaemia risk (TC {val} mg/dL ≥ 300)"}

        # 13. LDL Cholesterol
        elif code == "LDL":
            if val >= 190.0:
                return {"status": "CRITICAL_HIGH", "severity": "CRITICAL",
                        "reason": f"Very high LDL — familial hypercholesterolaemia threshold (LDL {val} mg/dL ≥ 190)"}

        return None
