// apps/web/src/lib/simulationApi.ts
// API client for the simulation backend, with timeout + graceful fallback.
// If the backend is unreachable, callers get `null` and fall back to the
// client engine (lesson: Vite "failed to fetch" robustness — never a white screen).
import type { Series } from "../components/simulators/simulatorsData";

export const API_BASE =
  (typeof import.meta !== "undefined" && (import.meta as any).env?.VITE_API_BASE) ||
  "http://localhost:8000";
export const API_V1 =
  (typeof import.meta !== "undefined" && (import.meta as any).env?.VITE_API_V1) ||
  "/api/v1";

const RUN_TIMEOUT = 8000;
const LIST_TIMEOUT = 4000;

export interface ApiSimulator {
  id: string; name: string; category: string; description: string; version: string;
}
export interface ApiParam {
  name: string; label: string; type: string; default: any; description: string;
  unit: string; min_value: number | null; max_value: number | null;
  options: string[]; required: boolean;
}

async function fetchWithTimeout(url: string, init: RequestInit, timeout: number): Promise<Response> {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeout);
  try {
    return await fetch(url, { ...init, signal: ctrl.signal });
  } finally {
    clearTimeout(timer);
  }
}

export async function pingBackend(): Promise<boolean> {
  try {
    const r = await fetchWithTimeout(`${API_BASE}/health`, {}, LIST_TIMEOUT);
    return r.ok;
  } catch {
    return false;
  }
}

/** List all registered simulators (null if backend unreachable). */
export async function fetchSimulators(): Promise<ApiSimulator[] | null> {
  try {
    const r = await fetchWithTimeout(`${API_BASE}${API_V1}/simulation/simulators`, {}, LIST_TIMEOUT);
    if (!r.ok) return null;
    const d = await r.json();
    return Array.isArray(d.simulators) ? d.simulators : null;
  } catch {
    return null;
  }
}

/** Get parameter schema for one simulator (null if unreachable). */
export async function fetchParameters(id: string): Promise<ApiParam[] | null> {
  try {
    const r = await fetchWithTimeout(
      `${API_BASE}${API_V1}/simulation/simulators/${encodeURIComponent(id)}`, {}, LIST_TIMEOUT);
    if (!r.ok) return null;
    const d = await r.json();
    return Array.isArray(d.parameters) ? d.parameters : null;
  } catch {
    return null;
  }
}

/** Run a simulation on the backend; null on any failure (-> client fallback). */
export async function runOnServer(
  simId: string,
  params: Record<string, any>,
): Promise<{ series: Series[]; metrics: Record<string, number> } | null> {
  try {
    const r = await fetchWithTimeout(
      `${API_BASE}${API_V1}/simulation/run`,
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
    let series: Series[] = [];
    // ۱. standard outputs.series (new simulators)
    const raw = d.outputs?.series;
    if (Array.isArray(raw)) {
      series = raw.filter((s: any) => Array.isArray(s?.values)).map((s: any, i: number) => ({
        labelKey: s.key, label: s.label, color: s.color ?? PALETTE[i % PALETTE.length],
        values: s.values, kind: s.kind ?? "line", fill: !!s.fill,
      }));
    }
    // ۲. fallback: legacy charts (dict of numeric lists)
    if (series.length === 0 && d.charts && typeof d.charts === "object") {
      let ci = 0;
      for (const [key, vals] of Object.entries(d.charts)) {
        if (Array.isArray(vals) && vals.length && typeof vals[0] === "number") {
          series.push({ labelKey: key, label: key, color: PALETTE[ci++ % PALETTE.length],
            values: vals as number[], kind: "line", fill: ci === 1 });
        }
      }
    }
    // ۳. fallback: a single series from a scalar metric (so something renders)
    if (series.length === 0 && d.metrics && Object.keys(d.metrics).length) {
      const entries = Object.entries(d.metrics).filter(([, v]) => typeof v === "number");
      if (entries.length) {
        series.push({ labelKey: "metrics", label: entries.map(([k]) => k).join(" / "),
          color: PALETTE[0], values: entries.map(([, v]) => v as number), kind: "bars" });
      }
    }
    // ۴. final fallback: numeric values directly in outputs
    if (series.length === 0 && d.outputs && typeof d.outputs === "object") {
      const numEntries = Object.entries(d.outputs).filter(([, v]) => typeof v === "number");
      if (numEntries.length) {
        series.push({ labelKey: "outputs", label: numEntries.map(([k]) => k).join(" / "),
          color: PALETTE[0], values: numEntries.map(([, v]) => v as number), kind: "bars" });
      }
    }
    return series.length ? { series, metrics: d.metrics ?? {} } : null;
  } catch {
    return null;
  }
}
