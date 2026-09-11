import api from './api';

export const analysisApi = {
  // Execute Phase 6 Clinical Intelligence Engine
  runAnalysis: async (reportId, force = false) => {
    const res = await api.post(`/analysis/${reportId}`, null, { params: { force } });
    return res.data;
  },

  // Fetch full clinical analysis
  getAnalysis: async (reportId) => {
    const res = await api.get(`/analysis/${reportId}`);
    return res.data;
  },

  // Fetch executive summary & score
  getSummary: async (reportId) => {
    const res = await api.get(`/analysis/${reportId}/summary`);
    return res.data;
  },

  // Fetch doctor synthesis
  getDoctorSummary: async (reportId) => {
    const res = await api.get(`/analysis/${reportId}/doctor`);
    return res.data;
  },

  // Fetch patient summary
  getPatientSummary: async (reportId) => {
    const res = await api.get(`/analysis/${reportId}/patient`);
    return res.data;
  },

  // Fetch recommendations
  getRecommendations: async (reportId) => {
    const res = await api.get(`/analysis/${reportId}/recommendations`);
    return res.data;
  },

  // Fetch timelines & deltas
  getTimeline: async (reportId) => {
    const res = await api.get(`/analysis/${reportId}/timeline`);
    return res.data;
  },

  // Fetch knowledge graph
  getKnowledgeGraph: async (reportId) => {
    const res = await api.get(`/analysis/${reportId}/graph`);
    return res.data;
  },

  // Fetch evidence traceability
  getEvidence: async (reportId) => {
    const res = await api.get(`/analysis/${reportId}/evidence`);
    return res.data;
  },

  // Fetch conflicts
  getConflicts: async (reportId) => {
    const res = await api.get(`/analysis/${reportId}/conflicts`);
    return res.data;
  },

  // Fetch missing evidence
  getMissingEvidence: async (reportId) => {
    const res = await api.get(`/analysis/${reportId}/missing-evidence`);
    return res.data;
  },

  // Fetch prompt package for Phase 7
  getPromptPackage: async (reportId, target = 'chat') => {
    const res = await api.get(`/analysis/${reportId}/prompt-package/${target}`);
    return res.data;
  },

  // Retry analysis (bypass cache)
  retryAnalysis: async (reportId) => {
    const res = await api.post(`/analysis/${reportId}/retry`);
    return res.data;
  }
};
