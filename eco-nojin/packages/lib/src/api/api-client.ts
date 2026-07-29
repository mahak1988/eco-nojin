import axios, { AxiosInstance, AxiosError } from 'axios';
import type { components } from './api-types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

apiClient.interceptors.request.use((config) => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const api = {
  getDashboardStats: () => apiClient.get<components['schemas']['DashboardStatsResponse']>('/api/v1/stats').then(r => r.data),
  getIoTStats: () => apiClient.get<components['schemas']['IoTStatsResponse']>('/api/v1/iot/stats').then(r => r.data),
  getMyWallet: () => apiClient.get<components['schemas']['UserWalletResponse']>('/api/v1/ecocoin/wallets/me').then(r => r.data),
  getEcoCoinStats: () => apiClient.get<any>('/api/v1/ecocoin/stats').then(r => r.data),
  getAcademyStats: () => apiClient.get<components['schemas']['AcademyStatsResponse']>('/api/v1/academy/statistics').then(r => r.data),
  getMaintenanceStats: () => apiClient.get<components['schemas']['MaintenanceStatsResponse']>('/api/v1/maintenance/stats').then(r => r.data),
  getMRVStats: () => apiClient.get<components['schemas']['MRVStatsResponse']>('/api/v1/mrv/stats').then(r => r.data),
  getDroughtStats: () => apiClient.get<components['schemas']['DroughtStatsResponse']>('/api/v1/drought/statistics').then(r => r.data),
  getFinancialDashboard: () => apiClient.get<components['schemas']['FinancialDashboardResponse']>('/api/v1/financial/dashboard').then(r => r.data),
  getThresholds: () => apiClient.get<components['schemas']['ThresholdsResponse']>('/api/v1/scientific/thresholds').then(r => r.data),
  getCourses: () => apiClient.get('/api/v1/academy/courses').then(r => r.data),
};

export default api;
