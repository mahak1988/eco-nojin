import { useQuery, useMutation } from '@tanstack/react-query';
import api from '@/lib/api/client';

export function useAIAnalysis(type: string, data: any) {
  return useQuery({
    queryKey: ['ai', 'analysis', type, data],
    queryFn: async () => {
      const response = await api.post(`/api/v1/ai/analyze/${type}`, data);
      return response.data;
    },
    enabled: !!data && Object.keys(data).length > 0,
  });
}

export function useSoilAnalysis(soilData: any) {
  return useQuery({
    queryKey: ['ai', 'soil', soilData],
    queryFn: async () => {
      const response = await api.post('/api/v1/ai/analyze/soil', soilData);
      return response.data;
    },
    enabled: !!soilData,
  });
}

export function useWeatherAnalysis(weatherData: any) {
  return useQuery({
    queryKey: ['ai', 'weather', weatherData],
    queryFn: async () => {
      const response = await api.post('/api/v1/ai/analyze/weather', weatherData);
      return response.data;
    },
    enabled: !!weatherData,
  });
}

export function useVegetationAnalysis(ndvi: number, evi: number) {
  return useQuery({
    queryKey: ['ai', 'vegetation', ndvi, evi],
    queryFn: async () => {
      const response = await api.post('/api/v1/ai/analyze/vegetation', { ndvi, evi });
      return response.data;
    },
    enabled: !isNaN(ndvi) && !isNaN(evi),
  });
}

export function useFarmPlan(areaHa: number, cropType: string, soilData: any, weatherData: any) {
  return useQuery({
    queryKey: ['ai', 'farm-plan', areaHa, cropType],
    queryFn: async () => {
      const response = await api.post('/api/v1/ai/analyze/farm-plan', {
        area_ha: areaHa,
        crop_type: cropType,
        soil: soilData,
        weather: weatherData
      });
      return response.data;
    },
    enabled: areaHa > 0 && !!cropType,
  });
}

export function useAIChat() {
  return useMutation({
    mutationFn: async (message: string) => {
      const response = await api.post('/api/v1/ai/chat', { message });
      return response.data;
    },
  });
}
