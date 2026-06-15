import { apiClient } from '../core/instance';

export interface TrainingSession {
  session_id: string;
  pilot_site: string;
  activity_type: 'FFS' | 'FGD' | 'PRA';
  participant_count: number;
  women_count: number;
}

export const trainingApi = {
  getSessions: (pilotSite?: string) =>
    apiClient.get<TrainingSession[]>('/api/training/sessions', { params: { pilot_site: pilotSite } }),
  getModules: () => apiClient.get('/api/training/modules'),
};
