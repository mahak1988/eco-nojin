import axios from 'axios';
import type { AxiosError, InternalAxiosRequestConfig } from 'axios';

// Base URL from Vite env or fallback
const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

export const apiClient = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth interceptor: attach JWT token from localStorage
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('accessToken');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => Promise.reject(error)
);

// Response interceptor: normalize errors per Phase 0 standard
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response) {
      // Normalize to standard error shape: { error, message, request_id, detail }
      const data = error.response.data as Record<string, unknown> || {};
      const normalized = {
        error: data.error || `HTTP_${error.response.status}`,
        message: data.message || error.message || 'Unknown error',
        request_id: error.response.headers['x-request-id'] || data.request_id || null,
        detail: data.detail || null,
        status: error.response.status,
      };
      return Promise.reject(normalized);
    }
    return Promise.reject({
      error: 'NETWORK_ERROR',
      message: error.message || 'Network error',
      request_id: null,
      detail: null,
    });
  }
);

export default apiClient;
