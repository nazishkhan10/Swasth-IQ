"""
Organ System Classifier Engine (Phase 6).
Classifies validated parameters into 10 organ/system panels.
Computes independent 0-100 score, status, affected parameters, confidence,
and cross-organ dependency linkages.
"""

from typing import Dict, Any, List
from app.services.analysis.context import MedicalAnalysisContext


ORGAN_PANEL_MAP = {
    "Blood": ["HGB", "RBC", "WBC", "PLT", "HCT", "MCV", "MCH", "MCHC", "NEUT", "LYMPH", "EOS", "MONO", "BASO", "ABS_NEUT", "ABS_LYMPH", "ABS_EOS", "ABS_MONO", "RDW_CV", "RDW_SD", "PCT", "MPV", "PDW"],
    "Kidney": ["CREAT", "EGFR", "BUN", "UREA", "URIC", "K", "NA", "CL"],
    "Diabetes": ["HBA1C", "GLU_FAST", "GLU_RAND", "GLU_PP"],
    "Lipid": ["CHOL", "LDL", "HDL", "TRIG", "VLDL"],
    "Thyroid": ["TSH", "FT3", "FT4", "T3", "T4"],
    "Liver": ["ALT", "AST", "ALP", "BILI_TOT", "BILI_DIR", "ALB", "TP"],
    "Vitamin": ["VITD", "VITB12", "FOLATE"],
    "Inflammation": ["HS_CRP", "ESR"],
    "Electrolytes": ["K", "NA", "CL", "HCO3", "CA", "MG"],
    "Cardiac": ["TROP_I", "BNP", "CK_MB"]
}


class OrganSystemClassifier:

    @classmethod
    def classify(cls, ctx: MedicalAnalysisContext) -> Dict[str, Any]:
        params_by_code = {p.get("parameter_code"): p for p in ctx.validated_parameters if p.get("parameter_code")}

        panels = {}
        affected_organs = []

        for organ_name, codes in ORGAN_PANEL_MAP.items():
            matched_params = [params_by_code[c] for c in codes if c in params_by_code]
            if not matched_params:
                continue

            abnormal_count = 0
            critical_count = 0
            affected_param_names = []
            param_details = []
            conf_sum = 0.0

            for p in matched_params:
                status = (p.get("status") or "NORMAL").upper()
                conf_sum += p.get("validation_confidence", 0.9)
                param_display = p.get("parameter_name") or p.get("parameter_code")
                val = p.get("converted_value") if p.get("is_converted") else p.get("numeric_value")
                unit = p.get("canonical_unit") or p.get("normalized_unit") or p.get("unit") or ""

                param_details.append({
                    "name": param_display,
                    "code": p.get("parameter_code"),
                    "value": str(val if val is not None else p.get("raw_value", "")),
                    "unit": unit,
                    "status": status,
                    "ref_range": f"{p.get('ref_range_low', '')} - {p.get('ref_range_high', '')}".strip(" -")
                })

                if "CRITICAL" in status or status == "INVALID_VALUE":
                    critical_count += 1
                    abnormal_count += 1
                    affected_param_names.append(f"{param_display} ({status})")
                elif status in ["HIGH", "LOW", "MODERATE_HIGH", "MODERATE_LOW", "SEVERE_HIGH", "SEVERE_LOW"]:
                    abnormal_count += 1
                    affected_param_names.append(f"{param_display} ({status})")

            total_matched = len(matched_params)
            avg_conf = conf_sum / total_matched if total_matched > 0 else 0.90

            # Calculate independent 0-100 organ score
            panel_score = 100 - (critical_count * 35) - (abnormal_count * 15)
            panel_score = max(0, min(100, panel_score))

            if panel_score >= 85:
                status_label = "Optimal Health"
            elif panel_score >= 65:
                status_label = "Borderline / Mild Shift"
            elif panel_score >= 40:
                status_label = "Moderate Dysfunction"
            else:
                status_label = "Critical Dysfunction"

            if panel_score < 85:
                affected_organs.append(organ_name)

            panels[organ_name] = {
                "score": panel_score,
                "status": status_label,
                "total_parameters": total_matched,
                "abnormal_parameters_count": abnormal_count,
                "critical_parameters_count": critical_count,
                "affected_parameters": affected_param_names,
                "parameters": param_details,
                "confidence": round(avg_conf, 2)
            }


        # Build cross-organ dependency linkages
        dependency_graph = cls._build_organ_dependencies(affected_organs)

        return {
            "panels": panels,
            "affected_organs": affected_organs,
            "dependency_graph": dependency_graph
        }

    @classmethod
    def _build_organ_dependencies(cls, affected: List[str]) -> List[Dict[str, Any]]:
        links = []
        if "Diabetes" in affected and "Kidney" in affected:
            links.append({
                "source": "Diabetes", "target": "Kidney",
                "relationship": "Diabetic Nephropathy Risk",
                "clinical_description": "Chronic hyperglycemia induces glomerular hyperfiltration and microvascular renal damage."
            })
        if "Diabetes" in affected and "Lipid" in affected:
            links.append({
                "source": "Diabetes", "target": "Lipid",
                "relationship": "Diabetic Dyslipidemia",
                "clinical_description": "Insulin resistance increases hepatic VLDL secretion and small dense LDL particles."
            })
        if "Kidney" in affected and "Lipid" in affected:
            links.append({
                "source": "Kidney", "target": "Lipid",
                "relationship": "Cardiorenal-Metabolic Risk",
                "clinical_description": "Impaired renal clearance exacerbates atherogenic lipid retention."
            })
        if "Inflammation" in affected and "Lipid" in affected:
            links.append({
                "source": "Inflammation", "target": "Lipid",
                "relationship": "Vascular Atherogenesis",
                "clinical_description": "Systemic inflammation accelerates arterial macrophage cholesterol uptake."
            })
        return links
