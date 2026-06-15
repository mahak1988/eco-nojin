import { apiClient } from '../core/instance';

export interface MRVReport {
  report_id: string;
  pilot_site: string;
  soc_change_tCO2: number;
  water_saved_m3: number;
  verified: boolean;
}

export const mrvApi = {
  getReports: (pilotSite?: string) =>
    apiClient.get<MRVReport[]>('/api/mrv/reports', { params: { pilot_site: pilotSite } }),
  verifyReport: (reportId: string) =>
    apiClient.post('/api/mrv/reports/' + reportId + '/verify'),
};
