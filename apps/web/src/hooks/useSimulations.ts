/**
 * ============================================================================
 *  useSimulations — React Query hooks for simulation operations
 * ============================================================================
 */

import {
  useQuery,
  useMutation,
  useQueryClient,
  UseQueryOptions,
} from "@tanstack/react-query";
import {
  simulationService,
  Simulation,
  SimulationRunRequest,
  SimulationResult,
} from "@/services/simulationService";

export const simulationKeys = {
  all: ["simulations"] as const,
  lists: () => [...simulationKeys.all, "list"] as const,
  details: () => [...simulationKeys.all, "detail"] as const,
  detail: (id: string) => [...simulationKeys.details(), id] as const,
  results: (id: string) => [...simulationKeys.detail(id), "result"] as const,
};

export const useSimulations = (
  options?: Omit<UseQueryOptions<Simulation[]>, "queryKey" | "queryFn">
) => {
  return useQuery({
    queryKey: simulationKeys.lists(),
    queryFn: () => simulationService.getAll(),
    ...options,
  });
};

export const useSimulation = (
  id: string,
  options?: Omit<UseQueryOptions<Simulation>, "queryKey" | "queryFn">
) => {
  return useQuery({
    queryKey: simulationKeys.detail(id),
    queryFn: () => simulationService.getById(id),
    enabled: !!id,
    ...options,
  });
};

export const useSimulationResult = (
  id: string,
  options?: Omit<UseQueryOptions<SimulationResult>, "queryKey" | "queryFn">
) => {
  return useQuery({
    queryKey: simulationKeys.results(id),
    queryFn: () => simulationService.getResult(id),
    enabled: !!id,
    ...options,
  });
};

export const useRunSimulation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (request: SimulationRunRequest) =>
      simulationService.run(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: simulationKeys.lists() });
    },
  });
};

export const useCancelSimulation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => simulationService.cancel(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: simulationKeys.detail(id) });
    },
  });
};

export const useDeleteSimulation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => simulationService.delete(id),
    onSuccess: (_, id) => {
      queryClient.removeQueries({ queryKey: simulationKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: simulationKeys.lists() });
    },
  });
};

export const useSimulationPolling = (
  id: string,
  options: { enabled?: boolean; interval?: number } = {}
) => {
  const { enabled = true, interval = 2000 } = options;
  
  return useQuery({
    queryKey: simulationKeys.detail(id),
    queryFn: () => simulationService.getById(id),
    enabled: enabled && !!id,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (!data) return false;
      if (data.status === "completed" || data.status === "failed") return false;
      return interval;
    },
  });
};
