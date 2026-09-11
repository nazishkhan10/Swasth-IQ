import axios from 'axios';

const API_BASE_URL = `${import.meta.env.VITE_API_BASE_URL || ''}/api/v1/chat`;

export const chatApi = {
  // Synchronous Chat
  sendMessage: async (reportId, question) => {
    const res = await axios.post(`${API_BASE_URL}`, {
      report_id: reportId,
      question: question
    });
    return res.data;
  },

  // Dynamic Conversation Starter Chips
  getStarters: async (reportId) => {
    const res = await axios.get(`${API_BASE_URL}/report/${reportId}/starters`);
    return res.data;
  },

  // Report-Scoped Session Lifecycle
  initSession: async (reportId) => {
    const res = await axios.post(`${API_BASE_URL}/report/${reportId}/session`);
    return res.data;
  },

  closeSession: async (reportId) => {
    const res = await axios.delete(`${API_BASE_URL}/report/${reportId}/session`);
    return res.data;
  },

  // Fetch Session History
  getHistory: async (reportId) => {
    const res = await axios.get(`${API_BASE_URL}/history/${reportId}`);
    return res.data;
  },

  // Clear History
  clearHistory: async (reportId) => {
    const res = await axios.delete(`${API_BASE_URL}/history/${reportId}`);
    return res.data;
  },

  // Get Cached Clinical Intelligence
  getInsights: async (reportId) => {
    const res = await axios.get(`${API_BASE_URL}/insights/${reportId}`);
    return res.data;
  },

  // Get Provider Status
  getProviders: async () => {
    const res = await axios.get(`${API_BASE_URL}/providers`);
    return res.data;
  }
};


export default chatApi;
