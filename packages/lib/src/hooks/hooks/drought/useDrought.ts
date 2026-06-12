import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api-client';

export function useDroughtRisk(lat: number, lng: number) {
  return useQuery({
    queryKey: ['drought', 'risk', lat, lng],
    queryFn: async () => {
      const response = await api.get(`/api/v1/drought/risk?lat=${lat}&lng=${lng}`);
      return response.data;
    },
    enabled: !isNaN(lat) && !isNaN(lng),
    staleTime: 60 * 60 * 1000,
  });
}

export function useSPEIAnalysis(lat: number, lng: number) {
  return useQuery({
    queryKey: ['drought', 'spei', lat, lng],
    queryFn: async () => {
      const response = await api.get(`/api/v1/drought/spei?lat=${lat}&lng=${lng}`);
      return response.data;
    },
    enabled: !isNaN(lat) && !isNaN(lng),
    staleTime: 60 * 60 * 1000,
  });
}

export function useRainfallData(lat: number, lng: number, startDate: string, endDate: string) {
  return useQuery({
    queryKey: ['drought', 'rainfall', lat, lng, startDate, endDate],
    queryFn: async () => {
      const response = await api.get(
        `/api/v1/drought/rainfall?lat=${lat}&lng=${lng}&start=${startDate}&end=${endDate}`
      );
      return response.data;
    },
    enabled: !isNaN(lat) && !isNaN(lng) && !!startDate && !!endDate,
  });
}
