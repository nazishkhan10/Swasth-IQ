"""
Recommendation Template Registry (Phase 6).
Stores structured recommendation definitions organized by clinical triage levels.
"""

from typing import Dict, Any, List

RECOMMENDATION_TEMPLATES: Dict[str, Dict[str, Any]] = {
    # ── CRITICAL / IMMEDIATE ──────────────────────────────────────────────
    "REC_DM_ENDOCRINE": {
        "id": "REC_DM_ENDOCRINE",
        "title": "Urgent Endocrinology Consultation & Glycemic Stabilization",
        "category": "Doctor Consultation",
        "priority": "CRITICAL",
        "triage_level": "Immediate",
        "action": "Schedule urgent endocrinology consultation for anti-diabetic medication adjustment.",
        "rationale": "High HbA1c / glucose indicates therapy failure and high vascular complication risk."
    },
    "REC_CKD_NEPHROLOGIST": {
        "id": "REC_CKD_NEPHROLOGIST",
        "title": "Nephrology Specialist Evaluation & CKD Management",
        "category": "Doctor Consultation",
        "priority": "CRITICAL",
        "triage_level": "Immediate",
        "action": "Refer to nephrologist for comprehensive renal function evaluation and nephroprotective regimen.",
        "rationale": "Impaired eGFR and elevated creatinine signify progressive loss of nephron clearance capacity."
    },
    "REC_ANEMIA_HAEMATOLOGY": {
        "id": "REC_ANEMIA_HAEMATOLOGY",
        "title": "Hematology Evaluation for Severe Anemia",
        "category": "Doctor Consultation",
        "priority": "CRITICAL",
        "triage_level": "Immediate",
        "action": "Urgent medical evaluation for severe hemoglobin drop.",
        "rationale": "Critical reduction in oxygen carrying capacity requires immediate clinical intervention."
    },

    # ── HIGH / URGENT ─────────────────────────────────────────────────────
    "REC_THYROID_ENDOCRINE": {
        "id": "REC_THYROID_ENDOCRINE",
        "title": "Endocrine Evaluation for Thyroid Dysfunction",
        "category": "Doctor Consultation",
        "priority": "HIGH",
        "triage_level": "Urgent",
        "action": "Consult physician for thyroid function assessment and hormone therapy evaluation.",
        "rationale": "Abnormal TSH level alters systemic basal metabolic rate and cardiovascular physiology."
    },
    "REC_LIPID_CARDIOLOGY": {
        "id": "REC_LIPID_CARDIOLOGY",
        "title": "Cardiovascular Risk Stratification & Lipid Management",
        "category": "Doctor Consultation",
        "priority": "HIGH",
        "triage_level": "Urgent",
        "action": "Discuss lipid-lowering pharmacotherapy (e.g., statin) and cardiovascular risk profiling.",
        "rationale": "Elevated LDL-C and Total Cholesterol accelerate coronary artery plaque formation."
    },

    # ── MEDIUM / ROUTINE & LIFESTYLE ──────────────────────────────────────
    "REC_DM_DIET": {
        "id": "REC_DM_DIET",
        "title": "Low-Glycemic Medical Nutrition Therapy",
        "category": "Nutrition",
        "priority": "MEDIUM",
        "triage_level": "Routine",
        "action": "Adopt a low-glycemic index, fiber-rich diet with controlled carbohydrate intake.",
        "rationale": "Dietary modification minimizes postprandial glucose spikes and improves insulin sensitivity."
    },
    "REC_LIPID_DIET": {
        "id": "REC_LIPID_DIET",
        "title": "Heart-Healthy Low Saturated Fat Diet",
        "category": "Nutrition",
        "priority": "MEDIUM",
        "triage_level": "Routine",
        "action": "Reduce dietary saturated fats, trans-fats, and dietary cholesterol; increase soluble fiber.",
        "rationale": "Nutritional intake directly modulates hepatic VLDL assembly and LDL clearance."
    },
    "REC_LIPID_EXERCISE": {
        "id": "REC_LIPID_EXERCISE",
        "title": "Aerobic Exercise & Physical Activity Plan",
        "category": "Exercise",
        "priority": "MEDIUM",
        "triage_level": "Routine",
        "action": "Engage in at least 150 minutes per week of moderate-intensity aerobic physical activity.",
        "rationale": "Regular exercise increases HDL-C and enhances muscular glucose uptake."
    },
    "REC_PREDM_LIFESTYLE": {
        "id": "REC_PREDM_LIFESTYLE",
        "title": "Prediabetes Lifestyle Modification Program",
        "category": "Lifestyle",
        "priority": "MEDIUM",
        "triage_level": "Routine",
        "action": "Target 5-7% body weight reduction through dietary restriction and regular exercise.",
        "rationale": "Modest weight reduction prevents or delays onset of overt Type 2 Diabetes by 58%."
    },
    "REC_VITD_SUPPLEMENT": {
        "id": "REC_VITD_SUPPLEMENT",
        "title": "Vitamin D3 Supplementation",
        "category": "Medication Discussion",
        "priority": "MEDIUM",
        "triage_level": "Routine",
        "action": "Discuss oral Vitamin D3 (Cholecalciferol) supplementation with your physician.",
        "rationale": "Restoring serum 25-OH Vitamin D > 30 ng/mL optimizes calcium homeostasis and bone health."
    },
    "REC_ANEMIA_IRON": {
        "id": "REC_ANEMIA_IRON",
        "title": "Iron & Hematinic Evaluation",
        "category": "Medication Discussion",
        "priority": "MEDIUM",
        "triage_level": "Routine",
        "action": "Order serum ferritin, iron, and total iron-binding capacity (TIBC) panel.",
        "rationale": "Identifies iron deficiency vs anemia of chronic disease."
    },

    # ── MONITORING / REPEAT TESTS ─────────────────────────────────────────
    "REC_DM_MONITOR": {
        "id": "REC_DM_MONITOR",
        "title": "Repeat Glycemic Profile in 3 Months",
        "category": "Follow-up Tests",
        "priority": "LOW",
        "triage_level": "Monitoring",
        "action": "Repeat HbA1c and fasting blood glucose testing in 90 days.",
        "rationale": "Reflects mean erythrocyte glucose exposure over the preceding 120-day lifespan."
    },
    "REC_CKD_MONITOR": {
        "id": "REC_CKD_MONITOR",
        "title": "Monitor Renal Clearance & Electrolytes in 1-3 Months",
        "category": "Follow-up Tests",
        "priority": "LOW",
        "triage_level": "Monitoring",
        "action": "Recheck serum creatinine, eGFR, and electrolytes in 30-90 days.",
        "rationale": "Tracks trajectory of renal filtration stability vs acute decline."
    },
    "REC_CKD_HYDRATION": {
        "id": "REC_CKD_HYDRATION",
        "title": "Adequate Hydration & Avoid Nephrotoxins",
        "category": "Lifestyle",
        "priority": "MEDIUM",
        "triage_level": "Routine",
        "action": "Maintain optimal fluid intake and avoid over-the-counter NSAIDs (e.g., ibuprofen).",
        "rationale": "NSAIDs inhibit renal prostaglandins causing prerenal hypoperfusion."
    },
    "REC_THYROID_FULL_PANEL": {
        "id": "REC_THYROID_FULL_PANEL",
        "title": "Complete Thyroid Panel (Free T3, Free T4, Anti-TPO)",
        "category": "Follow-up Tests",
        "priority": "LOW",
        "triage_level": "Monitoring",
        "action": "Order serum Free T3, Free T4, and Thyroid Peroxidase antibodies.",
        "rationale": "Differentiates primary pituitary vs thyroid gland pathology and autoimmune etiology."
    },
    "REC_VITD_SUN": {
        "id": "REC_VITD_SUN",
        "title": "Safe Sun Exposure & Dietary Vitamin D Intake",
        "category": "Lifestyle",
        "priority": "LOW",
        "triage_level": "Informational",
        "action": "Increase dietary intake of fortified dairy, fatty fish, and safe sunlight exposure.",
        "rationale": "Ultraviolet B radiation converts 7-dehydrocholesterol in skin to Vitamin D3."
    },
    "REC_VITD_RECHECK": {
        "id": "REC_VITD_RECHECK",
        "title": "Recheck Vitamin D (25-OH) Level in 3 Months",
        "category": "Follow-up Tests",
        "priority": "LOW",
        "triage_level": "Monitoring",
        "action": "Repeat 25-OH Vitamin D blood test after 12 weeks of therapy.",
        "rationale": "Verifies therapeutic repletion into optimal target window (30-60 ng/mL)."
    },
    "REC_INFLAM_INVESTIGATE": {
        "id": "REC_INFLAM_INVESTIGATE",
        "title": "Clinical Investigation of Inflammatory Biomarker Elevation",
        "category": "Doctor Consultation",
        "priority": "MEDIUM",
        "triage_level": "Routine",
        "action": "Evaluate potential infectious, metabolic, or autoimmune drivers of elevated hs-CRP.",
        "rationale": "Persistent systemic inflammation accelerates endothelial injury."
    },
    "REC_INFLAM_MONITOR": {
        "id": "REC_INFLAM_MONITOR",
        "title": "Recheck Inflammatory Markers (hs-CRP / ESR) in 4-6 Weeks",
        "category": "Follow-up Tests",
        "priority": "LOW",
        "triage_level": "Monitoring",
        "action": "Repeat hs-CRP measurement in 4 to 6 weeks.",
        "rationale": "Assesses whether inflammatory elevation is transient vs chronic."
    },
    "REC_PREDM_MONITOR": {
        "id": "REC_PREDM_MONITOR",
        "title": "Annual Prediabetes Screening",
        "category": "Follow-up Tests",
        "priority": "LOW",
        "triage_level": "Monitoring",
        "action": "Repeat HbA1c and fasting blood glucose annually.",
        "rationale": "Detects early conversion from prediabetes to overt Type 2 Diabetes."
    },
    # ── ROUTINE WELLNESS & CBC TEMPLATES ──────────────────────────────────
    "REC_WELLNESS_ANNUAL": {
        "id": "REC_WELLNESS_ANNUAL",
        "title": "Annual Preventive Health & Lab Screening",
        "category": "Follow-up Tests",
        "priority": "INFORMATIONAL",
        "triage_level": "Monitoring",
        "action": "Schedule an annual routine clinical checkup and basic metabolic panel.",
        "rationale": "Routine monitoring detects subclinical metabolic, renal, or hematologic shifts early."
    },
    "REC_WELLNESS_HYDRATION": {
        "id": "REC_WELLNESS_HYDRATION",
        "title": "Balanced Dietary Intake & Optimal Hydration",
        "category": "Nutrition",
        "priority": "INFORMATIONAL",
        "triage_level": "Routine",
        "action": "Maintain 2-2.5L daily water intake and a micronutrient-dense balanced diet.",
        "rationale": "Supports optimal plasma volume, renal clearance, and cellular metabolism."
    },
    "REC_WELLNESS_EXERCISE": {
        "id": "REC_WELLNESS_EXERCISE",
        "title": "Regular Aerobic Exercise & Physical Activity",
        "category": "Exercise",
        "priority": "INFORMATIONAL",
        "triage_level": "Routine",
        "action": "Aim for at least 150 minutes of moderate physical activity per week.",
        "rationale": "Enhances cardiovascular resilience, insulin sensitivity, and immune function."
    },
    "REC_CBC_MONITOR": {
        "id": "REC_CBC_MONITOR",
        "title": "Routine Hematologic Monitoring",
        "category": "Follow-up Tests",
        "priority": "INFORMATIONAL",
        "triage_level": "Monitoring",
        "action": "Maintain periodic annual Complete Blood Count (CBC) monitoring.",
        "rationale": "Ensures stable erythropoiesis, leukocyte immune defense, and thrombocyte parameters."
    }
}

