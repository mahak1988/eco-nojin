import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../client';
import { ENDPOINTS } from '../endpoints';
import { toast } from 'react-hot-toast';
import type {
  EcoCoinBalance,
  EcoCoinTransaction,
  EcoCoinTransferRequest,
  EcoCoinTransferResponse,
  EcoCoinReward,
  EcoCoinHistory,
  EcoCoinStats,
} from '../types/ecocoin.types';

// ============================================================================
// Get Balance Hook
// ============================================================================

export function useEcoCoinBalance() {
  return useQuery({
    queryKey: ['ecocoin', 'balance'],
    queryFn: async (): Promise<EcoCoinBalance> => {
      const response = await apiClient.get<EcoCoinBalance>(
        ENDPOINTS.ECOCOIN.BALANCE
      );
      return response;
    },
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000, // Refresh every minute
    retry: 2,
  });
}

// ============================================================================
// Get Transactions Hook
// ============================================================================

export function useEcoCoinTransactions(page: number = 1, pageSize: number = 20) {
  return useQuery({
    queryKey: ['ecocoin', 'transactions', page, pageSize],
    queryFn: async (): Promise<EcoCoinHistory> => {
      const response = await apiClient.get<EcoCoinHistory>(
        ENDPOINTS.ECOCOIN.TRANSACTIONS,
        { page, page_size: pageSize }
      );
      return response;
    },
    staleTime: 60 * 1000, // 1 minute
  });
}

// ============================================================================
// Transfer EcoCoin Hook
// ============================================================================

export function useTransferEcoCoin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: EcoCoinTransferRequest): Promise<EcoCoinTransferResponse> => {
      const response = await apiClient.post<EcoCoinTransferResponse>(
        ENDPOINTS.ECOCOIN.TRANSFER,
        data
      );
      return response;
    },

    onSuccess: (data) => {
      toast.success(`انتقال موفق! ${data.message}`);
      
      // Invalidate queries to refresh data
      queryClient.invalidateQueries({ queryKey: ['ecocoin'] });
    },

    onError: (error: any) => {
      const message = error?.PersianMessage || error?.message || 'خطا در انتقال';
      toast.error(message);
    },
  });
}

// ============================================================================
// Get Rewards Hook
// ============================================================================

export function useEcoCoinRewards() {
  return useQuery({
    queryKey: ['ecocoin', 'rewards'],
    queryFn: async (): Promise<EcoCoinReward[]> => {
      const response = await apiClient.get<EcoCoinReward[]>(
        ENDPOINTS.ECOCOIN.REWARDS
      );
      return response;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// ============================================================================
// Get Stats Hook
// ============================================================================

export function useEcoCoinStats() {
  return useQuery({
    queryKey: ['ecocoin', 'stats'],
    queryFn: async (): Promise<EcoCoinStats> => {
      const response = await apiClient.get<EcoCoinStats>(
        '/ecocoin/stats'
      );
      return response;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// ============================================================================
// Combined Hook for Dashboard
// ============================================================================

export function useEcoCoinDashboard() {
  const balance = useEcoCoinBalance();
  const transactions = useEcoCoinTransactions(1, 10);
  const rewards = useEcoCoinRewards();
  const stats = useEcoCoinStats();

  return {
    balance,
    transactions,
    rewards,
    stats,
    isLoading: balance.isLoading || transactions.isLoading,
    isError: balance.isError || transactions.isError,
  };
}