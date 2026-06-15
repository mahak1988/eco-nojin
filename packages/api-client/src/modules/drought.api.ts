import { apiClient } from '../core/instance';

export interface DroughtIndex {
  id: string;
  pilot_site: string;
  index_type: 'SPEI' | 'SPI' | 'PDSI' | 'NDVI';
  value: number;
  severity: 'normal' | 'mild' | 'moderate' | 'severe' | 'extreme';
  timestamp: string;
}

export const droughtApi = {
  getIndices: (pilotSite?: string) =>
    apiClient.get<DroughtIndex[]>('/api/drought/indices', { params: { pilot_site: pilotSite } }),
  getEarlyWarning: (pilotSite: string) =>
    apiClient.get('/api/drought/early-warning/' + pilotSite),
};
