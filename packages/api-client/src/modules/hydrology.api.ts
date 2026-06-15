import { apiClient } from '../core/instance';

export const hydrologyApi = {
  runSWAT: (pilotSite: string, scenario: any) =>
    apiClient.post('/api/hydrology/simulate/swat', { pilot_site: pilotSite, ...scenario }),
  runWEAP: (pilotSite: string, scenario: any) =>
    apiClient.post('/api/hydrology/simulate/weap', { pilot_site: pilotSite, ...scenario }),
  getSimulationStatus: (id: string) => apiClient.get('/api/hydrology/simulations/' + id),
};
