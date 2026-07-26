import { apiFetch, v1, API_BASE } from "./http";

export const simulationApi = {
  listSimulators: () =>
    apiFetch<{ simulators?: unknown[] }>(v1("/simulation/simulators")),

  getSimulator: (id: string) =>
    apiFetch(v1(`/simulation/simulators/${encodeURIComponent(id)}`)),

  run: (simulatorId: string, parameters: Record<string, unknown>) =>
    apiFetch(v1("/simulation/run"), {
      method: "POST",
      body: JSON.stringify({ simulator_id: simulatorId, parameters }),
    }),

  health: () => apiFetch(`${API_BASE}/health`),
};
