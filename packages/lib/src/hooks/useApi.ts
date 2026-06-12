import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api-client';

export const queryKeys = {
  dashboard: ['dashboard', 'stats'],
  iot: ['iot', 'stats'],
  ecocoin: { wallet: ['ecocoin', 'wallet'], stats: ['ecocoin', 'stats'] },
  academy: ['academy', 'stats'],
  maintenance: ['maintenance', 'stats'],
  mrv: ['mrv', 'stats'],
  drought: ['drought', 'stats'],
  financial: ['financial', 'dashboard'],
  scientific: ['scientific', 'thresholds'],
  courses: ['academy', 'courses'],
};

export function useDashboardStats() {
  return useQuery({ queryKey: queryKeys.dashboard, queryFn: api.getDashboardStats, staleTime: 5 * 60 * 1000 });
}

export function useIoTStats() {
  return useQuery({ queryKey: queryKeys.iot, queryFn: api.getIoTStats, staleTime: 30 * 1000 });
}

export function useMyWallet() {
  return useQuery({ queryKey: queryKeys.ecocoin.wallet, queryFn: api.getMyWallet });
}

export function useEcoCoinStats() {
  return useQuery({ queryKey: queryKeys.ecocoin.stats, queryFn: api.getEcoCoinStats });
}

export function useAcademyStats() {
  return useQuery({ queryKey: queryKeys.academy, queryFn: api.getAcademyStats });
}

export function useCourses() {
  return useQuery({ queryKey: queryKeys.courses, queryFn: api.getCourses });
}

export function useMaintenanceStats() {
  return useQuery({ queryKey: queryKeys.maintenance, queryFn: api.getMaintenanceStats });
}

export function useMRVStats() {
  return useQuery({ queryKey: queryKeys.mrv, queryFn: api.getMRVStats });
}

export function useDroughtStats() {
  return useQuery({ queryKey: queryKeys.drought, queryFn: api.getDroughtStats });
}

export function useFinancialDashboard() {
  return useQuery({ queryKey: queryKeys.financial, queryFn: api.getFinancialDashboard });
}

export function useThresholds() {
  return useQuery({ queryKey: queryKeys.scientific, queryFn: api.getThresholds });
}
