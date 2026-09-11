"""
Document Loader (Phase 7 RAG Engine).
Curates authoritative medical guidelines, laboratory reference databases, disease criteria,
clinical nutrition, exercise protocols, drug information, and emergency guidance.
Each document chunk contains 5-tier priority metadata:
Priority 1: WHO, ICMR, CDC, NICE Guidelines
Priority 2: Peer-reviewed journals
Priority 3: Medical Textbooks
Priority 4: Lifestyle/Nutrition manuals
Priority 5: Medical terminology dictionaries
"""

from typing import List, Dict, Any


class DocumentLoader:
    """Provides structured medical knowledge base across 8 isolated collections."""

    _KNOWLEDGE_VERSION = "2026.1"

    @classmethod
    def get_all_documents(cls) -> List[Dict[str, Any]]:
        """Returns all pre-curated medical knowledge chunks."""

        docs = []

        # ── 1. MEDICAL GUIDELINES (Priority 1) ──────────────────────────────
        docs.extend([
            {
                "id": "GUIDE_ADA_DM2_2026",
                "collection": "medical_guidelines",
                "title": "ADA Standards of Care in Diabetes (2026 Update)",
                "content": (
                    "Diabetes Mellitus Type 2 is diagnosed when HbA1c is >= 6.5% or Fasting Blood Glucose is >= 126 mg/dL. "
                    "Glycemic target for most non-pregnant adults is HbA1c < 7.0%. HbA1c >= 8.0% indicates uncontrolled "
                    "glycemia requiring urgent therapeutic escalation or dual oral therapy. Regular SMBG monitoring and "
                    "lifestyle interventions (mediterranean diet, 150 min/week moderate physical activity) are recommended."
                ),
                "metadata": {
                    "source": "American Diabetes Association (ADA)",
                    "priority": 1,
                    "version": cls._KNOWLEDGE_VERSION,
                    "specialty": "Endocrinology",
                    "country": "Global",
                    "language": "English"
                }
            },
            {
                "id": "GUIDE_KDIGO_CKD_2026",
                "collection": "medical_guidelines",
                "title": "KDIGO Clinical Practice Guideline for CKD Evaluation & Management",
                "content": (
                    "Chronic Kidney Disease (CKD) Stage 3a is defined by eGFR between 45 and 59 mL/min/1.73m² persisting for > 3 months. "
                    "Serum Creatinine levels above 1.35 mg/dL indicate decreased renal clearance. Nephrology consultation is recommended "
                    "for eGFR < 60 mL/min/1.73m². Strict blood pressure control (< 130/80 mmHg), avoidance of nephrotoxic drugs (NSAIDs), "
                    "and protein intake moderate limitation (0.8 g/kg/day) are essential to prevent CKD progression."
                ),
                "metadata": {
                    "source": "KDIGO / NICE Guidelines",
                    "priority": 1,
                    "version": cls._KNOWLEDGE_VERSION,
                    "specialty": "Nephrology",
                    "country": "Global",
                    "language": "English"
                }
            },
            {
                "id": "GUIDE_ATA_THYROID_2026",
                "collection": "medical_guidelines",
                "title": "American Thyroid Association Guidelines for Subclinical Hypothyroidism",
                "content": (
                    "Subclinical hypothyroidism is characterized by serum TSH concentrations above the reference ceiling (typically > 4.5 uIU/mL) "
                    "with normal serum Free T4 levels. TSH between 4.5 and 10 uIU/mL warrants monitoring every 3-6 months and evaluation for "
                    "thyroid peroxidase (Anti-TPO) autoantibodies. Symptoms include fatigue, weight gain, cold intolerance, and dyslipidemia."
                ),
                "metadata": {
                    "source": "American Thyroid Association (ATA)",
                    "priority": 1,
                    "version": cls._KNOWLEDGE_VERSION,
                    "specialty": "Endocrinology",
                    "country": "Global",
                    "language": "English"
                }
            },
            {
                "id": "GUIDE_ACC_LIPID_2026",
                "collection": "medical_guidelines",
                "title": "ACC/AHA Guideline on the Management of Blood Cholesterol",
                "content": (
                    "Total Cholesterol >= 240 mg/dL and LDL-C >= 160 mg/dL indicate high cardiovascular risk. First-line therapy for elevated "
                    "LDL-C includes dietary saturated fat reduction (< 7% of total calories), elimination of trans fats, increased soluble fiber, "
                    "and statin therapy based on overall 10-year ASCVD risk stratification."
                ),
                "metadata": {
                    "source": "ACC / AHA Guidelines",
                    "priority": 1,
                    "version": cls._KNOWLEDGE_VERSION,
                    "specialty": "Cardiology",
                    "country": "Global",
                    "language": "English"
                }
            }
        ])

        # ── 2. LABORATORY REFERENCE (Priority 1) ────────────────────────────
        docs.extend([
            {
                "id": "LAB_REF_HBA1C",
                "collection": "lab_reference",
                "title": "HbA1c Laboratory Interpretation Standards",
                "content": (
                    "HbA1c reflects average blood glucose over the preceding 2-3 months. Normal: < 5.7%. Prediabetes: 5.7% - 6.4%. "
                    "Diabetes: >= 6.5%. Critical High: >= 8.0%. Spurious HbA1c elevation can occur with iron deficiency anemia or hemoglobinopathies."
                ),
                "metadata": {
                    "source": "ICMR / WHO Lab Reference Manual",
                    "priority": 1,
                    "version": cls._KNOWLEDGE_VERSION,
                    "specialty": "Pathology",
                    "country": "India/Global",
                    "language": "English"
                }
            },
            {
                "id": "LAB_REF_CREAT_EGFR",
                "collection": "lab_reference",
                "title": "Renal Function Tests (Creatinine & eGFR Interpretation)",
                "content": (
                    "Serum Creatinine reference range: 0.7 - 1.35 mg/dL. Elevated creatinine indicates reduced glomerular filtration. "
                    "eGFR (CKD-EPI 2021 formula) > 90 is normal; 60-89 indicates mildly decreased GFR; 45-59 indicates mild-to-moderate CKD (Stage 3a); "
                    "< 15 indicates Kidney Failure (Stage 5)."
                ),
                "metadata": {
                    "source": "NKDEP / ICMR Guidelines",
                    "priority": 1,
                    "version": cls._KNOWLEDGE_VERSION,
                    "specialty": "Nephrology",
                    "country": "Global",
                    "language": "English"
                }
            }
        ])

        # ── 3. DISEASES (Priority 2) ───────────────────────────────────────
        docs.extend([
            {
                "id": "DIS_DM2_SYMPTOMS",
                "collection": "diseases",
                "title": "Type 2 Diabetes Mellitus Clinical Profile",
                "content": (
                    "Type 2 Diabetes involves progressive insulin resistance and beta-cell dysfunction. Classic symptoms include polyuria, polydipsia, "
                    "unexplained weight loss, blurred vision, and slow wound healing. Long-term complications affect microvascular (retinopathy, "
                    "nephropathy, neuropathy) and macrovascular (coronary artery disease, stroke) systems."
                ),
                "metadata": {
                    "source": "Harrison's Principles of Internal Medicine",
                    "priority": 2,
                    "version": cls._KNOWLEDGE_VERSION,
                    "specialty": "Endocrinology",
                    "country": "Global",
                    "language": "English"
                }
            }
        ])

        # ── 4. NUTRITION (Priority 4) ───────────────────────────────────────
        docs.extend([
            {
                "id": "NUT_DIABETES_CKD",
                "collection": "nutrition",
                "title": "Medical Nutrition Therapy for Diabetic Kidney Disease",
                "content": (
                    "Patients with concurrent Diabetes and Stage 3 CKD require tailored nutrition: limit daily sodium intake to < 2,000 mg, "
                    "avoid added refined sugars, consume low-glycemic index carbohydrates (whole grains, pulses), maintain controlled protein intake "
                    "(0.8 g/kg body weight), and limit processed foods high in inorganic phosphorus."
                ),
                "metadata": {
                    "source": "Clinical Nutrition Guidelines for CKD",
                    "priority": 4,
                    "version": cls._KNOWLEDGE_VERSION,
                    "specialty": "Dietetics",
                    "country": "Global",
                    "language": "English"
                }
            }
        ])

        # ── 5. EXERCISE (Priority 4) ────────────────────────────────────────
        docs.extend([
            {
                "id": "EXE_METABOLIC",
                "collection": "exercise",
                "title": "Physical Activity & Exercise Prescription in Metabolic Risk",
                "content": (
                    "Engage in at least 150 minutes of moderate-intensity aerobic exercise per week (e.g., brisk walking, swimming, cycling) "
                    "spread over 3-5 days. Resistance training 2 days/week improves muscle insulin sensitivity. Patients with CKD or hypertension "
                    "should avoid heavy isometric straining and maintain adequate pre- and post-workout hydration."
                ),
                "metadata": {
                    "source": "American College of Sports Medicine (ACSM)",
                    "priority": 4,
                    "version": cls._KNOWLEDGE_VERSION,
                    "specialty": "Sports Medicine",
                    "country": "Global",
                    "language": "English"
                }
            }
        ])

        # ── 6. EMERGENCY GUIDANCE (Priority 1) ─────────────────────────────
        docs.extend([
            {
                "id": "EMERG_RED_FLAGS",
                "collection": "emergency",
                "title": "Clinical Red Flags & Emergency Triage Symptoms",
                "content": (
                    "Immediate emergency medical attention (ER / 911 / 112) is required if experiencing acute severe shortness of breath, "
                    "chest pain radiating to arm or jaw, sudden severe headache, acute confusion, severe vomiting with inability to keep fluids down, "
                    "anuria (no urination for > 12 hours), or blood glucose > 400 mg/dL with ketones."
                ),
                "metadata": {
                    "source": "Emergency Medicine Protocol (CDC / WHO)",
                    "priority": 1,
                    "version": cls._KNOWLEDGE_VERSION,
                    "specialty": "Emergency Medicine",
                    "country": "Global",
                    "language": "English"
                }
            }
        ])

        return docs
