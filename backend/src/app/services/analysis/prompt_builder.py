"""
Multi-Target Phase 7 Prompt Packager Engine (Phase 6).
Exports 5 structured JSON packages for Phase 7 LLM / RAG consumption:
1. doctor_package.json
2. patient_package.json
3. chat_package.json
4. rag_package.json
5. api_package.json
"""

from typing import Dict, Any, List
from app.services.analysis.context import MedicalAnalysisContext


class Phase7PromptPackager:

    @classmethod
    def package_all(cls, ctx: MedicalAnalysisContext, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        patient = ctx.patient_metadata
        conditions = analysis_data.get("conditions", [])
        evidence = analysis_data.get("evidence", [])
        recs = analysis_data.get("recommendations", [])
        score = analysis_data.get("health_score", 100)
        risk = analysis_data.get("overall_risk", "LOW")

        base_meta = {
            "patient_name": patient.get("patient_name"),
            "patient_id": patient.get("patient_id"),
            "age": patient.get("age"),
            "gender": patient.get("gender"),
            "report_date": patient.get("report_date"),
            "overall_health_score": score,
            "overall_risk": risk
        }

        # 1. Doctor Package
        doctor_package = {
            **base_meta,
            "clinical_summary": analysis_data.get("doctor_summary"),
            "detected_conditions": conditions,
            "evidence_matrix": evidence,
            "clinical_recommendations": recs,
            "organ_status": analysis_data.get("organ_data", {}).get("panels"),
            "conflicts": analysis_data.get("conflicts")
        }

        # 2. Patient Package
        patient_package = {
            **base_meta,
            "patient_summary": analysis_data.get("patient_summary"),
            "health_highlights": [
                f"{c.get('condition_name')}: {c.get('explanation', {}).get('why_detected')}"
                for c in conditions
            ],
            "key_next_steps": [r["action"] for r in recs[:3]]
        }

        # 3. Chat Package (Phase 7 Conversational Context)
        chat_package = {
            "system_instruction": "You are a clinical AI health assistant. Answer questions strictly using this structured context. Never invent lab values.",
            "patient_profile": base_meta,
            "conditions": conditions,
            "evidence_snippets": evidence,
            "recommendations": recs
        }

        # 4. RAG Package (Phase 7 Vector & Graph Context)
        rag_package = {
            "knowledge_graph": analysis_data.get("graph"),
            "timelines": analysis_data.get("timelines"),
            "parameter_influence": analysis_data.get("parameter_influence")
        }

        # 5. API Package
        api_package = {
            "report_id": ctx.report_id,
            "health_score": score,
            "risk": risk,
            "conditions_count": len(conditions),
            "evidence_count": len(evidence),
            "recommendations_count": len(recs)
        }

        return {
            "doctor": doctor_package,
            "patient": patient_package,
            "chat": chat_package,
            "rag": rag_package,
            "api": api_package
        }
