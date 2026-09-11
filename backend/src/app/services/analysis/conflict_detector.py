"""
Clinical Conflict Detector Engine (Phase 6).
Detects biological contradictions between validated parameters
(e.g., Normal HbA1c with FGlucose > 300, Normal Creatinine with eGFR < 30).
Reduces analysis confidence and triggers manual review flags.
"""

from typing import List, Dict, Any
from app.services.analysis.context import MedicalAnalysisContext


class ClinicalConflictDetector:

    @classmethod
    def detect_conflicts(cls, ctx: MedicalAnalysisContext) -> List[Dict[str, Any]]:
        params = {p.get("parameter_code"): p for p in ctx.validated_parameters if p.get("parameter_code")}
        conflicts = []

        hba1c_p = params.get("HBA1C")
        glu_p = params.get("GLU_FAST") or params.get("GLU_RAND")

        if hba1c_p and glu_p:
            hba1c_val = hba1c_p.get("converted_value") if hba1c_p.get("is_converted") else hba1c_p.get("numeric_value")
            glu_val = glu_p.get("converted_value") if glu_p.get("is_converted") else glu_p.get("numeric_value")

            if hba1c_val and glu_val:
                # Conflict: Normal HbA1c (<5.7) with severe hyperglycemia (>250)
                if hba1c_val < 5.7 and glu_val >= 250.0:
                    conflicts.append({
                        "conflict_id": "CONF_GLU_HBA1C_MISMATCH",
                        "title": "Glycemic Mismatch Alert",
                        "parameters": ["HbA1c", "Fasting Glucose"],
                        "description": f"Normal HbA1c ({hba1c_val}%) conflicts with acute severe hyperglycemia ({glu_val} mg/dL).",
                        "clinical_significance": "May indicate acute glycemic spike, recent steroid therapy, or hemoglobinopathy.",
                        "confidence_penalty": 0.15,
                        "action_required": "Repeat fasting glucose and verify erythrocyte lifespan."
                    })

        creat_p = params.get("CREAT")
        egfr_p = params.get("EGFR")

        if creat_p and egfr_p:
            creat_val = creat_p.get("converted_value") if creat_p.get("is_converted") else creat_p.get("numeric_value")
            egfr_val = egfr_p.get("converted_value") if egfr_p.get("is_converted") else egfr_p.get("numeric_value")

            if creat_val and egfr_val:
                # Conflict: Normal creatinine (<1.0) with Stage 4/5 eGFR (<30)
                if creat_val <= 1.0 and egfr_val < 30.0:
                    conflicts.append({
                        "conflict_id": "CONF_RENAL_EGFR_CREAT_MISMATCH",
                        "title": "Renal Clearance Mismatch Alert",
                        "parameters": ["Serum Creatinine", "eGFR"],
                        "description": f"Normal Creatinine ({creat_val} mg/dL) conflicts with severely reduced eGFR ({egfr_val} mL/min/1.73m²).",
                        "clinical_significance": "May reflect extreme low muscle mass, amputation, or eGFR calculation formula error.",
                        "confidence_penalty": 0.20,
                        "action_required": "Perform Cystatin C clearance test for accurate eGFR verification."
                    })

        return conflicts
