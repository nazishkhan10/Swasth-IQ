"""
Medical Analysis Engine (Phase 6 Master Orchestrator).
Executes the full deterministic runtime pipeline:
Data Quality Gate -> Analysis Context -> Organ Classification -> Disease Rule Registry ->
Risk Engine -> Health Score -> Conflict Detector -> Missing Evidence -> Evidence Builder ->
Recommendation Engine -> Timeline Builder -> Knowledge Graph -> Dual Summary Builder ->
Layered Confidence -> Phase 7 Prompt Packager -> Persistence & Caching.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.report import Report
from app.models.patient_metadata import PatientMetadata
from app.models.validated_medical_value import ValidatedMedicalValue
from app.models.parse_warning import ParseWarning
from app.models.medical_analysis import MedicalAnalysis

from app.services.analysis.context import MedicalAnalysisContext
from app.services.analysis.determinism import DeterminismEngine
from app.services.analysis.organ_system_classifier import OrganSystemClassifier
from app.services.analysis.rules import ALL_DISEASE_RULES
from app.services.analysis.conflict_detector import ClinicalConflictDetector
from app.services.analysis.missing_evidence import MissingEvidenceEngine
from app.services.analysis.health_score_engine import HealthScoreEngine
from app.services.analysis.parameter_influence import ParameterInfluenceEngine
from app.services.analysis.coverage_checklist import CoverageChecklistEngine
from app.services.analysis.risk_engine import RiskEngine
from app.services.analysis.evidence_builder import EvidenceBuilder
from app.services.analysis.recommendation_engine import RecommendationEngine
from app.services.analysis.timeline_builder import TimelineBuilder
from app.services.analysis.graph_builder import GraphBuilder
from app.services.analysis.ai_summary_builder import AISummaryBuilder
from app.services.analysis.confidence_engine import ConfidenceEngine
from app.services.analysis.prompt_builder import Phase7PromptPackager

logger = logging.getLogger(__name__)


class MedicalAnalysisEngine:

    @classmethod
    def run_analysis(cls, db: Session, report_id: int, force_recompute: bool = False) -> Dict[str, Any]:
        """Runs full Phase 6 clinical reasoning or fetches cached analysis if hash matches."""

        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise ValueError(f"Report #{report_id} not found.")

        # 1. Fetch Phase 5 Validated Values
        val_records = db.query(ValidatedMedicalValue).filter(ValidatedMedicalValue.report_id == report_id).all()
        if not val_records:
            # Trigger Phase 5 validation auto-run if none exists
            from app.services.validation.validation_engine import ValidationEngine
            ValidationEngine.validate_report(db, report)

            val_records = db.query(ValidatedMedicalValue).filter(ValidatedMedicalValue.report_id == report_id).all()

        val_params = [
            {
                "parameter_code": r.parameter_code,
                "parameter_name": r.parameter_name,
                "numeric_value": r.validated_value,
                "converted_value": r.converted_value,
                "is_converted": r.is_converted,
                "canonical_unit": r.canonical_unit,
                "normalized_unit": r.normalized_unit,
                "ref_range_low": r.reference_low,
                "ref_range_high": r.reference_high,
                "status": r.status,
                "raw_value": r.raw_value,
                "unit": r.raw_unit,
                "page_number": getattr(r, "page_number", 1),
                "validation_confidence": r.validation_confidence,
                "ocr_confidence": r.ocr_confidence,
                "reference_source": r.reference_source
            }
            for r in val_records
        ]


        # 2. Fetch Patient Metadata
        pm = db.query(PatientMetadata).filter(PatientMetadata.report_id == report_id).first()
        meta_dict = {
            "patient_name": pm.patient_name if pm else None,
            "patient_id": (pm.accession_number or getattr(pm, "patient_id", None)) if pm else None,
            "age": pm.age if pm else None,
            "gender": pm.gender if pm else None,
            "report_date": pm.report_date if pm else None,
            "facility_name": (pm.lab_name or getattr(pm, "facility_name", None)) if pm else None,
            "accession_id": pm.accession_number if pm else None
        }


        # 3. Compute Determinism Hash
        dataset_hash = DeterminismEngine.compute_hash(val_params, meta_dict)

        # Check Cache unless force_recompute
        if not force_recompute:
            cached = db.query(MedicalAnalysis).filter(
                MedicalAnalysis.report_id == report_id,
                MedicalAnalysis.determinism_hash == dataset_hash
            ).first()
            if cached:
                logger.info(f"[Phase 6] Returning cached analysis for Report #{report_id} (hash: {dataset_hash[:12]})")
                return cls._to_response_dict(cached, val_params)


        # 4. Fetch Quality Score & Warnings
        from app.services.validation.validation_engine import ValidationEngine
        try:
            quality_dict = ValidationEngine._compute_quality_score(val_records, warn_dicts, pm)
            quality_score = quality_dict.get("score", 85)
        except Exception:
            quality_score = 85


        warn_records = db.query(ParseWarning).filter(ParseWarning.report_id == report_id).all()
        warn_dicts = [{"warning_type": w.warning_type, "message": w.message} for w in warn_records]

        # Quality Gate Check
        if quality_score < 50:
            quality_status = "BLOCKED"
        elif quality_score < 70:
            quality_status = "LIMITED"
        elif quality_score < 90:
            quality_status = "WARNING"
        else:
            quality_status = "FULL"

        # 5. Build Immutable Analysis Context
        ctx = MedicalAnalysisContext(
            report_id=report_id,
            patient_metadata=meta_dict,
            validated_parameters=val_params,
            validation_summary={"quality_score": quality_score},
            validation_warnings=warn_dicts,
            quality_score=quality_score,
            quality_gate_status=quality_status,
            confidence=quality_score / 100.0
        )


        # 6. Execute Pipeline
        organ_data = OrganSystemClassifier.classify(ctx)

        detected_conditions = []
        for rule_cls in ALL_DISEASE_RULES:
            cond = rule_cls.evaluate(ctx)
            if cond:
                detected_conditions.append(cond)

        conflicts = ClinicalConflictDetector.detect_conflicts(ctx)
        missing_ev = MissingEvidenceEngine.evaluate_missing_evidence(ctx)
        health_score_data = HealthScoreEngine.calculate_score(ctx, organ_data, detected_conditions)
        risk_data = RiskEngine.evaluate_risks(ctx, detected_conditions, organ_data)

        param_influence = ParameterInfluenceEngine.compute_influence(ctx, detected_conditions, organ_data)
        coverage_check = CoverageChecklistEngine.evaluate_coverage(ctx)

        evidence_list = EvidenceBuilder.build_evidence(ctx, detected_conditions)
        recs = RecommendationEngine.generate_recommendations(ctx, detected_conditions, evidence_list)

        timelines = TimelineBuilder.build_timelines(ctx, health_score_data["overall_health_score"], detected_conditions)
        graph = GraphBuilder.build_graph(ctx, detected_conditions, evidence_list, recs)

        summaries = AISummaryBuilder.build_summaries(ctx, detected_conditions, risk_data, recs)
        confidence_data = ConfidenceEngine.calculate_confidence(ctx, conflicts)

        # Versioning metadata
        versioning_dict = {
            "analysis_version": "3.0.0",
            "rule_version": "1.1.0",
            "knowledge_version": "1.0.0",
            "recommendation_version": "2.0.0",
            "reference_db_version": "2026.1",
            "prompt_package_version": "1.0.0"
        }

        full_analysis_data = {
            "organ_data": organ_data,
            "conditions": [c.__dict__ if hasattr(c, "__dict__") else c for c in detected_conditions],
            "evidence": evidence_list,
            "recommendations": recs,
            "health_score": health_score_data["overall_health_score"],
            "overall_risk": health_score_data["overall_risk"],
            "doctor_summary": summaries["doctor_summary"],
            "patient_summary": summaries["patient_summary"],
            "conflicts": conflicts,
            "graph": graph,
            "timelines": timelines,
            "parameter_influence": param_influence
        }

        prompt_packages = Phase7PromptPackager.package_all(ctx, full_analysis_data)

        # 7. Persist Result to DB
        db.query(MedicalAnalysis).filter(MedicalAnalysis.report_id == report_id).delete()
        db.flush()

        analysis_rec = MedicalAnalysis(
            report_id=report_id,
            determinism_hash=dataset_hash,
            overall_health_score=health_score_data["overall_health_score"],
            overall_risk=health_score_data["overall_risk"],
            analysis_version="3.0.0",
            versioning_json=json.dumps(versioning_dict),
            summary=summaries["summary"],
            doctor_summary=summaries["doctor_summary"],
            patient_summary=summaries["patient_summary"],
            recommendations_json=json.dumps(recs),
            evidence_json=json.dumps(evidence_list),
            missing_evidence_json=json.dumps(missing_ev),
            conflicts_json=json.dumps(conflicts),
            organ_json=json.dumps(organ_data["panels"]),
            organ_dependency_json=json.dumps(organ_data["dependency_graph"]),
            timeline_json=json.dumps(timelines["visit_timeline"]),
            timeline_deltas_json=json.dumps(timelines["parameter_deltas"]),
            graph_json=json.dumps(graph),
            risk_json=json.dumps(risk_data),
            conditions_json=json.dumps([c.__dict__ if hasattr(c, "__dict__") else c for c in detected_conditions]),
            confidence_json=json.dumps(confidence_data),
            parameter_influence_json=json.dumps(param_influence),
            coverage_checklist_json=json.dumps(coverage_check),
            prompt_packages_json=json.dumps(prompt_packages),
            quality_gate_status=quality_status,
            confidence=confidence_data["overall_confidence_float"]
        )

        db.add(analysis_rec)
        db.commit()
        db.refresh(analysis_rec)

        return cls._to_response_dict(analysis_rec, val_params)


    @classmethod
    def _to_response_dict(cls, rec: MedicalAnalysis, val_params: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "id": rec.id,
            "report_id": rec.report_id,
            "determinism_hash": rec.determinism_hash,
            "overall_health_score": rec.overall_health_score,
            "overall_risk": rec.overall_risk,
            "analysis_version": rec.analysis_version,
            "versioning": json.loads(rec.versioning_json) if rec.versioning_json else {},
            "quality_gate_status": rec.quality_gate_status,
            "confidence": rec.confidence,
            "summary": rec.summary,
            "doctor_summary": rec.doctor_summary,
            "patient_summary": rec.patient_summary,
            "recommendations": json.loads(rec.recommendations_json) if rec.recommendations_json else [],
            "evidence": json.loads(rec.evidence_json) if rec.evidence_json else [],
            "missing_evidence": json.loads(rec.missing_evidence_json) if rec.missing_evidence_json else [],
            "conflicts": json.loads(rec.conflicts_json) if rec.conflicts_json else [],
            "organ_panels": json.loads(rec.organ_json) if rec.organ_json else {},
            "organ_dependencies": json.loads(rec.organ_dependency_json) if rec.organ_dependency_json else [],
            "timelines": json.loads(rec.timeline_json) if rec.timeline_json else [],
            "timeline_deltas": json.loads(rec.timeline_deltas_json) if rec.timeline_deltas_json else [],
            "graph": json.loads(rec.graph_json) if rec.graph_json else {},
            "risk": json.loads(rec.risk_json) if rec.risk_json else {},
            "conditions": json.loads(rec.conditions_json) if rec.conditions_json else [],
            "confidence_breakdown": json.loads(rec.confidence_json) if rec.confidence_json else {},
            "parameter_influence": json.loads(rec.parameter_influence_json) if rec.parameter_influence_json else [],
            "coverage_checklist": json.loads(rec.coverage_checklist_json) if rec.coverage_checklist_json else [],
            "prompt_packages": json.loads(rec.prompt_packages_json) if rec.prompt_packages_json else {},
            "validated_parameters": val_params or [],
            "created_at": rec.created_at.isoformat() if rec.created_at else None
        }

