import { apiClient } from '../core/instance';

export interface SoilAnalysis {
  pilot_site: string;
  soc_percent: number;
  erosion_rate: number;
  ph: number;
}

export const soilWaterApi = {
  getSoilAnalysis: (pilotSite: string) =>
    apiClient.get<SoilAnalysis>('/api/soil-water/analysis/' + pilotSite),
  getWaterBalance: (pilotSite: string) =>
    apiClient.get('/api/soil-water/water-balance/' + pilotSite),
};
