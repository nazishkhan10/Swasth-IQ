"""
Medical Knowledge Graph Engine (Phase 6).
Constructs a rich 9-node graph schema:
Patient -> Report -> Visit -> Parameter -> Validation -> Disease Rule -> Detected Condition -> Recommendation -> Evidence
For consumption by Phase 7 Hybrid Medical RAG Chat.
"""

from typing import List, Dict, Any
from app.services.analysis.context import MedicalAnalysisContext


class GraphBuilder:

    @classmethod
    def build_graph(cls, ctx: MedicalAnalysisContext, conditions: List[Any], evidence: List[Dict[str, Any]], recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        nodes = []
        edges = []

        patient_id = ctx.patient_metadata.get("patient_id") or f"PAT-{ctx.report_id:05d}"

        # 1. Patient Node
        nodes.append({"id": f"Node_Patient_{patient_id}", "type": "Patient", "label": f"Patient ({patient_id})"})

        # 2. Report Node
        nodes.append({"id": f"Node_Report_{ctx.report_id}", "type": "Report", "label": f"Report #{ctx.report_id}"})
        edges.append({"source": f"Node_Patient_{patient_id}", "target": f"Node_Report_{ctx.report_id}", "relation": "HAS_REPORT"})

        # 3. Visit Node
        nodes.append({"id": f"Node_Visit_{ctx.report_id}", "type": "Visit", "label": f"Visit ({ctx.patient_metadata.get('report_date') or 'Current'})"})
        edges.append({"source": f"Node_Report_{ctx.report_id}", "target": f"Node_Visit_{ctx.report_id}", "relation": "ASSOCIATED_VISIT"})

        # 4. Parameter & Validation Nodes
        for p in ctx.validated_parameters:
            name = p.get("parameter_name") or p.get("parameter_code") or "Parameter"
            code = p.get("parameter_code") or name
            val = p.get("converted_value") if p.get("is_converted") else p.get("numeric_value")

            p_node_id = f"Node_Param_{code}"
            nodes.append({"id": p_node_id, "type": "Parameter", "label": f"{name} ({val})"})
            edges.append({"source": f"Node_Visit_{ctx.report_id}", "target": p_node_id, "relation": "CONTAINS_PARAMETER"})

        # 5. Condition Nodes
        for c in conditions:
            c_name = getattr(c, "condition_name", "") if hasattr(c, "condition_name") else c.get("condition_name")
            c_id = getattr(c, "condition_id", "") if hasattr(c, "condition_id") else c.get("condition_id")
            c_node_id = f"Node_Condition_{c_id}"

            nodes.append({"id": c_node_id, "type": "DetectedCondition", "label": c_name})

            # Link parameters to condition
            supp = getattr(c, "supporting_parameters", []) if hasattr(c, "supporting_parameters") else c.get("supporting_parameters", [])
            for s_name in supp:
                for p in ctx.validated_parameters:
                    p_code = p.get("parameter_code") or p.get("parameter_name") or ""
                    if p_code and (p_code in s_name or s_name in p_code):
                        edges.append({"source": f"Node_Param_{p_code}", "target": c_node_id, "relation": "TRIGGERS_CONDITION"})

        # 6. Recommendation Nodes
        for r in recommendations:
            r_node_id = f"Node_Rec_{r['id']}"
            nodes.append({"id": r_node_id, "type": "Recommendation", "label": r["title"]})

            # Link to conditions if matching, else link from Visit
            linked = False
            for c in conditions:
                c_id = getattr(c, "condition_id", "") if hasattr(c, "condition_id") else c.get("condition_id")
                r_ids = getattr(c, "recommendation_ids", []) if hasattr(c, "recommendation_ids") else c.get("recommendation_ids", [])
                if r["id"] in r_ids:
                    edges.append({"source": f"Node_Condition_{c_id}", "target": r_node_id, "relation": "HAS_RECOMMENDATION"})
                    linked = True

            if not linked:
                edges.append({"source": f"Node_Visit_{ctx.report_id}", "target": r_node_id, "relation": "RECOMMENDED_ACTION"})

        # 7. Evidence Nodes
        for ev in evidence[:10]:
            ev_node_id = f"Node_Evidence_{ev['evidence_id']}"
            nodes.append({"id": ev_node_id, "type": "Evidence", "label": f"Evidence ({ev['parameter_name']}: {ev['canonical_value']} {ev['canonical_unit']})"})
            p_code = ev.get("parameter_code")
            if p_code:
                edges.append({"source": f"Node_Param_{p_code}", "target": ev_node_id, "relation": "PROVIDES_EVIDENCE"})

        return {
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges)
        }

