/**
 * Feature Flags — Medical Report Analyzer
 * Phase 2: Smart Upload & File Management
 *
 * To enable a feature for a new phase, flip its value to `true`.
 */

export const FEATURES = {
  // Phase 2 ✅ — Upload and file management
  UPLOAD: true,
  REPORT_HISTORY: true,

  // Phase 2 ❌ — Camera requires device permission (enabled but gated by browser support)
  CAMERA: true,

  // Phase 3 ✅ — OCR & Document Intelligence
  OCR: true,

  // Phase 4 ✅ — Medical Data Extraction & Structured Parsing
  PARSER: true,
  MEDICAL_PARSER: true,
  AI_ANALYSIS: false,

  // Phase 5 ✅ — Medical Validation Engine
  VALIDATION: true,

  // Phase 3 ❌ — Medical recommendations
  DIET_SUGGESTIONS: false,
  LIFESTYLE_SUGGESTIONS: false,

  // Phase 4 ❌ — Export
  PDF_EXPORT: false,

  // Debug mode (auto-disabled in production)
  DEBUG_MODE: import.meta.env.DEV,
};

export default FEATURES;
