"""
Response Enhancer (Phase 7 Medical AI — Architecture Freeze v8.2).
Decorates JSON objects with status icons, colors, chips, and follow-up prompts.
"""

from typing import Dict, Any, List

class ResponseEnhancer:
    """Enhances formatted JSON responses with UI metadata (icons, colors, badges)."""

    STATUS_COLORS = {
        "NORMAL": {"color": "emerald", "icon": "CheckCircle2", "badge": "bg-emerald-50 text-emerald-700 border-emerald-200"},
        "LOW": {"color": "sky", "icon": "ArrowDown", "badge": "bg-sky-50 text-sky-700 border-sky-200"},
        "HIGH": {"color": "amber", "icon": "ArrowUp", "badge": "bg-amber-50 text-amber-700 border-amber-200"},
        "CRITICAL_HIGH": {"color": "rose", "icon": "AlertTriangle", "badge": "bg-rose-50 text-rose-700 border-rose-200"},
        "CRITICAL_LOW": {"color": "rose", "icon": "AlertTriangle", "badge": "bg-rose-50 text-rose-700 border-rose-200"}
    }

    @classmethod
    def enhance(cls, formatted_data: Dict[str, Any], validated_params: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        enhanced = dict(formatted_data)
        
        # Populate findings if empty from validated_params
        if not enhanced.get("findings") and validated_params:
            enhanced_findings = []
            for p in validated_params[:6]:
                status = (p.get("status") or "NORMAL").upper()
                cfg = cls.STATUS_COLORS.get(status, cls.STATUS_COLORS["NORMAL"])
                enhanced_findings.append({
                    "parameter": p.get("parameter_name") or p.get("parameter_code"),
                    "value": str(p.get("converted_value") or p.get("numeric_value") or p.get("raw_value")),
                    "unit": p.get("canonical_unit") or p.get("unit") or "",
                    "status": status,
                    "color": cfg["color"],
                    "icon": cfg["icon"],
                    "badge": cfg["badge"]
                })
            enhanced["findings"] = enhanced_findings

        # Add response_type flag
        enhanced["response_type"] = "STRUCTURED_CARDS"
        enhanced["enhanced"] = True

        return enhanced
