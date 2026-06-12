import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api/client';

export function useForestMetrics(lat: number, lng: number) {
  return useQuery({
    queryKey: ['forest', 'metrics', lat, lng],
    queryFn: async () => {
      const response = await api.get(`/api/v1/mrv/forest/metrics?lat=${lat}&lng=${lng}`);
      return response.data;
    },
    enabled: !isNaN(lat) && !isNaN(lng),
    staleTime: 24 * 60 * 60 * 1000,
  });
}

export function useVegetationTimeseries(lat: number, lng: number, startDate: string, endDate: string) {
  return useQuery({
    queryKey: ['vegetation', 'timeseries', lat, lng, startDate, endDate],
    queryFn: async () => {
      const response = await api.get(
        `/api/v1/mrv/vegetation/timeseries?lat=${lat}&lng=${lng}&start=${startDate}&end=${endDate}`
      );
      return response.data;
    },
    enabled: !isNaN(lat) && !isNaN(lng) && !!startDate && !!endDate,
  });
}

export function useCarbonSequestration(lat: number, lng: number, areaHa: number) {
  return useQuery({
    queryKey: ['carbon', 'sequestration', lat, lng, areaHa],
    queryFn: async () => {
      const response = await api.get(
        `/api/v1/mrv/carbon/sequestration?lat=${lat}&lng=${lng}&area=${areaHa}`
      );
      return response.data;
    },
    enabled: !isNaN(lat) && !isNaN(lng) && areaHa > 0,
  });
}
