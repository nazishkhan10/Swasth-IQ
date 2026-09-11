"""
Patient Parser Service.
Extracts patient demographics and report header metadata from OCR text blocks.
"""

import re
from typing import Dict, Any, List

class PatientParser:
    """Parses Patient Name, Age, Gender, Lab Name, Doctor Name, Report Date, Accession Number."""

    @classmethod
    def parse(cls, blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        full_text = "\n".join([b.get("text", "") for b in blocks if b.get("text")])

        result = {
            "patient_name": None,
            "age": None,
            "gender": None,
            "lab_name": None,
            "doctor_name": None,
            "report_date": None,
            "sample_date": None,
            "accession_number": None,
            "confidence": 0.90
        }

        # 1. Patient Name
        name_match = re.search(r"(?:patient\s*name|patient|pt\.?\s*name|name)\s*[:\-]\s*(?:mr\.|mrs\.|ms\.|dr\.)?\s*([A-Za-z\s\.]+)", full_text, re.IGNORECASE)
        if name_match:
            candidate = name_match.group(1).strip()
            candidate = candidate.split("\n")[0].strip()
            # Strip trailing labels like Barcode, ID, Visit, Age, Gender, Date
            candidate = re.split(r"\s+(?:barcode|id|visit|report|age|gender|sex|date|ref|dr|bmi|collection)\b", candidate, flags=re.IGNORECASE)[0].strip()
            # Clean extra spaces
            candidate = " ".join(candidate.split())
            if len(candidate) > 2 and candidate.lower() not in ["report", "test", "name"]:
                result["patient_name"] = candidate.title()
        
        if not result["patient_name"]:
            salutation_match = re.search(r"\b(mr\.|mrs\.|ms\.)\s+([A-Za-z\s]+)", full_text, re.IGNORECASE)
            if salutation_match:
                candidate = f"{salutation_match.group(1)} {salutation_match.group(2)}".strip()
                candidate = candidate.split("\n")[0].strip()
                candidate = re.split(r"\s+(?:barcode|id|visit|report|age|gender|sex|date|ref|dr)\b", candidate, flags=re.IGNORECASE)[0].strip()
                candidate = " ".join(candidate.split())
                result["patient_name"] = candidate.title()

        # 2. Age & Gender
        age_match = re.search(r"\b(\d+)\s*(?:yrs?|years?|y/o)\b", full_text, re.IGNORECASE)
        if age_match:
            result["age"] = f"{age_match.group(1)} Years"

        gender_match = re.search(r"\b(male|female)\b", full_text, re.IGNORECASE)
        if gender_match:
            result["gender"] = gender_match.group(1).capitalize()

        # 3. Doctor
        doc_match = re.search(r"(?:ref\s*by|referred\s*by|ordering\s*doctor|ordering\s*physician|doctor|dr\.?)\s*[:\-]\s*([A-Za-z\s\.]+)", full_text, re.IGNORECASE)
        if doc_match:
            doc_name = doc_match.group(1).strip()
            doc_name = doc_name.split("\n")[0].strip()
            doc_name = re.split(r"\s+(?:date|lab|age|sample|report|analyzing)\b", doc_name, flags=re.IGNORECASE)[0].strip()
            doc_name = " ".join(doc_name.split())
            if len(doc_name) > 2 and "self" not in doc_name.lower():
                result["doctor_name"] = doc_name if doc_name.lower().startswith("dr") else f"Dr. {doc_name.title()}"

        # 4. Lab / Hospital Name
        lab_match = re.search(r"^([A-Z0-9\s\.\-]{5,40}\s*(?:DIAGNOSTICS|LABORATORIES|HOSPITAL|LABS|CLINIC))", full_text, re.IGNORECASE | re.MULTILINE)
        if lab_match:
            result["lab_name"] = " ".join(lab_match.group(1).strip().title().split())

        # 5. Report Date / Collection Time
        dates = re.findall(r"\b\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2}\b|\b\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}\b", full_text)
        if dates:
            result["report_date"] = dates[0]
            if len(dates) > 1:
                result["sample_date"] = dates[1]

        # 6. Accession Number / Patient ID
        acc_match = re.search(r"(?:patient\s*id|id|acc(?:ession)?\s*(?:no|id)?|sample\s*id|reg\s*no|pid)\s*[:\-]\s*([A-Za-z0-9\-_]+)", full_text, re.IGNORECASE)
        if acc_match:
            result["accession_number"] = acc_match.group(1).strip()

        filled = sum(1 for k, v in result.items() if v is not None and k != "confidence")
        result["confidence"] = min(0.95, round(0.50 + (filled * 0.08), 2))

        return result
