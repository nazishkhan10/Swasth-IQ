"""
Central Parameter Dictionary for Medical Report Extraction.
Contains canonical names, parameter codes, categories, aliases, and expected units.
Order matters: Specific multi-word parameters (e.g. Troponin I, LDL Cholesterol, Blood Urea Nitrogen, Glycosylated Hemoglobin) are placed before general ones.
"""

PARAMETER_DICTIONARY = [
    # ── Cardiac Markers ────────────────────────────────────────────────────────
    {
        "code": "TROP_I",
        "name": "High-Sensitivity Troponin I",
        "category": "Cardiac",
        "aliases": [
            r"\bhigh\s*-\s*sensitivity\s*troponin\s*i\b", r"\bhs\s*-\s*troponin\s*i\b", r"\btroponin\s*i\b", r"\bhs\s*-\s*tnic\b"
        ],
        "expected_units": ["pg/mL", "ng/mL", "ng/L"]
    },

    # ── Blood Sugar / HbA1c ───────────────────────────────────────────────────
    {
        "code": "HBA1C",
        "name": "HbA1c",
        "category": "Sugar",
        "aliases": [
            r"\bhba1c\b", r"\bglycosylated\s*hemoglobin\b", r"\bglycated\s*hemoglobin\b", r"\bhemoglobin\s*a1c\b", r"\bglycosylated\s*hemoglobin\s*\(hba1c\)\b"
        ],
        "expected_units": ["%", "mmol/mol", "ng/dL"]
    },
    {
        "code": "GLU_FAST",
        "name": "Fasting Blood Glucose",
        "category": "Sugar",
        "aliases": [
            r"\bfasting\s*blood\s*glucose\b", r"\bfasting\s*plasma\s*glucose\b", r"\bfglucose\b", r"\bfasting\s*glucose\b", r"\bfasting\s*blood\s*sugar\b", r"\bfbs\b", r"\bserum\s*fasting\s*glucose\b"
        ],
        "expected_units": ["mg/dL", "mmol/L"]
    },
    {
        "code": "GLU_PP",
        "name": "Post Prandial Blood Sugar",
        "category": "Sugar",
        "aliases": [
            r"\bpp\s*glucose\b", r"\bpost\s*prandial\s*blood\s*sugar\b", r"\bppbs\b"
        ],
        "expected_units": ["mg/dL"]
    },
    {
        "code": "GLU_RAND",
        "name": "Random Blood Glucose",
        "category": "Sugar",
        "aliases": [
            r"\brandom\s*blood\s*sugar\b", r"\brbs\b", r"\brandom\s*glucose\b"
        ],
        "expected_units": ["mg/dL"]
    },

    # ── Lipid Profile ──────────────────────────────────────────────────────────
    {
        "code": "LDL",
        "name": "LDL Cholesterol",
        "category": "Lipid",
        "aliases": [
            r"\bldl\b", r"\bldl\s*cholesterol\b", r"\bldl\s*-\s*c\b", r"\blow\s*density\s*lipoprotein\b"
        ],
        "expected_units": ["mg/dL"]
    },
    {
        "code": "HDL",
        "name": "HDL Cholesterol",
        "category": "Lipid",
        "aliases": [
            r"\bhdl\b", r"\bhdl\s*cholesterol\b", r"\bhigh\s*density\s*lipoprotein\b"
        ],
        "expected_units": ["mg/dL"]
    },
    {
        "code": "VLDL",
        "name": "VLDL Cholesterol",
        "category": "Lipid",
        "aliases": [
            r"\bvldl\b", r"\bvldl\s*cholesterol\b"
        ],
        "expected_units": ["mg/dL"]
    },
    {
        "code": "CHOL",
        "name": "Total Cholesterol",
        "category": "Lipid",
        "aliases": [
            r"\btotal\s*cholesterol\b", r"\btotal\s*chol\b", r"^cholesterol$", r"\bserum\s*cholesterol\b"
        ],
        "expected_units": ["mg/dL", "mmol/L"]
    },
    {
        "code": "TRIG",
        "name": "Triglycerides",
        "category": "Lipid",
        "aliases": [
            r"\btriglycerides?\b", r"\bserum\s*triglycerides?\b"
        ],
        "expected_units": ["mg/dL"]
    },
    {
        "code": "HS_CRP",
        "name": "hs-CRP",
        "category": "Lipid",
        "aliases": [
            r"\bhs\s*-\s*crp\b", r"\bhscrp\b", r"\bhigh\s*sensitivity\s*c\s*-\s*reactive\s*protein\b", r"\bc\s*-\s*reactive\s*protein\b"
        ],
        "expected_units": ["mg/L", "mg/dL"]
    },

    # ── KFT / RFT ─────────────────────────────────────────────────────────────
    {
        "code": "BUN",
        "name": "BUN (Blood Urea Nitrogen)",
        "category": "KFT",
        "aliases": [
            r"\bbun\b", r"\bblood\s*urea\s*nitrogen\b", r"\bblood\s*urea\s*nitrogen\s*\(bun\)\b"
        ],
        "expected_units": ["mg/dL"]
    },
    {
        "code": "CREAT",
        "name": "Serum Creatinine",
        "category": "KFT",
        "aliases": [
            r"\bcreatinine\b", r"\bserum\s*creatinine\b", r"\bcreat\b"
        ],
        "expected_units": ["mg/dL", "µmol/L"]
    },
    {
        "code": "EGFR",
        "name": "eGFR",
        "category": "KFT",
        "aliases": [
            r"\begfr\b", r"\bestimated\s*gfr\b", r"\begfr\s*\(ckd\-epi\s*\d*\)\b"
        ],
        "expected_units": ["mL/min/1.73m2", "mL/min"]
    },
    {
        "code": "UREA",
        "name": "Blood Urea",
        "category": "KFT",
        "aliases": [
            r"^blood\s*urea$", r"^urea$", r"\bserum\s*urea\b", r"\bserum\s*blood\s*urea\b"
        ],
        "expected_units": ["mg/dL"]
    },
    {
        "code": "URIC",
        "name": "Uric Acid",
        "category": "KFT",
        "aliases": [
            r"\buric\s*acid\b", r"\bserum\s*uric\s*acid\b"
        ],
        "expected_units": ["mg/dL"]
    },
    {
        "code": "NA",
        "name": "Serum Sodium",
        "category": "KFT",
        "aliases": [
            r"\bsodium\b", r"\bserum\s*sodium\b", r"\bna\+\b", r"\bna\b"
        ],
        "expected_units": ["mEq/L", "mmol/L"]
    },
    {
        "code": "K",
        "name": "Serum Potassium",
        "category": "KFT",
        "aliases": [
            r"\bpotassium\b", r"\bserum\s*potassium\b", r"\bk\+\b"
        ],
        "expected_units": ["mEq/L", "mmol/L"]
    },
    {
        "code": "CL",
        "name": "Serum Chloride",
        "category": "KFT",
        "aliases": [
            r"\bchloride\b", r"\bserum\s*chloride\b", r"\bcl-\b"
        ],
        "expected_units": ["mEq/L", "mmol/L"]
    },

    # ── CBC ────────────────────────────────────────────────────────────────────
    {
        "code": "HGB",
        "name": "Hemoglobin",
        "category": "CBC",
        "aliases": [
            r"^hemoglobin$", r"^hgb$", r"^hb$", r"^haemoglobin$", r"\bhaemoglobin\s*\(hb\)\b", r"\btotal\s*hemoglobin\b"
        ],
        "expected_units": ["g/dL", "g/L", "gm/dl"]
    },
    {
        "code": "RBC",
        "name": "RBC Count",
        "category": "CBC",
        "aliases": [
            r"\brbc\b", r"\bred\s*blood\s*cell\b", r"\bred\s*cell\s*count\b", r"\brbc\s*count\b", r"\btotal\s*rbc\b"
        ],
        "expected_units": ["10^6/µL", "million/µL", "mil/cu.mm", "cells/µL"]
    },
    {
        "code": "WBC",
        "name": "WBC Count",
        "category": "CBC",
        "aliases": [
            r"\bwbc\b", r"\bwhite\s*blood\s*cell\b", r"\btotal\s*leukocyte\s*count\b", r"\btlc\b", r"\bwbc\s*count\b"
        ],
        "expected_units": ["10^3/µL", "cells/µL", "/cu.mm", "/cumm", "thou/cu.mm"]
    },
    {
        "code": "PLT",
        "name": "Platelet Count",
        "category": "CBC",
        "aliases": [
            r"\bplatelet\b", r"\bplatelet\s*count\b", r"\bplt\b", r"\bthrombocyte\b", r"\btotal\s*platelet\s*count\b"
        ],
        "expected_units": ["10^3/µL", "lakh/cu.mm", "lakhs/cumm", "/cu.mm", "/cumm", "cells/µL"]
    },
    {
        "code": "MCV",
        "name": "Mean Corpuscular Volume (MCV)",
        "category": "CBC",
        "aliases": [
            r"\bmcv\b", r"\bmean\s*corpuscular\s*volume\b"
        ],
        "expected_units": ["fL", "fl"]
    },
    {
        "code": "MCH",
        "name": "Mean Corpuscular Hemoglobin (MCH)",
        "category": "CBC",
        "aliases": [
            r"\bmch\b", r"\bmean\s*corpuscular\s*hemoglobin\b", r"\bmean\s*cell\s*haemoglobin\b"
        ],
        "expected_units": ["pg"]
    },
    {
        "code": "MCHC",
        "name": "Mean Corpuscular Hemoglobin Concentration (MCHC)",
        "category": "CBC",
        "aliases": [
            r"\bmchc\b", r"\bmean\s*corpuscular\s*hemoglobin\s*concentration\b", r"\bmean\s*cell\s*haemoglobin\s*con\b"
        ],
        "expected_units": ["g/dL", "%", "g/dl"]
    },
    {
        "code": "HCT",
        "name": "Hematocrit (HCT / PCV)",
        "category": "CBC",
        "aliases": [
            r"\bhct\b", r"\bpcv\b", r"\bhematocrit\b", r"\bhaematocrit\b", r"\bpacked\s*cell\s*volume\b", r"\bhematocrit\s*value\b"
        ],
        "expected_units": ["%"]
    },
    {
        "code": "NEUT",
        "name": "Neutrophils",
        "category": "CBC",
        "aliases": [
            r"^neutrophils?$", r"\bneutrophil\b"
        ],
        "expected_units": ["%"]
    },
    {
        "code": "LYMPH",
        "name": "Lymphocytes",
        "category": "CBC",
        "aliases": [
            r"^lymphocytes?$", r"\blymphocyte\b"
        ],
        "expected_units": ["%"]
    },
    {
        "code": "EOS",
        "name": "Eosinophils",
        "category": "CBC",
        "aliases": [
            r"^eosinophils?$", r"\beosinophil\b"
        ],
        "expected_units": ["%"]
    },
    {
        "code": "MONO",
        "name": "Monocytes",
        "category": "CBC",
        "aliases": [
            r"^monocytes?$", r"\bmonocyte\b"
        ],
        "expected_units": ["%"]
    },
    {
        "code": "BASO",
        "name": "Basophils",
        "category": "CBC",
        "aliases": [
            r"^basophils?$", r"\bbasophil\b"
        ],
        "expected_units": ["%"]
    },
    {
        "code": "ABS_NEUT",
        "name": "Absolute Neutrophils",
        "category": "CBC",
        "aliases": [
            r"\babsolute\s*neutrophils?\b", r"\babs\.\s*neutrophils?\b", r"\banc\b"
        ],
        "expected_units": ["/cumm", "/cu.mm", "/µL"]
    },
    {
        "code": "ABS_LYMPH",
        "name": "Absolute Lymphocytes",
        "category": "CBC",
        "aliases": [
            r"\babsolute\s*lymphocytes?\b", r"\babs\.\s*lymphocytes?\b", r"\balc\b"
        ],
        "expected_units": ["/cumm", "/cu.mm", "/µL"]
    },
    {
        "code": "ABS_EOS",
        "name": "Absolute Eosinophils",
        "category": "CBC",
        "aliases": [
            r"\babsolute\s*eosinophils?\b", r"\babs\.\s*eosinophils?\b", r"\baec\b"
        ],
        "expected_units": ["/cumm", "/cu.mm", "/µL"]
    },
    {
        "code": "ABS_MONO",
        "name": "Absolute Monocytes",
        "category": "CBC",
        "aliases": [
            r"\babsolute\s*monocytes?\b", r"\babs\.\s*monocytes?\b"
        ],
        "expected_units": ["/cumm", "/cu.mm", "/µL"]
    },
    {
        "code": "RDW_CV",
        "name": "RDW-CV",
        "category": "CBC",
        "aliases": [
            r"\brdw\s*-\s*cv\b", r"\brdw_cv\b"
        ],
        "expected_units": ["%"]
    },
    {
        "code": "RDW_SD",
        "name": "RDW-SD",
        "category": "CBC",
        "aliases": [
            r"\brdw\s*-\s*sd\b", r"\brdw_sd\b"
        ],
        "expected_units": ["fL", "fl"]
    },
    {
        "code": "PCT",
        "name": "Plateletcrit (PCT)",
        "category": "CBC",
        "aliases": [
            r"^pct$", r"\bplateletcrit\b"
        ],
        "expected_units": ["%", ""]
    },
    {
        "code": "MPV",
        "name": "Mean Platelet Volume (MPV)",
        "category": "CBC",
        "aliases": [
            r"^mpv$", r"\bmean\s*platelet\s*volume\b"
        ],
        "expected_units": ["fL", "fl"]
    },
    {
        "code": "PDW",
        "name": "Platelet Distribution Width (PDW)",
        "category": "CBC",
        "aliases": [
            r"^pdw$", r"\bplatelet\s*distribution\s*width\b"
        ],
        "expected_units": ["fL", "fl", "%", ""]
    },


    # ── Thyroid ────────────────────────────────────────────────────────────────
    {
        "code": "TSH",
        "name": "TSH",
        "category": "Thyroid",
        "aliases": [
            r"\btsh\b", r"\bthyroid\s*stimulating\s*hormone\b"
        ],
        "expected_units": ["µIU/mL", "mIU/L", "uIU/mL"]
    },

    # ── Vitamins & Health Indicators ───────────────────────────────────────────
    {
        "code": "VITD",
        "name": "Vitamin D (25-OH)",
        "category": "Vitamin",
        "aliases": [
            r"\bvitamin\s*d\b", r"\bvit\s*d\b", r"\b25\s*-\s*hydroxy\s*vitamin\s*d\b"
        ],
        "expected_units": ["ng/mL", "nmol/L"]
    },
    {
        "code": "VITB12",
        "name": "Vitamin B12",
        "category": "Vitamin",
        "aliases": [
            r"\bvitamin\s*b12\b", r"\bvit\s*b12\b", r"\bcyanocobalamin\b"
        ],
        "expected_units": ["pg/mL", "pmol/L"]
    },
    {
        "code": "HEALTH_SCORE",
        "name": "Overall Health Score",
        "category": "General",
        "aliases": [
            r"\bhealth\s*score\b"
        ],
        "expected_units": ["/100", "score"]
    }
]
