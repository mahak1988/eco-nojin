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
  EcoCoinDashboard,
} from '../types/ecocoin.types';

// ============================================================================
// Get Balance Hook
// ============================================================================

export function useEcoCoinBalance(address?: string) {
  return useQuery<EcoCoinBalance>({
    queryKey: ['ecocoin', 'balance', address],
    queryFn: async () => {
      if (!address) throw new Error('Wallet address is required');
      const { data } = await apiClient.get<EcoCoinBalance>(
        ENDPOINTS.ECOCOIN.BALANCE(address)
      );
      return data;
    },
    enabled: !!address,
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000, // Refresh every minute
    retry: 2,
  });
}

// ============================================================================
// Get Transactions Hook
// ============================================================================

export function useEcoCoinTransactions(address?: string, limit: number = 50) {
  return useQuery<EcoCoinHistory>({
    queryKey: ['ecocoin', 'transactions', address, limit],
    queryFn: async () => {
      if (!address) throw new Error('Wallet address is required');
      const { data } = await apiClient.get<EcoCoinHistory>(
        ENDPOINTS.ECOCOIN.TRANSACTIONS(address, limit)
      );
      return data;
    },
    enabled: !!address,
    staleTime: 60 * 1000, // 1 minute
  });
}

// ============================================================================
// Transfer EcoCoin Hook
// ============================================================================

export function useTransferEcoCoin() {
  const queryClient = useQueryClient();

  return useMutation<EcoCoinTransferResponse, Error, EcoCoinTransferRequest>({
    mutationFn: async (payload) => {
      const { data } = await apiClient.post<EcoCoinTransferResponse>(
        ENDPOINTS.ECOCOIN.TRANSFER,
        payload
      );
      return data;
    },

    onSuccess: (data) => {
      toast.success(`Transfer successful: ${data.tx_hash.slice(0, 10)}...`);
      
      // Invalidate queries to refresh data
      queryClient.invalidateQueries({ queryKey: ['ecocoin'] });
    },

    onError: (error) => {
      toast.error(`Transfer failed: ${error.message}`);
    },
  });
}

// ============================================================================
// Get Rewards Hook
// ============================================================================

export function useEcoCoinRewards() {
  return useQuery<EcoCoinReward[]>({
    queryKey: ['ecocoin', 'rewards'],
    queryFn: async () => {
      const { data } = await apiClient.get<EcoCoinReward[]>(
        ENDPOINTS.ECOCOIN.REWARDS
      );
      return data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// ============================================================================
// Get Stats Hook
// ============================================================================

export function useEcoCoinStats() {
  return useQuery<EcoCoinStats>({
    queryKey: ['ecocoin', 'stats'],
    queryFn: async () => {
      const { data } = await apiClient.get<EcoCoinStats>(
        ENDPOINTS.ECOCOIN.STATS
      );
      return data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// ============================================================================
// Combined Hook for Dashboard
// ============================================================================

export function useEcoCoinDashboard(address?: string) {
  const balance = useEcoCoinBalance(address);
  const transactions = useEcoCoinTransactions(address, 10);
  const rewards = useEcoCoinRewards();
  const stats = useEcoCoinStats();

  return {
    balance,
    transactions,
    rewards,
    stats,
    isLoading:
      balance.isLoading ||
      transactions.isLoading ||
      rewards.isLoading ||
      stats.isLoading,
    isError: !!(balance.error || transactions.error || rewards.error || stats.error),
  };
}
