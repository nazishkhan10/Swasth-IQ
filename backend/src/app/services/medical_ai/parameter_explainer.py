"""
Parameter Explainer Engine (Phase 7 Medical AI).
Explains specific laboratory parameters grounded strictly in Phase 5 validated data.
"""

from typing import Dict, Any

class ParameterExplainer:
    @classmethod
    def explain(cls, param_data: Dict[str, Any], provider_mgr) -> Dict[str, Any]:
        p_name = param_data.get("parameter_name") or param_data.get("parameter_code")
        val = param_data.get("converted_value") or param_data.get("numeric_value") or param_data.get("raw_value")
        unit = param_data.get("unit", "")
        status = param_data.get("status", "NORMAL")

        prompt = [
            {
                "role": "system",
                "content": "You are Swasth-IQ. Explain this validated lab parameter simply without calculating or inventing values."
            },
            {
                "role": "user",
                "content": f"Parameter: {p_name} | Value: {val} {unit} | Status: {status}"
            }
        ]
        return provider_mgr.generate(prompt, temperature=0.2)
