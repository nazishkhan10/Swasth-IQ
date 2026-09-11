"""
Medical Validation Engine — Phase 5 Clinical Hardening.

Full 9-stage deterministic validation pipeline:
  Stage 1 — Alias Resolution         (FBS → GLU_FAST)
  Stage 2 — Numeric Parsing          (<20, ≈4.5 → float + operator)
  Stage 3 — Qualitative Detection    (Negative/Reactive → QUALITATIVE)
  Stage 4 — Unit Normalization       (mg/dl → mg/dL)
  Stage 5 — Unit Compatibility Check (CREAT + ng/dL → INVALID_UNIT — STOP)
  Stage 6 — Unit Conversion          (µmol/L → mg/dL before comparison)
  Stage 7 — Hard Limit Sanity        (HbA1c 999% → INVALID_VALUE — STOP)
  Stage 8 — Reference Range Validation (bad report ref → fallback + warning)
  Stage 9 — Critical Rules + Range Classification + Severity + OCR Weighting

Every stage appends to a per-parameter validation_trace list.
A data_quality_score is computed for the whole report at the end.
"""

import time
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.report import Report
from app.models.medical_value import MedicalValue
from app.models.patient_metadata import PatientMetadata
from app.models.validated_medical_value import ValidatedMedicalValue
from app.models.parse_warning import ParseWarning

from app.services.parser.unit_normalizer import UnitNormalizer
from app.services.parser.numeric_parser import NumericParser
from app.services.validation.parameter_aliases import ParameterAliasResolver
from app.services.validation.unit_compatibility import UnitCompatibilityLayer
from app.services.validation.parameter_sanity import ParameterSanityRules
from app.services.validation.reference_ranges import ReferenceRangeService
from app.services.validation.critical_rules import CriticalRulesEngine
from app.logs.logger import logger


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _trace(steps: List[str], msg: str) -> None:
    steps.append(msg)


