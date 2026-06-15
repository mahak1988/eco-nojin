import { apiClient } from '../core/instance';

export interface Grievance {
  grievance_id: string;
  pilot_site: string;
  category: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'received' | 'acknowledged' | 'resolved';
}

export const safeguardsApi = {
  getGrievances: (pilotSite?: string) =>
    apiClient.get<Grievance[]>('/api/safeguards/grm/grievances', { params: { pilot_site: pilotSite } }),
  submitGrievance: (data: Partial<Grievance>) =>
    apiClient.post('/api/safeguards/grm/submit', data),
};
