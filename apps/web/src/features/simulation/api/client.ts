/**
 * Typed client for /api/v1/simulation/* endpoints.
 * Respects VITE_USE_MOCK (Constitution R1).
 */

const API_BASE = import.meta.env.VITE_API_URL ?? "";
const USE_MOCK = String(import.meta.env.VITE_USE_MOCK ?? "").toLowerCase() === "true";

export type SimulationModel =
  | "richards"
  | "sebs"
  | "daycent"
  | "saint_venant"
  | "uncertainty"
  | "qaoa"
  | "nitrogen"
  | "soil_chemistry"
  | "canopy"
  | "shuttleworth";

export interface RunRequest {
  model: SimulationModel;
  params: Record<string, number | string | boolean>;
}

export interface RunResponse {
  job_id: string;
  status: "queued" | "running" | "done" | "error";
  result?: Record<string, unknown>;
  metrics?: { NSE?: number; RMSE?: number; KGE?: number };
  error?: string;
}

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    credentials: "include",
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
  return res.json() as Promise<T>;
}

function mockRun(req: RunRequest): RunResponse {
  return {
    job_id: `mock-${req.model}-${Date.now()}`,
    status: "done",
    result: { model: req.model, params: req.params, note: "mock" },
    metrics: { NSE: 0.82, RMSE: 0.15, KGE: 0.78 },
  };
}

export async function runSimulation(req: RunRequest): Promise<RunResponse> {
  if (USE_MOCK) return mockRun(req);
  return postJson<RunResponse>("/api/v1/simulation/run", req);
}

export async function getSimulationStatus(jobId: string): Promise<RunResponse> {
  if (USE_MOCK) {
    return { job_id: jobId, status: "done", metrics: { NSE: 0.82, RMSE: 0.15, KGE: 0.78 } };
  }
  const res = await fetch(`${API_BASE}/api/v1/simulation/runs/${jobId}`, {
    credentials: "include",
    headers: { Accept: "application/json" },
  });
  if (!res.ok) throw new Error(`API ${res.status}`);
  return res.json() as Promise<RunResponse>;
}