def _warn(warnings: List[Dict], page: int, param: str, wtype: str, msg: str) -> None:
    warnings.append({
        "page_number": page,
        "parameter_name": param,
        "warning_type": wtype,
        "message": msg,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Main Engine
# ─────────────────────────────────────────────────────────────────────────────

class ValidationEngine:
    """Master Orchestrator — Phase 5 Medical Validation Engine."""

    @classmethod
    def validate_report(cls, db: Session, report: Report) -> Dict[str, Any]:
        start_time = time.time()
        logger.info(f"[ValidationEngine] Starting Phase 5 validation for Report #{report.id}")

        raw_values = db.query(MedicalValue).filter(MedicalValue.report_id == report.id).all()
        patient_rec = db.query(PatientMetadata).filter(PatientMetadata.report_id == report.id).first()

        age_str = patient_rec.age if patient_rec else None
        gender_str = patient_rec.gender if patient_rec else None

        if not raw_values:
            logger.info(f"[ValidationEngine] No MedicalValues found for Report #{report.id}. Auto-executing Phase 4 Medical Parser...")
            from app.services.parser.medical_parser import MedicalParser
            MedicalParser.parse_report(db, report)
            raw_values = db.query(MedicalValue).filter(MedicalValue.report_id == report.id).all()
            patient_rec = db.query(PatientMetadata).filter(PatientMetadata.report_id == report.id).first()

            if not raw_values:
                logger.warning(f"[ValidationEngine] Still no MedicalValues found for Report #{report.id} after auto-parsing.")

            return {
                "report_id": report.id, "status": "no_data",
                "total_parameters": 0, "validated_parameters": 0,
                "data_quality_score": 0, "data_quality_breakdown": {},
                "summary": {"normal": 0, "low": 0, "high": 0, "critical": 0,
                            "unknown": 0, "invalid": 0, "qualitative": 0, "warnings": 0},
                "validated_values": []
            }

        # Idempotent — clear previous validation data
        db.query(ValidatedMedicalValue).filter(ValidatedMedicalValue.report_id == report.id).delete()
        db.flush()
        # Idempotent — clear ALL previous warnings for this report on each validation run.
        # This prevents duplicate accumulation when the user re-runs validation or the
        # parser re-runs (e.g. MedicalDataViewer auto-triggers parse on load).
        db.query(ParseWarning).filter(
            ParseWarning.report_id == report.id
        ).delete(synchronize_session=False)
        db.flush()

        validated_records: List[ValidatedMedicalValue] = []
        all_warnings: List[Dict] = []

        for mv in raw_values:
            try:
                record, warns = cls._validate_single(mv, age_str, gender_str)
                validated_records.append(record)
                all_warnings.extend(warns)
            except Exception as exc:
                # Never fail the entire report — isolate per-parameter errors
                logger.error(f"[ValidationEngine] Error validating '{mv.parameter_name}': {exc}")
                _warn(all_warnings, mv.page_number or 1, mv.parameter_name or "?",
                      "Validation Warning", f"Unexpected error: {exc}")

        for rec in validated_records:
            db.add(rec)
        db.commit()

        for w in all_warnings:
            db.add(ParseWarning(
                report_id=report.id,
                page_number=w.get("page_number", 1),
                parameter_name=w.get("parameter_name"),
                warning_type=w.get("warning_type", "Validation Warning"),
                message=w.get("message", ""),
            ))
        db.commit()

        proc_time = round(time.time() - start_time, 3)
        quality = cls._compute_quality_score(validated_records, all_warnings, patient_rec)
        summary = cls.get_validation_summary(db, report)

        logger.info(
            f"[ValidationEngine] Phase 5 COMPLETED for Report #{report.id} in {proc_time}s "
            f"| Validated: {len(validated_records)} | Critical: {summary.get('critical', 0)} "
            f"| Quality: {quality['score']}/100"
        )

        result = cls.get_validated_data(db, report)
        result["data_quality_score"] = quality["score"]
        result["data_quality_breakdown"] = quality["breakdown"]
        return result

    # ─────────────────────────────────────────────────────────────────────────
    # Per-parameter 9-stage pipeline
    # ─────────────────────────────────────────────────────────────────────────

    @classmethod
    def _validate_single(
        cls,
        mv: MedicalValue,
        age_str: Optional[str],
        gender_str: Optional[str]
    ) -> Tuple[ValidatedMedicalValue, List[Dict]]:

        warnings: List[Dict] = []
        trace: List[str] = []
        page = mv.page_number or 1
        param_name = mv.parameter_name or "Unknown"

        # ── Stage 1: Alias Resolution ─────────────────────────────────────
        param_code = ParameterAliasResolver.resolve(param_name, mv.parameter_code)
        if param_code != (mv.parameter_code or "").upper():
            _trace(trace, f"S1: Alias resolved '{mv.parameter_code}' → '{param_code}'")
        else:
            _trace(trace, f"S1: Code retained '{param_code}'")

        # ── Stage 2: Numeric Parsing ──────────────────────────────────────
        parsed = NumericParser.parse(mv.value or "")
        num_val = parsed.value
        value_operator = parsed.operator
        _trace(trace, f"S2: Parsed '{mv.value}' → {value_operator} {num_val} (numeric={parsed.is_numeric})")

        # ── Stage 3: Qualitative Detection ───────────────────────────────
        is_qualitative = ParameterSanityRules.is_qualitative(mv.value or "")
        if is_qualitative:
            _trace(trace, f"S3: Qualitative value detected: '{mv.value}'")
            rec = cls._build_record(
                mv=mv, param_code=param_code, status="QUALITATIVE", severity="QUALITATIVE",
                is_critical=False, ref_low=None, ref_high=None, ref_text=None,
                ref_source="UNKNOWN", norm_unit=mv.unit or "",
                num_val=None, conv_val=None, conv_unit=None, conv_factor=None, was_converted=False,
                ocr_conf=float(mv.confidence or 0.9),
                val_conf=float(mv.confidence or 0.9),
                notes=f"Qualitative result: {mv.value}",
                trace=trace,
            )
            _warn(warnings, page, param_name, "Qualitative Value",
                  f"'{mv.value}' is a qualitative result, not numeric. Stored as QUALITATIVE.")
            return rec, warnings

        # ── Stage 4: Unit Normalization ───────────────────────────────────
        raw_unit = mv.unit or ""
        norm_unit = UnitNormalizer.normalize(raw_unit) if raw_unit else ""
        if not norm_unit:
            norm_unit = raw_unit
        _trace(trace, f"S4: Unit '{raw_unit}' → '{norm_unit}'")

        if raw_unit and not UnitNormalizer.is_known_unit(raw_unit):
            _warn(warnings, page, param_name, "Unknown Unit",
                  f"Unit '{raw_unit}' is not in the canonical unit registry.")

        # ── Stage 5: Unit Compatibility Check ─────────────────────────────
        is_compatible = UnitCompatibilityLayer.is_compatible(param_code, norm_unit)
        _trace(trace, f"S5: Unit compatibility '{norm_unit}' for '{param_code}': {is_compatible}")

        if norm_unit and not is_compatible:
            allowed = UnitCompatibilityLayer.get_allowed_units(param_code)
            reason = (
                f"Unit '{norm_unit}' is incompatible with {param_code}. "
                f"Expected: {', '.join(allowed) if allowed else 'unknown'}."
            )
            _warn(warnings, page, param_name, "Invalid Unit", reason)
            _trace(trace, f"S5: STOP — INVALID_UNIT")

            rec = cls._build_record(
                mv=mv, param_code=param_code, status="INVALID_UNIT", severity="UNKNOWN",
                is_critical=False, ref_low=None, ref_high=None, ref_text=None,
                ref_source="UNKNOWN", norm_unit=norm_unit,
                num_val=num_val, conv_val=None, conv_unit=None, conv_factor=None, was_converted=False,
                ocr_conf=float(mv.confidence or 0.9),
                val_conf=0.0,
                notes=reason,
                trace=trace,
            )
            return rec, warnings

        # ── Stage 6: Unit Conversion ──────────────────────────────────────
        conv_val = num_val
        conv_unit = norm_unit
        conv_factor = None
        was_converted = False

        if num_val is not None and norm_unit:
            conversion = UnitCompatibilityLayer.convert(param_code, num_val, norm_unit)
            if conversion.was_converted:
                conv_val = conversion.converted_value
                conv_unit = conversion.canonical_unit
                conv_factor = conversion.conversion_factor
                was_converted = True
                _trace(trace, f"S6: Converted {num_val} {norm_unit} → {conv_val} {conv_unit} (×{conv_factor})")
                _warn(warnings, page, param_name, "Converted Unit",
                      f"Unit converted: {num_val} {norm_unit} → {conv_val} {conv_unit}")
            else:
                _trace(trace, f"S6: No conversion needed (already canonical)")
        else:
            _trace(trace, f"S6: Skipped (no numeric value or no unit)")

        # Use converted value for all downstream comparisons
        compare_val = conv_val if conv_val is not None else num_val

        # ── Stage 7: Hard Limit Sanity ────────────────────────────────────
        if compare_val is not None:
            sanity = ParameterSanityRules.check_hard_limits(param_code, compare_val)
            _trace(trace, f"S7: Hard limit check → valid={sanity.valid} ({sanity.reason})")

            if not sanity.valid:
                _warn(warnings, page, param_name, "Invalid Value", sanity.reason)
                rec = cls._build_record(
                    mv=mv, param_code=param_code, status="INVALID_VALUE", severity="UNKNOWN",
                    is_critical=False, ref_low=None, ref_high=None, ref_text=None,
                    ref_source="UNKNOWN", norm_unit=conv_unit or norm_unit,
                    num_val=num_val, conv_val=conv_val, conv_unit=conv_unit,
                    conv_factor=conv_factor, was_converted=was_converted,
                    ocr_conf=float(mv.confidence or 0.9),
                    val_conf=0.0,
                    notes=sanity.reason,
                    trace=trace,
                )
                return rec, warnings
        else:
            _trace(trace, f"S7: Skipped (no numeric value)")

        # ── Stage 8: Reference Range Validation ───────────────────────────
        ref_low = mv.reference_low
        ref_high = mv.reference_high
        ref_text = mv.reference_range
        ref_source = "REPORT"

        if ref_low is not None or ref_high is not None:
            # Sanity-check the report-supplied reference
            ref_sanity = ParameterSanityRules.validate_report_reference(ref_low, ref_high, param_code)
            _trace(trace, f"S8: Report reference sanity → valid={ref_sanity.valid} ({ref_sanity.reason})")

            if not ref_sanity.valid:
                _warn(warnings, page, param_name, "Invalid Reference",
                      f"Report reference range [{ref_low}, {ref_high}] is impossible: {ref_sanity.reason}. "
                      f"Falling back to STANDARD_DATABASE.")
                ref_low = None
                ref_high = None
                ref_text = None
                ref_source = "FALLBACK_FROM_REPORT"
        else:
            _trace(trace, f"S8: No report reference range")

        # Fallback to standard database if no valid report range
        if ref_low is None and ref_high is None:
            fallback = ReferenceRangeService.get_fallback_reference(param_code, age_str, gender_str)
            if fallback:
                ref_low = fallback["low"]
                ref_high = fallback["high"]
                ref_text = fallback["text"]
                ref_source = "STANDARD_DATABASE" if ref_source == "REPORT" else ref_source
                if not norm_unit and fallback.get("unit"):
                    norm_unit = fallback["unit"]
                    conv_unit = norm_unit
                _trace(trace, f"S8: Fallback reference → [{ref_low}, {ref_high}] ({ref_source})")
            else:
                ref_source = "UNKNOWN"
                _warn(warnings, page, param_name, "Missing Reference",
                      f"No reference range found in report or standard database for '{param_name}'.")
                _trace(trace, f"S8: No reference found → MISSING_REFERENCE")

        # ── Stage 9: Classification ───────────────────────────────────────
        status = "UNKNOWN"
        severity = "UNKNOWN"
        is_critical = False
        notes_parts: List[str] = []

        if compare_val is None:
            status = "INVALID"
            severity = "UNKNOWN"
            _trace(trace, f"S9: No numeric value → INVALID")

        else:
            # 9a — Critical Rules (only on validated, converted canonical value)
            crit = CriticalRulesEngine.evaluate(param_code, compare_val)
            if crit:
                status = crit["status"]
                severity = crit["severity"]
                is_critical = True
                notes_parts.append(crit["reason"])
                _trace(trace, f"S9a: CRITICAL → {status}: {crit['reason']}")
            else:
                _trace(trace, f"S9a: Not critical")

            # 9b — Range Classification (only if not already critical)
            if not is_critical:
                if ref_low is None and ref_high is None:
                    status = "MISSING_REFERENCE"
                    severity = "UNKNOWN"
                    _trace(trace, f"S9b: No reference → MISSING_REFERENCE")

                elif ref_low is not None and compare_val < ref_low:
                    status = "LOW"
                    dev = (ref_low - compare_val) / ref_low if ref_low > 0 else 0.1
                    severity = "SEVERE" if dev > 0.4 else "MODERATE" if dev > 0.2 else "MILD"
                    _trace(trace, f"S9b: {compare_val} < {ref_low} → LOW ({severity}, dev={dev:.2f})")

                elif ref_high is not None and compare_val > ref_high:
                    status = "HIGH"
                    dev = (compare_val - ref_high) / ref_high if ref_high > 0 else 0.1
                    severity = "SEVERE" if dev > 0.5 else "MODERATE" if dev > 0.2 else "MILD"
                    _trace(trace, f"S9b: {compare_val} > {ref_high} → HIGH ({severity}, dev={dev:.2f})")

                else:
                    status = "NORMAL"
                    severity = "NORMAL"
                    _trace(trace, f"S9b: In range → NORMAL")

        # 9c — Operator-aware notes for LT/GT values
        if value_operator in ("LT", "LTE"):
            notes_parts.append(f"Value reported as '{mv.value}' (less-than threshold)")
        elif value_operator in ("GT", "GTE"):
            notes_parts.append(f"Value reported as '{mv.value}' (greater-than threshold)")
        elif value_operator == "APPROX":
            notes_parts.append(f"Value reported as approximately {num_val}")

        # ── Confidence Calculation ────────────────────────────────────────
        ocr_conf = float(mv.confidence or 0.9)
        val_conf = ocr_conf   # Start from OCR confidence — NEVER exceed it

        # Reduce for reference source quality
        if ref_source in ("STANDARD_DATABASE", "FALLBACK_FROM_REPORT"):
            val_conf = val_conf * 0.95
        elif ref_source == "UNKNOWN":
            val_conf = val_conf * 0.80

        # Reduce for missing unit
        if not norm_unit:
            val_conf = val_conf * 0.85
            notes_parts.append("Unit missing — confidence reduced")

        # Reduce for conversion (slight uncertainty)
        if was_converted:
            val_conf = val_conf * 0.97

        # Low OCR confidence warning
        if ocr_conf < 0.70:
            val_conf = min(val_conf, ocr_conf)   # Hard cap
            _warn(warnings, page, param_name, "OCR Low Confidence",
                  f"OCR confidence {int(ocr_conf * 100)}% is below 70%. Validation confidence capped.")
            _trace(trace, f"Conf: OCR={ocr_conf:.2f} → val_conf capped at {val_conf:.2f}")

        val_conf = round(max(0.0, min(1.0, val_conf)), 2)
        _trace(trace, f"Final: status={status} severity={severity} critical={is_critical} conf={val_conf}")

        rec = cls._build_record(
            mv=mv, param_code=param_code,
            status=status, severity=severity, is_critical=is_critical,
            ref_low=ref_low, ref_high=ref_high, ref_text=ref_text, ref_source=ref_source,
            norm_unit=conv_unit or norm_unit,
            num_val=num_val, conv_val=conv_val if was_converted else None,
            conv_unit=conv_unit if was_converted else None,
            conv_factor=conv_factor, was_converted=was_converted,
            ocr_conf=ocr_conf, val_conf=val_conf,
            notes="; ".join(notes_parts) if notes_parts else None,
            trace=trace,
        )
        return rec, warnings

    # ─────────────────────────────────────────────────────────────────────────
    # Record builder
    # ─────────────────────────────────────────────────────────────────────────

    @classmethod
    def _build_record(
        cls, mv: MedicalValue, param_code: str,
        status: str, severity: str, is_critical: bool,
        ref_low, ref_high, ref_text, ref_source: str, norm_unit: str,
        num_val, conv_val, conv_unit, conv_factor, was_converted: bool,
        ocr_conf: float, val_conf: float,
        notes: Optional[str], trace: List[str],
    ) -> ValidatedMedicalValue:
        return ValidatedMedicalValue(
            medical_value_id=mv.id,
            report_id=mv.report_id,
            parameter_name=mv.parameter_name,
            parameter_code=param_code,
            category=mv.category or "General",
            raw_value=mv.value or "",
            validated_value=num_val,
            raw_unit=mv.unit or "",
            normalized_unit=norm_unit,
            # Conversion fields
            is_converted=was_converted,
            converted_value=conv_val,
            canonical_unit=conv_unit,
            conversion_factor=conv_factor,
            # Reference
            reference_low=ref_low,
            reference_high=ref_high,
            reference_text=ref_text,
            reference_source=ref_source,
            # Clinical
            status=status,
            severity=severity,
            critical=is_critical,
            # Confidence
            ocr_confidence=round(ocr_conf, 2),
            validation_confidence=val_conf,
            # Audit
            validation_notes=notes,
            validation_trace=" | ".join(trace),
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Data Quality Score
    # ─────────────────────────────────────────────────────────────────────────

    @classmethod
    def _compute_quality_score(
        cls,
        records: List[ValidatedMedicalValue],
        warnings: List[Dict],
        patient_rec
    ) -> Dict[str, Any]:
        if not records:
            return {"score": 0, "breakdown": {}}

        n = len(records)
        invalid = sum(1 for r in records if r.status in ("INVALID_UNIT", "INVALID_VALUE", "INVALID"))
        converted = sum(1 for r in records if r.is_converted)
        missing_ref = sum(1 for r in records if r.reference_source == "UNKNOWN")
        missing_unit = sum(1 for r in records if not r.normalized_unit)
        low_ocr = sum(1 for r in records if (r.ocr_confidence or 1.0) < 0.70)
        avg_conf = sum(r.validation_confidence for r in records) / n

        # Demographic bonus
        has_demographics = bool(patient_rec and (patient_rec.age or patient_rec.gender))

        # Score calculation (100 points)
        score = 100
        score -= (invalid / n) * 30            # Up to -30 for invalid values
        score -= (missing_ref / n) * 15        # Up to -15 for missing references
        score -= (missing_unit / n) * 10       # Up to -10 for missing units
        score -= (low_ocr / n) * 15            # Up to -15 for low OCR confidence
        score -= (1 - avg_conf) * 20           # Up to -20 for low validation confidence
        if not has_demographics:
            score -= 5                          # -5 if no age/gender

        score = max(0, min(100, round(score)))

        breakdown = {
            "total_parameters": n,
            "valid": n - invalid,
            "invalid": invalid,
            "converted": converted,
            "missing_references": missing_ref,
            "missing_units": missing_unit,
            "low_ocr_confidence_count": low_ocr,
            "average_validation_confidence": round(avg_conf, 2),
            "has_demographics": has_demographics,
            "total_warnings": len(warnings),
        }

        return {"score": score, "breakdown": breakdown}

    # ─────────────────────────────────────────────────────────────────────────
    # Read / Summary helpers
    # ─────────────────────────────────────────────────────────────────────────

    @classmethod
    def get_validated_data(cls, db: Session, report: Report) -> Dict[str, Any]:
        records = db.query(ValidatedMedicalValue).filter(
            ValidatedMedicalValue.report_id == report.id
        ).order_by(ValidatedMedicalValue.id).all()

        summary = cls.get_validation_summary(db, report)

        list_out = []
        for r in records:
            list_out.append({
                "id": r.id,
                "medical_value_id": r.medical_value_id,
                "report_id": r.report_id,
                "parameter_name": r.parameter_name,
                "parameter_code": r.parameter_code,
                "category": r.category,
                # Values
                "raw_value": r.raw_value,
                "validated_value": r.validated_value,
                "raw_unit": r.raw_unit,
                "normalized_unit": r.normalized_unit,
                # Conversion
                "is_converted": r.is_converted,
                "converted_value": r.converted_value,
                "canonical_unit": r.canonical_unit,
                "conversion_factor": r.conversion_factor,
                # Reference
                "reference_low": r.reference_low,
                "reference_high": r.reference_high,
                "reference_text": r.reference_text,
                "reference_source": r.reference_source,
                # Clinical
                "status": r.status,
                "severity": r.severity,
                "critical": r.critical,
                # Confidence
                "ocr_confidence": r.ocr_confidence,
                "validation_confidence": r.validation_confidence,
                # Audit
                "validation_notes": r.validation_notes,
                "validation_trace": r.validation_trace,
            })

        return {
            "report_id": report.id,
            "status": "completed" if list_out else "no_data",
            "total_parameters": len(list_out),
            "validated_parameters": len(list_out),
            "summary": summary,
            "validated_values": list_out,
        }

    @classmethod
    def get_validation_summary(cls, db: Session, report: Report) -> Dict[str, Any]:
        records = db.query(ValidatedMedicalValue).filter(
            ValidatedMedicalValue.report_id == report.id
        ).all()
        warn_count = db.query(ParseWarning).filter(
            ParseWarning.report_id == report.id
        ).count()

        counts = {
            "normal": 0, "low": 0, "high": 0, "critical": 0,
            "unknown": 0, "invalid": 0, "qualitative": 0, "warnings": warn_count,
        }
        total_conf = 0.0

        for r in records:
            total_conf += r.validation_confidence or 0.0
            st = (r.status or "").upper()
            if r.critical or "CRITICAL" in st:
                counts["critical"] += 1
            elif st == "NORMAL":
                counts["normal"] += 1
            elif st == "LOW":
                counts["low"] += 1
            elif st == "HIGH":
                counts["high"] += 1
            elif st == "QUALITATIVE":
                counts["qualitative"] += 1
            elif st in ("INVALID_UNIT", "INVALID_VALUE", "INVALID"):
                counts["invalid"] += 1
            else:
                counts["unknown"] += 1

        avg_conf = round(total_conf / max(len(records), 1), 2)
        counts["overall_validation_confidence"] = avg_conf
        return counts
