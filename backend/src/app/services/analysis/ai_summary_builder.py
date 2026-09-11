"""
AI Dual Summary Builder Engine (Phase 6).
Generates two deterministic summaries assembled strictly from structured objects:
1. Doctor Summary: Formal medical nomenclature synthesis.
2. Patient Summary: Empathetic, clear, plain English overview.
"""

from typing import Dict, Any, List
from app.services.analysis.context import MedicalAnalysisContext


class AISummaryBuilder:

    @classmethod
    def build_summaries(cls, ctx: MedicalAnalysisContext, conditions: List[Any], risk_data: Dict[str, Any], recommendations: List[Dict[str, Any]]) -> Dict[str, str]:
        cond_names = [
            getattr(c, "condition_name", "") if hasattr(c, "condition_name") else c.get("condition_name")
            for c in conditions
        ]

        patient_name = ctx.patient_metadata.get("patient_name") or "Patient"

        # ── 1. Doctor Summary ──────────────────────────────────────────────────
        if cond_names:
            doc_summary = (
                f"Clinical Analysis for {patient_name}: Diagnostic evaluation identifies "
                f"{', '.join(cond_names)}. "
                f"Risk assessment indicates {risk_data.get('Metabolic Syndrome', {}).get('current_risk', 'MODERATE')} overall cardiometabolic burden. "
                f"Key management priority: {recommendations[0]['title'] if recommendations else 'Routine clinical follow-up'}. "
                f"Close monitoring of renal, glycemic, and lipid indicators is advised."
            )
        else:
            doc_summary = (
                f"Clinical Analysis for {patient_name}: All validated laboratory parameters operate within standard physiological reference boundaries. "
                f"No evidence of acute metabolic, renal, hematologic, or endocrine dysfunction."
            )

        # ── 2. Patient Summary ─────────────────────────────────────────────────
        if cond_names:
            pat_summary = (
                f"Hello {patient_name}. We reviewed your latest lab results. "
                f"Your report shows key areas that need attention: {', '.join(cond_names)}. "
                f"Our primary recommendation is to {recommendations[0]['action'] if recommendations else 'schedule a follow-up visit with your doctor'}. "
                f"Making small adjustments to your lifestyle and following up with your healthcare provider will help keep your health on track."
            )
        else:
            pat_summary = (
                f"Hello {patient_name}. Great news! Your latest blood test results look healthy, and all measured values are within normal ranges. "
                f"Continue maintaining your healthy lifestyle and schedule regular annual checkups."
            )

        return {
            "summary": doc_summary,
            "doctor_summary": doc_summary,
            "patient_summary": pat_summary
        }
