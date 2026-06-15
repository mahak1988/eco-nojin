import { apiClient } from '../core/instance';

export const dashboardApi = {
  getWatershedManagerDashboard: (pilotSite: string) =>
    apiClient.get('/api/dashboard/watershed-manager/' + pilotSite),
  getFarmerDashboard: (farmerId: string, farmId: string) =>
    apiClient.get('/api/dashboard/farmer/' + farmerId + '/' + farmId),
  getInvestorDashboard: (projectId: string) =>
    apiClient.get('/api/dashboard/investor/' + projectId),
  getDSSRecommendations: (pilotSite: string) =>
    apiClient.get('/api/dashboard/dss/recommendations/' + pilotSite),
};
