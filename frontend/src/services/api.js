import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

// Request Interceptor: Attach JWT Token if present in localStorage
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Catch 401 Unauthorized errors and trigger session cleanup
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear invalid session state if unauthenticated
      if (localStorage.getItem('token')) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.dispatchEvent(new Event('auth-unauthorized'));
      }
    }
    return Promise.reject(error);
  }
);

export default api;
