import { useQuery, useMutation } from '@tanstack/react-query';
import api from '@/lib/api/client';

export function useSentinelImages(
  bbox: [number, number, number, number],
  startDate: string,
  endDate: string,
  cloudCoverMax: number = 20
) {
  return useQuery({
    queryKey: ['satellite', 'sentinel', bbox, startDate, endDate, cloudCoverMax],
    queryFn: async () => {
      const response = await api.get('/api/v1/mrv/sentinel/search', {
        params: {
          bbox: bbox.join(','),
          start_date: startDate,
          end_date: endDate,
          cloud_cover_max: cloudCoverMax
        }
      });
      return response.data;
    },
    enabled: !!bbox && !!startDate && !!endDate,
    staleTime: 60 * 60 * 1000, // 1 hour
  });
}

export function useSpectralIndex(
  lat: number,
  lng: number,
  index: string = 'NDVI'
) {
  return useQuery({
    queryKey: ['satellite', 'index', lat, lng, index],
    queryFn: async () => {
      const response = await api.get(`/api/v1/mrv/spectral/${index}`, {
        params: { lat, lng }
      });
      return response.data;
    },
    enabled: !isNaN(lat) && !isNaN(lng),
    staleTime: 30 * 60 * 1000, // 30 minutes
  });
}

export function useVegetationHealth(lat: number, lng: number) {
  return useQuery({
    queryKey: ['satellite', 'vegetation', lat, lng],
    queryFn: async () => {
      const response = await api.get(`/api/v1/mrv/vegetation/health`, {
        params: { lat, lng }
      });
      return response.data;
    },
    enabled: !isNaN(lat) && !isNaN(lng),
  });
}
