/**
 * Application-wide constants — Medical Report Analyzer
 * No magic strings or numbers in components.
 */

export const APP_NAME = 'Medical Report Analyzer';
export const APP_TAGLINE = 'AI-Powered Health Insights';
export const APP_VERSION = '1.0.0';

// API
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
export const API_TIMEOUT_MS = 15000;

// Auth
export const TOKEN_KEY = 'token';
export const USER_KEY = 'user';

// Validation
export const PASSWORD_MIN_LENGTH = 6;
export const NAME_MIN_LENGTH = 2;

// File Upload (Phase 2)
export const ALLOWED_FILE_TYPES = ['application/pdf', 'image/png', 'image/jpeg', 'text/plain'];
export const MAX_FILE_SIZE_MB = 20;
export const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;

// UI / Toast
export const TOAST_DURATION_MS = 4000;
export const TOAST_DURATION_SHORT_MS = 2500;
export const TOAST_DURATION_LONG_MS = 6000;

// Routes
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/dashboard',
  UPLOAD: '/upload',
  MY_REPORTS: '/my-reports',
  REPORT_DETAIL: '/reports/:id',
  PROFILE: '/profile',
  NOT_FOUND: '*',
};

// Phase labels for progress widget
export const PHASE_LABELS = {
  1: 'Foundation & Auth',
  2: 'Upload & OCR',
  3: 'AI Analysis',
  4: 'Reports & Export',
};
