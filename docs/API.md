# API Specification — Medical Report Analyzer

All API endpoints are hosted by FastAPI with OpenAPI 3.0 specs available at `/docs` and `/redoc`.

Base API Path: `/api/v1`

## Endpoints Summary

### Authentication (`/api/v1/auth`)
- `POST /auth/register` — Register a new user account.
- `POST /auth/login` — Authenticate and receive JWT access token.
- `GET /auth/me` — Get current user profile.

### Document & File Management (`/api/v1/upload`, `/api/v1/files`)
- `POST /upload` — Upload medical report (PDF / PNG / JPG).
- `GET /files` — List uploaded reports for current user.
- `GET /files/{report_id}` — Get report metadata and processing status.
- `DELETE /files/{report_id}` — Delete report and associated data.

### OCR & Medical Parsing (`/api/v1/ocr`, `/api/v1/parser`)
- `POST /ocr/process/{report_id}` — Run OCR extraction pipeline.
- `GET /ocr/results/{report_id}` — Fetch raw and structured OCR text.
- `POST /parser/parse/{report_id}` — Run Phase 4 Medical Parser Engine.
- `GET /parser/results/{report_id}` — Fetch extracted parameters and reference ranges.

### Validation Engine (`/api/v1/validation`)
- `POST /validation/validate/{report_id}` — Execute Phase 5 Hardened Validation Engine.
- `GET /validation/results/{report_id}` — Fetch validated medical parameters and flags.

### Clinical Intelligence (`/api/v1/analysis`)
- `POST /analysis/run/{report_id}` — Run Phase 6 Clinical Intelligence & Organ Scoring.
- `GET /analysis/results/{report_id}` — Fetch patient summary, doctor summary, organ health scores, knowledge graph, and recommendations.

### Medical AI & Chat (`/api/v1/chat`)
- `POST /chat/query` — Send question to GPT-5 Nano Medical Assistant (Report-scoped).
- `GET /chat/history/{report_id}` — Retrieve active report chat history.
- `DELETE /chat/session/{report_id}` — Clear temporary session history on report close/upload.
