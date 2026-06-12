import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api/client';

export function useSensorData(sensorId?: string) {
  return useQuery({
    queryKey: ['iot', 'sensor', sensorId],
    queryFn: async () => {
      const url = sensorId 
        ? `/api/v1/iot/sensors/${sensorId}/latest`
        : '/api/v1/iot/sensors/latest';
      const response = await api.get(url);
      return response.data;
    },
    refetchInterval: 5000, // 5 seconds
  });
}

export function useSensorStats(sensorId: string, hours: number = 24) {
  return useQuery({
    queryKey: ['iot', 'stats', sensorId, hours],
    queryFn: async () => {
      const response = await api.get(`/api/v1/iot/sensors/${sensorId}/stats?hours=${hours}`);
      return response.data;
    },
    refetchInterval: 30000, // 30 seconds
  });
}

export function useIoTAlerts(severity?: string) {
  return useQuery({
    queryKey: ['iot', 'alerts', severity],
    queryFn: async () => {
      const url = severity 
        ? `/api/v1/iot/alerts?severity=${severity}`
        : '/api/v1/iot/alerts';
      const response = await api.get(url);
      return response.data;
    },
    refetchInterval: 10000, // 10 seconds
  });
}

export function useAcknowledgeAlert() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (alertId: string) => {
      const response = await api.post(`/api/v1/iot/alerts/${alertId}/acknowledge`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['iot', 'alerts'] });
    },
  });
}
