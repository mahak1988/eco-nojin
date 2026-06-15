import { apiClient } from '../core/instance';

export interface CarbonCredit {
  credit_id: string;
  pilot_site: string;
  volume_tCO2e: number;
  price_usd: number;
  status: 'pending' | 'verified' | 'sold';
}

export const financialApi = {
  getCarbonCredits: (pilotSite?: string) =>
    apiClient.get<CarbonCredit[]>('/api/financial/carbon-credits', { params: { pilot_site: pilotSite } }),
  calculateNPV: (projectId: string) =>
    apiClient.get('/api/financial/npv/' + projectId),
};
