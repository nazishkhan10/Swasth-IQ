"""
Master Medical Parser Service (Phase 4).
Executes multi-stage medical parsing pipeline on OCR output and persists structured records idempotently.
"""

import time
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.report import Report
from app.models.ocr_result import OCRResult
from app.models.medical_value import MedicalValue
from app.models.patient_metadata import PatientMetadata
from app.models.parse_warning import ParseWarning

from app.services.parser.report_classifier import ReportClassifier
from app.services.parser.patient_parser import PatientParser
from app.services.parser.parser_rules import ParserRules
from app.services.parser.timeline_parser import TimelineParser
from app.services.parser.duplicate_resolver import DuplicateResolver
from app.services.parser.parse_warnings import ParseWarningService
from app.services.ocr_storage import load_page_json
from app.logs.logger import logger


class MedicalParser:
    """Master Orchestrator for Phase 4 Medical Data Extraction."""

    @classmethod
    def parse_report(cls, db: Session, report: Report) -> Dict[str, Any]:
        start_time = time.time()
        logger.info(f"[MedicalParser] Starting Phase 4 pipeline execution for Report #{report.id} ({report.original_filename})")

        # 1. Fetch OCR Result DB records & Page JSONs (Normalized convergence layer)
        ocr_results = db.query(OCRResult).filter(
            OCRResult.report_id == report.id,
            OCRResult.version == (report.ocr_version or 1)
        ).order_by(OCRResult.page_number).all()

        pages_data: List[Dict[str, Any]] = []
        all_blocks: List[Dict[str, Any]] = []
        full_text_accumulator = ""

        for res in ocr_results:
            p_json = load_page_json(res.json_path)
            if p_json:
                pages_data.append(p_json)
                all_blocks.extend(p_json.get("blocks", []))
                full_text_accumulator += p_json.get("text", "") + "\n"

        if not pages_data:
            logger.info(f"[MedicalParser] No OCR JSON data found for Report #{report.id}. Auto-executing Phase 3 OCR...")
            from app.services.ocr_service import OCRService
            OCRService.process_report_ocr(db=db, report=report)
            ocr_results = db.query(OCRResult).filter(
                OCRResult.report_id == report.id,
                OCRResult.version == target_ver
            ).order_by(OCRResult.page_number).all()
            for res in ocr_results:
                p_json = load_page_json(res.json_path)
                if p_json:
                    pages_data.append(p_json)
                    all_blocks.extend(p_json.get("blocks", []))
                    full_text_accumulator += p_json.get("text", "") + "\n"

        if not pages_data:
            raise ValueError(f"No OCR data available for Report #{report.id} after auto-execution.")


        # 2. Stage 1: Report Classifier
        detected_type = ReportClassifier.classify(full_text_accumulator)
        logger.info(f"[MedicalParser] Stage 1 (Report Classifier) -> Detected Type: '{detected_type}'")

        # 3. Stage 2: Patient Parser
        patient_info = PatientParser.parse(all_blocks)
        patient_info["detected_report_type"] = detected_type
        logger.info(f"[MedicalParser] Stage 2 (Patient Parser) -> Extracted metadata for '{patient_info.get('patient_name') or 'Unknown Patient'}'")

        # 4. Stage 3-6: Parameter Extraction Strategy Selection
        combined_params: List[Dict[str, Any]] = []
        combined_warnings: List[Dict[str, Any]] = []

        if detected_type == "Longitudinal Patient Tracking Report":
            logger.info(f"[MedicalParser] Executing TimelineParser Strategy for Report #{report.id}")
            t_params, t_warns = TimelineParser.parse(pages_data)
            combined_params.extend(t_params)
            combined_warnings.extend(t_warns)

        # Fallback / Laboratory Parser Execution if non-timeline or timeline returned empty
        if not combined_params:
            logger.info(f"[MedicalParser] Executing Laboratory Parser Rules Strategy for Report #{report.id}")
            md_extracted, md_warnings = ParserRules.extract_from_markdown_tables(pages_data)
            table_extracted, table_warnings = ParserRules.extract_from_tables(pages_data)
            block_extracted, block_warnings = ParserRules.extract_from_blocks(pages_data)

            combined_params = md_extracted + table_extracted + block_extracted
            combined_warnings = md_warnings + table_warnings + block_warnings

        logger.info(f"[MedicalParser] Stage 3-6 (Extraction) -> Found {len(combined_params)} parameter candidates across {len(pages_data)} pages.")

        # 5. Stage 7: Duplicate Resolver
        resolved_params, dup_warnings = DuplicateResolver.resolve(combined_params)
        all_warnings = combined_warnings + dup_warnings

        if not resolved_params:
            all_warnings.append({
                "page_number": 1,
                "parameter_name": None,
                "warning_type": "Zero Extraction Failure",
                "message": "No valid medical parameters could be resolved from OCR output. Check table formatting."
            })
            logger.warning(f"[MedicalParser] Warning: Zero parameters extracted for Report #{report.id}")

        logger.info(f"[MedicalParser] Stage 7 (Duplicate Resolver) -> {len(resolved_params)} canonical parameters retained after resolving duplicates.")

        # 6. Idempotent Database Persistence
        # A) Delete old Medical Values & Parse Warnings for this report
        db.query(MedicalValue).filter(MedicalValue.report_id == report.id).delete()
        db.query(ParseWarning).filter(ParseWarning.report_id == report.id).delete()
        db.flush()

        # B) Idempotent Upsert for Patient Metadata
        patient_entry = db.query(PatientMetadata).filter(PatientMetadata.report_id == report.id).first()
        if not patient_entry:
            patient_entry = PatientMetadata(report_id=report.id)
            db.add(patient_entry)

        patient_entry.patient_name = patient_info.get("patient_name")
        patient_entry.age = patient_info.get("age")
        patient_entry.gender = patient_info.get("gender")
        patient_entry.lab_name = patient_info.get("lab_name")
        patient_entry.doctor_name = patient_info.get("doctor_name")
        patient_entry.report_date = patient_info.get("report_date")
        patient_entry.sample_date = patient_info.get("sample_date")
        patient_entry.accession_number = patient_info.get("accession_number")
        patient_entry.detected_report_type = detected_type
        patient_entry.confidence = patient_info.get("confidence", 0.90)

        # C) Insert New Medical Values
        for p in resolved_params:
            mv_entry = MedicalValue(
                report_id=report.id,
                ocr_version=report.ocr_version or 1,
                page_number=p.get("page_number", 1),
                block_id=p.get("block_id"),
                parameter_name=p["parameter_name"],
                parameter_code=p.get("parameter_code"),
                category=p.get("category", "General"),
                value=p["value"],
                numeric_value=p.get("numeric_value"),
                unit=p.get("unit"),
                reference_range=p.get("reference_range"),
                reference_context=p.get("reference_context"),
                reference_low=p.get("reference_low"),
                reference_high=p.get("reference_high"),
                status="Pending Validation", # Always 'Pending Validation' in Phase 4
                confidence=p.get("confidence", 0.90),
                bbox=p.get("bbox")
            )
            db.add(mv_entry)

        db.commit()

        # D) Record Warnings
        ParseWarningService.record_warnings(db, report.id, all_warnings)

        proc_time = round(time.time() - start_time, 3)
        avg_confidence = round(sum(p.get("confidence", 0.90) for p in resolved_params) / max(len(resolved_params), 1), 2)

        logger.info(f"[MedicalParser] Phase 4 Pipeline COMPLETED for Report #{report.id} in {proc_time}s | {len(resolved_params)} parameters | Avg Conf: {avg_confidence}")

        return cls.get_parsed_data(db, report)

    @classmethod
    def get_parsed_data(cls, db: Session, report: Report) -> Dict[str, Any]:
        patient_rec = db.query(PatientMetadata).filter(PatientMetadata.report_id == report.id).first()
        values_recs = db.query(MedicalValue).filter(MedicalValue.report_id == report.id).order_by(MedicalValue.page_number, MedicalValue.id).all()

        patient_dict = {
            "patient_name": patient_rec.patient_name if patient_rec else None,
            "age": patient_rec.age if patient_rec else None,
            "gender": patient_rec.gender if patient_rec else None,
            "lab_name": patient_rec.lab_name if patient_rec else None,
            "doctor_name": patient_rec.doctor_name if patient_rec else None,
            "report_date": patient_rec.report_date if patient_rec else None,
            "sample_date": patient_rec.sample_date if patient_rec else None,
            "accession_number": patient_rec.accession_number if patient_rec else None,
            "detected_report_type": patient_rec.detected_report_type if patient_rec else "General",
            "confidence": patient_rec.confidence if patient_rec else 1.0
        }

        params_list = []
        for v in values_recs:
            params_list.append({
                "id": v.id,
                "page_number": v.page_number,
                "block_id": v.block_id,
                "parameter_name": v.parameter_name,
                "parameter_code": v.parameter_code,
                "category": v.category,
                "value": v.value,
                "numeric_value": v.numeric_value,
                "unit": v.unit,
                "reference_range": v.reference_range,
                "reference_context": v.reference_context,
                "reference_low": v.reference_low,
                "reference_high": v.reference_high,
                "status": v.status, # Pending Validation
                "confidence": v.confidence,
                "bbox": v.bbox
            })

        avg_conf = round(sum(p["confidence"] for p in params_list) / max(len(params_list), 1), 2)

        return {
            "report_id": report.id,
            "status": "completed" if params_list else "no_data",
            "detected_report_type": patient_dict["detected_report_type"],
            "overall_confidence": avg_conf,
            "total_parameters": len(params_list),
            "patient": patient_dict,
            "parameters": params_list
        }
