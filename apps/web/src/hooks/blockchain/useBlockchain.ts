import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api/client';

export function useWallet(address?: string) {
  return useQuery({
    queryKey: ['blockchain', 'wallet', address],
    queryFn: async () => {
      const url = address 
        ? `/api/v1/ecocoin/wallets/${address}`
        : '/api/v1/ecocoin/wallets/me';
      const response = await api.get(url);
      return response.data;
    },
  });
}

export function useTokenStats() {
  return useQuery({
    queryKey: ['blockchain', 'stats'],
    queryFn: async () => {
      const response = await api.get('/api/v1/ecocoin/stats');
      return response.data;
    },
    refetchInterval: 60000, // 1 minute
  });
}

export function useTransactions(address?: string, limit: number = 50) {
  return useQuery({
    queryKey: ['blockchain', 'transactions', address, limit],
    queryFn: async () => {
      const url = address 
        ? `/api/v1/ecocoin/transactions?address=${address}&limit=${limit}`
        : `/api/v1/ecocoin/transactions?limit=${limit}`;
      const response = await api.get(url);
      return response.data;
    },
  });
}

export function useTransfer() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: { to: string; amount: number; token: string }) => {
      const response = await api.post('/api/v1/ecocoin/transfer', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['blockchain'] });
    },
  });
}

export function useStake() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: { amount: number; token: string; lock_days: number }) => {
      const response = await api.post('/api/v1/ecocoin/stake', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['blockchain'] });
    },
  });
}

export function useClaimReward() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: { action: string; quantity?: number }) => {
      const response = await api.post('/api/v1/ecocoin/reward', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['blockchain'] });
    },
  });
}
