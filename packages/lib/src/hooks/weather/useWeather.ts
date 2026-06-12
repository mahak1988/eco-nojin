import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api-client';

export function useCurrentWeather(lat: number, lng: number) {
  return useQuery({
    queryKey: ['weather', 'current', lat, lng],
    queryFn: async () => {
      const response = await api.get(`/api/v1/weather/current?lat=${lat}&lng=${lng}`);
      return response.data;
    },
    enabled: !isNaN(lat) && !isNaN(lng),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 10 * 60 * 1000, // 10 minutes
  });
}

export function useWeatherForecast(lat: number, lng: number, days: number = 7) {
  return useQuery({
    queryKey: ['weather', 'forecast', lat, lng, days],
    queryFn: async () => {
      const response = await api.get(`/api/v1/weather/forecast?lat=${lat}&lng=${lng}&days=${days}`);
      return response.data;
    },
    enabled: !isNaN(lat) && !isNaN(lng),
    staleTime: 30 * 60 * 1000, // 30 minutes
  });
}

export function useHistoricalWeather(
  lat: number, 
  lng: number, 
  startDate: string, 
  endDate: string
) {
  return useQuery({
    queryKey: ['weather', 'historical', lat, lng, startDate, endDate],
    queryFn: async () => {
      const response = await api.get(
        `/api/v1/weather/historical?lat=${lat}&lng=${lng}&start=${startDate}&end=${endDate}`
      );
      return response.data;
    },
    enabled: !isNaN(lat) && !isNaN(lng) && !!startDate && !!endDate,
  });
}
