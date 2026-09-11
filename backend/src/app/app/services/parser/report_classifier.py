"""
Report Classifier Service.
Analyzes full OCR text to classify document type (e.g. CBC, LFT, KFT, Lipid, Sugar, Thyroid, Vitamin, Urine, Mixed Panel, or Longitudinal Patient Tracking).
"""

from typing import List, Dict, Any

class ReportClassifier:
    """Classifies document type by matching keyword distributions against known panel headers and parameters."""

    PANEL_KEYWORDS = {
        "CBC": [
            "hemoglobin", "haemoglobin", "complete blood count", "cbc", "rbc", "wbc", "platelet", 
            "hematocrit", "pcv", "dlc", "tlc", "mcv", "mch", "mchc", "neutrophils", "lymphocytes"
        ],
        "LFT": [
            "liver function", "lft", "sgpt", "sgot", "alt", "ast", "alkaline phosphatase", "bilirubin", 
            "albumin", "globulin", "total protein"
        ],
        "KFT": [
            "kidney function", "renal function", "kft", "rft", "creatinine", "egfr", "blood urea", "bun", 
            "uric acid", "sodium", "potassium", "chloride"
        ],
        "Lipid": [
            "lipid profile", "lipid", "cholesterol", "triglycerides", "hdl", "ldl", "vldl", "hs-crp"
        ],
        "Sugar": [
            "blood sugar", "fasting glucose", "pp glucose", "rbs", "fbs", "hba1c", "glycated hemoglobin", "glycosylated hemoglobin"
        ],
        "Thyroid": [
            "thyroid profile", "tsh", "t3", "t4", "free t3", "free t4", "triiodothyronine", "thyroxine"
        ],
        "Vitamin": [
            "vitamin d", "25-oh", "vitamin b12", "cyanocobalamin"
        ],
        "Urine": [
            "urine routine", "urinalysis", "urine protein", "urine sugar", "specific gravity", "ketones"
        ]
    }

    @classmethod
    def classify(cls, full_text: str) -> str:
        text_lower = full_text.lower()

        # Check explicit longitudinal tracking title first
        if any(k in text_lower for k in ["longitudinal", "patient tracking", "tracking period", "total visits", "baseline encounter", "follow-up encounter"]):
            return "Longitudinal Patient Tracking Report"

        # Check explicit panel titles
        if "comprehensive" in text_lower and any(k in text_lower for k in ["metabolic", "lipid", "renal"]):
            return "Mixed Panel (Metabolic, Lipid & Renal)"

        category_scores: Dict[str, int] = {cat: 0 for cat in cls.PANEL_KEYWORDS}

        for category, keywords in cls.PANEL_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    category_scores[category] += 1

        sorted_scores = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        top_category, top_score = sorted_scores[0]

        if top_score == 0:
            return "General Laboratory Report"

        # Check if multiple panels are heavily present (Mixed Panel)
        active_categories = [cat for cat, score in sorted_scores if score >= 2]
        if len(active_categories) > 1:
            return f"Mixed Panel ({', '.join(active_categories[:3])})"

        return top_category
