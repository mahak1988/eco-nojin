import { apiClient } from '../core/instance';

export const gatewayApi = {
  getHealth: () => apiClient.get('/gateway/health'),
  getDomains: () => apiClient.get('/gateway/domains'),
  getPilots: () => apiClient.get('/gateway/pilots'),
  getApiInfo: () => apiClient.get('/api/info'),
};
