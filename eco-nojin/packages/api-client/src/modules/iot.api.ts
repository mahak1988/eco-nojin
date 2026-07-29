import { apiClient } from '../core/instance';

export interface IoTSensor {
  sensor_id: string;
  pilot_site: string;
  sensor_type: string;
  value: number;
  unit: string;
  timestamp: string;
}

export const iotApi = {
  getLatestReadings: (pilotSite: string) =>
    apiClient.get<IoTSensor[]>('/api/iot/readings/latest/' + pilotSite),
  getActiveAlerts: () => apiClient.get('/api/iot/alerts/active'),
};
