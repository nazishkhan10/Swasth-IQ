import api from './api';

export const authApi = {
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  login: async (credentials) => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },

  demoLogin: async () => {
    const response = await api.post('/auth/demo');
    return response.data;
  },

  getMe: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  checkHealth: async () => {
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
    const response = await api.get(`${API_BASE_URL}/health`);
    return response.data;
  }
};

export default authApi;
