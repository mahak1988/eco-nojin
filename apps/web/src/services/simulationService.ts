/**
 * ============================================================================
 *  Simulation Service — Run and manage simulations
 * ============================================================================
 */

import { apiClient } from "@/lib/api-client";

export interface Simulation {
  id: string;
  name: string;
  type: "climate" | "hydrology" | "crop" | "carbon" | "flood" | "drought" | "biodiversity" | "soil_erosion";
  status: "pending" | "running" | "completed" | "failed";
  created_at: string;
  completed_at?: string;
  parameters: Record<string, any>;
  results?: Record<string, any>;
}

export interface SimulationRunRequest {
  type: Simulation["type"];
  parameters: Record<string, any>;
  name?: string;
}

export interface SimulationResult {
  id: string;
  data: Record<string, any>;
  summary: {
    titleKey: string;
    metrics: Array<{ labelKey: string; value: string }>;
  };
  warnings: string[];
  duration: number;
}

const ENDPOINTS = {
  simulations: "/simulations",
  simulationById: (id: string) => `/simulations/${id}`,
  run: "/simulations/run",
  result: (id: string) => `/simulations/${id}/result`,
} as const;

export const simulationService = {
  async getAll(): Promise<Simulation[]> {
    const response = await apiClient.get<Simulation[]>(ENDPOINTS.simulations);
    return response.data;
  },
  
  async getById(id: string): Promise<Simulation> {
    const response = await apiClient.get<Simulation>(ENDPOINTS.simulationById(id));
    return response.data;
  },
  
  async run(request: SimulationRunRequest): Promise<Simulation> {
    const response = await apiClient.post<Simulation>(ENDPOINTS.run, request);
    return response.data;
  },
  
  async getResult(id: string): Promise<SimulationResult> {
    const response = await apiClient.get<SimulationResult>(ENDPOINTS.result(id));
    return response.data;
  },
  
  async cancel(id: string): Promise<void> {
    await apiClient.post(`${ENDPOINTS.simulationById(id)}/cancel`);
  },
  
  async delete(id: string): Promise<void> {
    await apiClient.delete(ENDPOINTS.simulationById(id));
  },
};

export default simulationService;
