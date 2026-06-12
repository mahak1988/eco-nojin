import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api/client';

export function useSoilProperties(lat: number, lng: number) {
  return useQuery({
    queryKey: ['soil', 'properties', lat, lng],
    queryFn: async () => {
      const response = await api.get(`/api/v1/soil-water/properties?lat=${lat}&lng=${lng}`);
      return response.data;
    },
    enabled: !isNaN(lat) && !isNaN(lng),
    staleTime: 60 * 60 * 1000, // 1 hour (soil doesn't change often)
  });
}

export function useSoilClassification(lat: number, lng: number) {
  return useQuery({
    queryKey: ['soil', 'classification', lat, lng],
    queryFn: async () => {
      const response = await api.get(`/api/v1/soil-water/classification?lat=${lat}&lng=${lng}`);
      return response.data;
    },
    enabled: !isNaN(lat) && !isNaN(lng),
  });
}
