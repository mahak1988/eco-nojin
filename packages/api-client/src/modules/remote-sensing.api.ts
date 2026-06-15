import { apiClient } from '../core/instance';

export interface SatelliteImage {
  image_id: string;
  satellite: 'Sentinel-2' | 'Landsat' | 'MODIS';
  pilot_site: string;
  acquisition_date: string;
  ndvi_mean?: number;
}

export const remoteSensingApi = {
  getLatestImages: (pilotSite: string) =>
    apiClient.get<SatelliteImage[]>('/api/remote-sensing/images/latest/' + pilotSite),
  calculateIndex: (pilotSite: string, indexType: string) =>
    apiClient.post('/api/remote-sensing/calculate-index', { pilot_site: pilotSite, index_type: indexType }),
};
