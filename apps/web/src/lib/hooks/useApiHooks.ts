import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api/client';

// Dashboard
export function useDashboardStats() {
  return useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: () => api.getDashboardStats(),
    staleTime: 5 * 60 * 1000,
  });
}

// IoT
export function useIoTStats() {
  return useQuery({
    queryKey: ['iot', 'stats'],
    queryFn: () => api.getIoTStats(),
    staleTime: 30 * 1000,
  });
}

// EcoCoin
export function useMyWallet() {
  return useQuery({
    queryKey: ['ecocoin', 'wallet'],
    queryFn: () => api.getMyWallet(),
  });
}

export function useTransferTokens() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: any) => api.transferTokens(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ecocoin', 'wallet'] });
    },
  });
}

// Academy
export function useAcademyStats() {
  return useQuery({
    queryKey: ['academy', 'stats'],
    queryFn: () => api.getAcademyStats(),
  });
}

// Add more hooks as needed...
