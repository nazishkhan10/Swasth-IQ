import api from './api';

export const validationApi = {
  // Execute Phase 5 Medical Validation Engine
  validateReport: async (reportId) => {
    const res = await api.post(`/validation/validate/${reportId}`);
    return res.data;
  },

  // Fetch validated medical dataset (auto-triggers validation if none exists)
  getValidationResults: async (reportId) => {
    const res = await api.get(`/validation/validate/${reportId}`);
    return res.data;
  },

  // Fetch validation summary metrics (normal, low, high, critical counts)
  getValidationSummary: async (reportId) => {
    const res = await api.get(`/validation/validate/${reportId}/summary`);
    return res.data;
  },

  // Fetch critical clinical values only
  getCriticalValues: async (reportId) => {
    const res = await api.get(`/validation/validate/${reportId}/critical`);
    return res.data;
  },

  // Idempotently re-run validation engine
  retryValidation: async (reportId) => {
    const res = await api.post(`/validation/validate/${reportId}/retry`);
    return res.data;
  },

  // Export validated dataset (json or csv)
  exportValidatedDataset: async (reportId, format = 'json') => {
    const res = await api.get(`/validation/export/${reportId}`, {
      params: { format },
      responseType: format === 'csv' ? 'blob' : 'json',
    });
    return res.data;
  },

  // Fetch data quality score (Phase 6 AI gating)
  getQualityScore: async (reportId) => {
    const res = await api.get(`/validation/validate/${reportId}/quality`);
    return res.data;
  },
};
