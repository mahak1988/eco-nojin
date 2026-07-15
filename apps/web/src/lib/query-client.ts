/**
 * ============================================================================
 *  Query Client — React Query configuration
 * ============================================================================
 */

import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      gcTime: 1000 * 60 * 10,
      retry: (failureCount: number, error: any) => {
        if (error?.response?.status === 401) return false;
        if (error?.response?.status === 403) return false;
        if (error?.response?.status === 404) return false;
        return failureCount < 2;
      },
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
    },
    mutations: {
      retry: 1,
    },
  },
});

export default queryClient;
