/** Simulation API client. Always exports API_BASE and API_V1 (Vite-safe). */

import type { Series } from "../components/simulators/simulatorsData";

// --- Stable exports (do not rename; many pages import these) ---
export const API_BASE: string = "";
export const API_V1: string = "/api/v1";

const RUN_TIMEOUT = 8000;
const LIST_TIMEOUT = 4000;

export interface ApiSimulator {
  id: string;
  name: string;
  category: string;
  description: string;
  version: string;
}

export interface ApiParam {
  name: string;
  label: string;
  type: string;
  default: unknown;
  description: string;
  unit: string;
  min_value: number | null;
  max_value: number | null;
  options: string[];
  required: boolean;
}

function joinUrl(path: string): string {
  const p = path.startsWith("/") ? path : `/${path}`;
  if (!API_BASE) return p;
  return `${API_BASE.replace(/\/$/, "")}${p}`;
}

async function fetchWithTimeout(url: string, init: RequestInit, timeout: number): Promise<Response> {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeout);
  try {
    return await fetch(url, { ...init, signal: ctrl.signal, credentials: "include" });
  } finally {
    clearTimeout(timer);
  }
}

export async function pingBackend(): Promise<boolean> {
  try {
    const r = await fetchWithTimeout(joinUrl("/health"), {}, LIST_TIMEOUT);
    return r.ok;
  } catch {
    return false;
  }
}

export async function fetchSimulators(): Promise<ApiSimulator[] | null> {
  try {
    const r = await fetchWithTimeout(joinUrl(`${API_V1}/simulation/simulators`), {}, LIST_TIMEOUT);
    if (!r.ok) return null;
    const d = await r.json();
    return Array.isArray(d.simulators) ? d.simulators : null;
  } catch {
    return null;
  }
}

export async function fetchParameters(id: string): Promise<ApiParam[] | null> {
  try {
    const r = await fetchWithTimeout(
      joinUrl(`${API_V1}/simulation/simulators/${encodeURIComponent(id)}`),
      {},
      LIST_TIMEOUT,
    );
    if (!r.ok) return null;
    const d = await r.json();
    return Array.isArray(d.parameters) ? d.parameters : null;
  } catch {
    return null;
  }
}

export async function runOnServer(
  simId: string,
  params: Record<string, unknown>,
): Promise<{ series: Series[]; metrics: Record<string, number> } | null> {
  try {
    const r = await fetchWithTimeout(
      joinUrl(`${API_V1}/simulation/run`),
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ simulator_id: simId, parameters: params }),
      },
      RUN_TIMEOUT,
    );
    if (!r.ok) return null;
    const d = await r.json();
    if (d.status !== "completed") return null;
    const PALETTE = ["#16a34a", "#0284c7", "#dc2626", "#f59e0b", "#7c3aed", "#0d9488"];
    const raw = d.outputs?.series;
    if (!Array.isArray(raw)) return null;
    const series: Series[] = raw
      .filter((s: { values?: unknown }) => Array.isArray(s?.values))
      .map(
        (
          s: {
            key?: string;
            label?: string;
            color?: string;
            values: number[];
            kind?: string;
            fill?: boolean;
          },
          i: number,
        ) => ({
          labelKey: s.key || `s${i}`,
          label: s.label || s.key || `Series ${i}`,
          color: s.color ?? PALETTE[i % PALETTE.length],
          values: s.values,
          kind: (s.kind as Series["kind"]) ?? "line",
          fill: !!s.fill,
        }),
      );
    return series.length ? { series, metrics: d.metrics ?? {} } : null;
  } catch {
    return null;
  }
}
