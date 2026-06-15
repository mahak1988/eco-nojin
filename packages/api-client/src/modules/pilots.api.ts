import { apiClient } from '../core/instance';

export interface PilotSite {
  pilot_id: string;
  name: string;
  country: string;
  continent: string;
  climate_zone: string;
  latitude: number;
  longitude: number;
  status: string;
}

export const pilotsApi = {
  getAllPilots: () => apiClient.get<PilotSite[]>('/api/pilots'),
  getPilot: (pilotId: string) => apiClient.get<PilotSite>('/api/pilots/' + pilotId),
  activatePilot: (pilotId: string) => apiClient.post('/api/pilots/' + pilotId + '/activate'),
};
