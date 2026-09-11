# Testing Guide & Quality Assurance

## Backend Test Suite

Run pytest in `backend/`:
```bash
cd backend
python -m pytest
```

All 250 test cases cover:
- User Authentication & JWT validation.
- OCR text extraction & confidence calculation.
- Phase 4 Medical Parser Engine (Regex, units, ranges).
- Phase 5 Hardened Validation Engine (Sanity, conversions, critical values).
- Phase 6 Clinical Intelligence Rules & Organ Scoring.
- Phase 7 RAG Engine, OpenAI GPT-5 Nano integration, Guardrails, and Session Management.

## Frontend Verification

```bash
cd frontend
npm run build
```
Ensures zero JSX / TypeScript / Vite bundling errors.
