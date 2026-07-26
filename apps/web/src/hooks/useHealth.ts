import { useQuery } from "@tanstack/react-query";
import { simulationApi } from "../api/simulation.api";
import type { HealthResponse } from "../types/common";

export function useApiHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: async (): Promise<HealthResponse> => {
      try {
        return (await simulationApi.health()) as HealthResponse;
      } catch {
        return { status: "unreachable" };
      }
    },
    refetchInterval: 60_000,
  });
}
