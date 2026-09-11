"""
Determinism Engine (Phase 6).
Computes SHA256 hash of validated parameters and metadata to ensure byte-for-byte
reproducibility and instant analysis cache lookup.
"""

import hashlib
import json
from typing import List, Dict, Any


class DeterminismEngine:
    @classmethod
    def compute_hash(cls, validated_params: List[Dict[str, Any]], patient_meta: Dict[str, Any]) -> str:
        """Generates a stable, canonical SHA256 checksum of validated input dataset."""
        sorted_params = sorted(
            validated_params,
            key=lambda p: (p.get("parameter_code") or p.get("parameter_name") or "", str(p.get("raw_value")))
        )
        canonical_payload = {
            "patient_id": patient_meta.get("patient_id") or patient_meta.get("accession_id"),
            "gender": patient_meta.get("gender"),
            "age": patient_meta.get("age"),
            "parameters": [
                {
                    "code": p.get("parameter_code"),
                    "name": p.get("parameter_name"),
                    "val": p.get("converted_value") if p.get("is_converted") else p.get("numeric_value"),
                    "unit": p.get("canonical_unit") or p.get("normalized_unit"),
                    "status": p.get("status")
                }
                for p in sorted_params
            ]
        }
        serialized = json.dumps(canonical_payload, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
