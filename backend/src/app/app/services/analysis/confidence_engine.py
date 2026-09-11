"""
Layered Confidence Engine (Phase 6).
Calculates a breakdown of OCR, Parser, Validation, Analysis, and Overall confidence scores.
"""

from typing import Dict, Any, List
from app.services.analysis.context import MedicalAnalysisContext


class ConfidenceEngine:

    @classmethod
    def calculate_confidence(cls, ctx: MedicalAnalysisContext, conflicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        ocr_conf_list = [p.get("ocr_confidence") or 0.95 for p in ctx.validated_parameters]
        val_conf_list = [p.get("validation_confidence") or 0.90 for p in ctx.validated_parameters]


        avg_ocr = (sum(ocr_conf_list) / len(ocr_conf_list)) if ocr_conf_list else 0.95
        avg_val = (sum(val_conf_list) / len(val_conf_list)) if val_conf_list else 0.90
        parser_conf = round(avg_ocr * 0.98, 2)

        analysis_base = 0.95
        # Apply conflict penalties
        total_penalty = sum(c.get("confidence_penalty", 0.1) for c in conflicts)
        analysis_conf = max(0.5, round(analysis_base - total_penalty, 2))

        # Quality gate adjustment
        if ctx.quality_score < 70:
            analysis_conf = max(0.5, round(analysis_conf - 0.15, 2))

        overall_conf = round((avg_ocr * 0.2) + (avg_val * 0.4) + (analysis_conf * 0.4), 2)

        return {
            "ocr_confidence": round(avg_ocr * 100, 1),
            "parser_confidence": round(parser_conf * 100, 1),
            "validation_confidence": round(avg_val * 100, 1),
            "analysis_confidence": round(analysis_conf * 100, 1),
            "overall_confidence": round(overall_conf * 100, 1),
            "overall_confidence_float": overall_conf,
            "conflicts_count": len(conflicts),
            "rationale": "High confidence based on validated reference ranges and deterministic rule evaluation." if not conflicts else f"Confidence reduced by {len(conflicts)} clinical conflict alert(s)."
        }
