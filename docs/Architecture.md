# Architecture Overview — Frozen Architecture v8.2

## System Overview
Medical Report Analyzer is a production-grade, privacy-preserving Clinical Intelligence & Medical AI platform designed to parse, validate, and analyze complex unstructured medical diagnostic laboratory reports.

```
[ PDF / Image Upload ] ──► [ OCR Engine (Sarvam / EasyOCR) ]
                                   │
                                   ▼
                       [ Phase 4: Medical Parser Engine ]
                                   │
                                   ▼
                       [ Phase 5: Hardened Validation Engine ]
                                   │
                                   ▼
                       [ Phase 6: Clinical Intelligence Engine ]
                                   │
                                   ▼
                       [ Phase 7: GPT-5 Nano Medical AI & RAG ]
                                   │
                                   ▼
                       [ Medical AI Workspace UI ]
```

## Core Architectural Layers

### 1. Document Extraction & OCR Pipeline
- Support for multi-page PDF, PNG, JPG, and scanned lab report documents.
- Dual OCR engine architecture with vision pre-processing, text region segmentation, and confidence scoring.

### 2. Phase 4 — Medical Parser Engine
- High-precision regex pattern extraction, parameter alias normalization, unit standardizations, and reference range parsing.
- Deterministic extraction for CBC, Lipid Profile, Renal Function, Liver Function, Thyroid Panel, HbA1c, and Metabolic panels.

### 3. Phase 5 — Hardened Validation Engine
- Multi-layer validation checking parameter sanity, physiological bounds, unit compatibility, and critical threshold alerts.
- Stores validated parameters with audit trace and confidence metrics in `validated_medical_values`.

### 4. Phase 6 — Clinical Intelligence Engine
- Deterministic clinical decision rules (Anemia, CKD, Diabetes, Thyroid, Inflammation, Lipid disorders).
- Organ health classification (Cardiovascular, Renal, Hepatic, Endocrine, Hematological).
- Risk scoring, missing evidence identification, and interactive knowledge graph generation.

### 5. Phase 7 — Medical AI & RAG Engine
- OpenAI GPT-5 Nano reasoning model with system guardrails (Input, Privacy/PII masking, Medical disclaimer, Output validation).
- Report-scoped session management with SHA-256 audit hashing for medical queries.

---
*Frozen Architecture v8.2 — CODEX Hackfest Compliance*
