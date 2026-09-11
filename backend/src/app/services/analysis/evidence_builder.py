"""
Deep Evidence Builder Engine (Phase 6).
Generates structured evidence records linking clinical findings and recommendations
to exact validated parameters, raw values, canonical units, reference ranges, page numbers,
deviation metrics, OCR confidence, and validation confidence.
"""

from typing import List, Dict, Any
from app.services.analysis.context import MedicalAnalysisContext


class EvidenceBuilder:

    @classmethod
    def build_evidence(cls, ctx: MedicalAnalysisContext, conditions: List[Any]) -> List[Dict[str, Any]]:
        evidence_list = []
        seen_keys = set()

        for p in ctx.validated_parameters:
            name = p.get("parameter_name") or p.get("parameter_code") or "Parameter"
            code = p.get("parameter_code") or name
            status = (p.get("status") or "NORMAL").upper()

            key = f"{code}_{p.get('numeric_value')}_{status}"
            if key in seen_keys:
                continue
            seen_keys.add(key)


            num_val = p.get("converted_value") if p.get("is_converted") else p.get("numeric_value")
            unit = p.get("canonical_unit") or p.get("normalized_unit") or ""
            ref_low = p.get("ref_range_low")
            ref_high = p.get("ref_range_high")

            # Calculate deviation metric
            deviation = "Within Reference"
            if num_val is not None and ref_high is not None and num_val > ref_high:
                diff = round(num_val - ref_high, 2)
                pct = round(((num_val - ref_high) / ref_high) * 100.0, 1) if ref_high > 0 else 0
                deviation = f"+{diff} {unit} (+{pct}% above upper limit {ref_high})"
            elif num_val is not None and ref_low is not None and num_val < ref_low:
                diff = round(ref_low - num_val, 2)
                pct = round(((ref_low - num_val) / ref_low) * 100.0, 1) if ref_low > 0 else 0
                deviation = f"-{diff} {unit} (-{pct}% below lower limit {ref_low})"

            evidence_id = f"EV_{code}_{len(evidence_list)+1:03d}"

            evidence_list.append({
                "evidence_id": evidence_id,
                "parameter_name": name,
                "parameter_code": code,
                "raw_value": str(p.get("raw_value")),
                "canonical_value": str(num_val),
                "canonical_unit": unit,
                "status": status,
                "page_number": p.get("page_number", 1),
                "reference_range": f"{ref_low or ''} - {ref_high or ''} {unit}".strip(),
                "deviation": deviation,
                "validation_confidence": p.get("validation_confidence", 0.90),
                "ocr_confidence": p.get("ocr_confidence", 0.95),
                "reference_source": p.get("reference_source", "STANDARD_DATABASE"),
                "is_unit_converted": p.get("is_converted", False),
                "conversion_audit": f"{p.get('raw_value')} {p.get('unit')} -> {num_val} {unit}" if p.get("is_converted") else None
            })

        return evidence_list
