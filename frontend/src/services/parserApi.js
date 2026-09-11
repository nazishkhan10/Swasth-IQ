import api from './api';

export const parserApi = {
  // Execute Phase 4 Medical Parser on report OCR output
  runParser: async (reportId) => {
    const response = await api.post(`/parser/${reportId}`);
    return response.data;
  },

  // Fetch full parsed report output
  getParsedData: async (reportId) => {
    const response = await api.get(`/parser/${reportId}`);
    return response.data;
  },

  // Fetch patient metadata
  getPatientMetadata: async (reportId) => {
    const response = await api.get(`/parser/${reportId}/patient`);
    return response.data;
  },

  // Fetch parameters with optional search query & category filter
  getParameters: async (reportId, search = '', category = 'All') => {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (category && category !== 'All') params.append('category', category);

    const queryString = params.toString() ? `?${params.toString()}` : '';
    const response = await api.get(`/parser/${reportId}/parameters${queryString}`);
    return response.data;
  },

  // Fetch parse warnings audit log
  getWarnings: async (reportId) => {
    const response = await api.get(`/parser/${reportId}/warnings`);
    return response.data;
  },

  // Force re-parsing
  retryParser: async (reportId) => {
    const response = await api.post(`/parser/${reportId}/retry`);
    return response.data;
  }
};

export default parserApi;
