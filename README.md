# 🩸 Swasth-IQ: Multi-Organ Medical Report Intelligence & Diagnostic Suite

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React_18-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Python 3.10+](https://img.shields.io/badge/Python_3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Pytest](https://img.shields.io/badge/Pytest-250%2F250_Passing-brightgreen?style=for-the-badge&logo=pytest)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-rose.svg?style=for-the-badge)](LICENSE)

---

## 📌 Executive Summary

**Swasth-IQ** is a high-performance clinical diagnostic analytics and multi-organ medical report intelligence platform. Built to transform complex, multi-page laboratory test reports into actionable physiological insights, Swasth-IQ bridges the gap between raw medical data and clinical comprehension.

The platform utilizes a **hybrid dual-engine optical pipeline** capable of parsing both structured digital PDF records and degraded physical document photographs. Extracted laboratory metrics are validated against physiological reference ranges, aggregated into **deterministic 5-organ health scores**, and surfaced via an audited medical conversational copilot protected by strict clinical guardrails.

---

## 🏛️ System Architecture

```
     ┌─────────────────────────────────────────────────────────────────────────┐
     │                      Multi-Modal Report Ingestion                       │
     │      [ Native Digital PDF Document ]   [ Degraded Physical Photo Scan ] │
     └────────────────────┬───────────────────────────────────┬────────────────┘
                          │                                   │
                          ▼                                   ▼
             ┌─────────────────────────┐         ┌─────────────────────────┐
             │   PyMuPDF (Fitz) Vector │         │  Neural Vision OCR Engine│
             │   Stream Extraction     │         │  (Sarvam Vision / Tesseract)
             └────────────┬────────────┘         └────────────┬────────────┘
                          │                                   │
                          └─────────────────┬─────────────────┘
                                            │ Raw Text Stream
                                            ▼
     ┌─────────────────────────────────────────────────────────────────────────┐
     │                Diagnostic Parameter Normalization Engine                │
     │     • Regex Canonical Token Matcher     • Alias & Synonym Dictionary    │
     │     • Unit Metric Standardizer (mg/dL)  • Numerical Value Sanitization  │
     └──────────────────────────────────────┬──────────────────────────────────┘
                                            │ Structured Lab Panels
                                            ▼
     ┌─────────────────────────────────────────────────────────────────────────┐
     │                 Deterministic Physiological Scoring Core                │
     │  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌──────────────┐ │
     │  │ Cardiovascular│ │  Renal Score  │ │ Hepatic Score │ │  Metabolic   │ │
     │  │  Index (0-100)│ │    (0-100)    │ │    (0-100)    │ │ Index (0-100)│ │
     │  └───────────────┘ └───────────────┘ └───────────────┘ └──────────────┘ │
     └──────────────────────────────────────┬──────────────────────────────────┘
                                            │ Panic Flags & Organ Scores
                                            ▼
     ┌─────────────────────────────────────────────────────────────────────────┐
     │                  Audited Clinical Copilot & Guardrails                  │
     │     • Report Context Gating             • Anti-Hallucination Boundaries │
     │     • Emergency Triage Panic Alerter    • Grounded Evidence Citations   │
     └──────────────────────────────────────┬──────────────────────────────────┘
                                            │ JSON API Response
                                            ▼
     ┌─────────────────────────────────────────────────────────────────────────┐
     │                     Swasth-IQ Responsive Dashboard                      │
     │         React 18 PWA · Interactive Organ Charts · Real-time Chat        │
     └─────────────────────────────────────────────────────────────────────────┘
```

---

## 🧬 Key Functional Modules

### 1. Dual-Path Document Ingestion Core
- **Native Vector Parsing:** Extracts clean digital PDF text layers instantly with PyMuPDF (sub-150ms execution).
- **Neural Optical OCR:** Ingests low-contrast mobile snapshots, skewed pages, and noisy lighting conditions with high fidelity.

### 2. Comprehensive Panel Normalization (100+ Lab Parameters)
Normalizes disparate naming conventions into 8 canonical clinical panels:
- **Complete Blood Count (CBC):** Hemoglobin, RBC, WBC, Platelets, MCV, MCH, MCHC, Neutrophils, Lymphocytes.
- **Lipid Profile:** Total Cholesterol, HDL, LDL, VLDL, Triglycerides, TC/HDL Ratio.
- **Renal Function Test (RFT):** Serum Creatinine, Blood Urea Nitrogen (BUN), eGFR, Uric Acid.
- **Liver Function Test (LFT):** Bilirubin (Total/Direct), SGOT (AST), SGPT (ALT), Alkaline Phosphatase, Total Protein, Albumin.
- **Metabolic & Glycemic:** Fasting Blood Sugar, Postprandial Glucose, HbA1c.
- **Thyroid Function Panel:** T3, T4, TSH.
- **Electrolyte Balance:** Sodium, Potassium, Chloride, Calcium.
- **Urine & Microscopy:** Specific Gravity, Urine Protein, Microalbumin.

### 3. Deterministic Multi-Organ Health Index
Unlike opaque black-box AI estimations, Swasth-IQ calculates transparent, reproducible health indices from 0 to 100 based on standard clinical risk formulas:
- **Cardiovascular Index:** Evaluates lipid atherogenic ratios and hematological viscosity indicators.
- **Renal Index:** Models filtration integrity via creatinine clearance and urea ratios.
- **Hepatic Index:** Scores parenchymal damage markers and biliary clearance enzymes.
- **Metabolic Index:** Reflects glycemic control and metabolic syndrome indicators.
- **Hematologic Index:** Tracks oxygenation capacity and immunological distribution.

### 4. Physiological Panic Value Detection
- Flags critical emergent thresholds (e.g., Potassium < 2.5 or > 6.5 mmol/L, Platelets < 20,000 /uL, Fasting Glucose > 400 mg/dL).
- Provides immediate visual triage warnings with recommended urgent clinical follow-up protocols.

### 5. Grounded Medical Assistant
- Scoped strictly to the active patient report.
- Synthesizes patient-friendly explanations without providing definitive unsolicited diagnostic assertions.
- Backed by automated prompt guardrails and sanitization filters.

---

## 💻 Technical Stack

- **Backend:** Python 3.10+, FastAPI, Uvicorn, Pydantic v2
- **Document Processing:** PyMuPDF (Fitz), Pillow, Tesseract OCR, Sarvam Vision API
- **Data & Testing:** SQLite / SQLAlchemy, Pytest (250 automated tests)
- **Frontend:** React 18, Vite, Tailwind CSS, Lucide React, Axios
- **Architecture:** Modular Service-Repository Pattern, RESTful API

---

## 📂 Repository Layout

```text
Swasth-IQ/
├── backend/
│   ├── generated_reports/       # Exported clinical PDF summaries
│   ├── knowledge_base/          # Reference ranges and medical dictionary
│   ├── ocr_results/             # Intermediate OCR transcriptions
│   ├── src/
│   │   ├── api/                 # FastAPI routes and endpoint handlers
│   │   ├── core/                # System configuration and global settings
│   │   ├── engine/              # Organ scoring & panic value algorithms
│   │   ├── models/              # Pydantic schemas and database models
│   │   ├── parser/              # Lab test extractor and token normalizer
│   │   └── services/            # Document storage, OCR, and AI services
│   ├── test/                    # Comprehensive unit and integration test suite
│   ├── requirements.txt         # Backend Python dependencies
│   └── run.py                   # Application launch script
├── docs/                        # Complete architecture and API documentation
└── frontend/
    ├── public/                  # Static assets and PWA icons
    ├── src/
    │   ├── components/          # Reusable UI components & organ widgets
    │   ├── layouts/             # Responsive layout wrappers
    │   ├── services/            # Axios API client integrations
    │   └── utils/               # Formatters, helpers, and constants
    ├── package.json             # Frontend dependency manifest
    └── vite.config.js           # Vite build configuration
```

---

## ⚡ Getting Started

### 1. Backend Installation

```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

*Update `.env` with your API credentials (optional for core rule engine features).*

Start the backend server:
```bash
python run.py
```
*API documentation will be live at `http://localhost:8000/docs`.*

---

### 2. Frontend Installation

```bash
cd ../frontend
npm install
npm run dev
```
*Access the user interface at `http://localhost:5173`.*

---

### 3. Running Test Suites

Execute the comprehensive automated test suite (250 tests covering OCR, normalizer, organ scoring, and API routes):
```bash
cd backend
pytest -v
```

---

## 👨‍💻 Maintainer & Author

**Nazish Khan**
- **GitHub:** [@nazishkhan10](https://github.com/nazishkhan10)
- **Email:** [nazish400210@gmail.com](mailto:nazish400210@gmail.com)

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
