/** Simulation backend client — re-exports API_BASE/API_V1 for older pages. */

import type { Series } from "../components/simulators/simulatorsData";
import { API_BASE as HTTP_API_BASE, API_V1 as HTTP_API_V1 } from "../api/http";

/** Empty string = same-origin / Vite proxy; absolute URL only if set in env. */
export const API_BASE: string =
  HTTP_API_BASE ||
  (typeof import.meta !== "undefined"
    ? String(
        (import.meta as ImportMeta & { env?: Record<string, string> }).env?.VITE_API_BASE_URL ||
          (import.meta as ImportMeta & { env?: Record<string, string> }).env?.VITE_API_BASE ||
          "",
      )
    : "");

export const API_V1: string =
  HTTP_API_V1 ||
  (typeof import.meta !== "undefined"
    ? String(
        (import.meta as ImportMeta & { env?: Record<string, string> }).env?.VITE_API_V1 || "/api/v1",
      )
    : "/api/v1");

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

function joinUrl(base: string, path: string): string {
  if (!base) return path.startsWith("/") ? path : `/${path}`;
  return `${base.replace(/\/$/, "")}${path.startsWith("/") ? path : `/${path}`}`;
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
    const r = await fetchWithTimeout(joinUrl(API_BASE, "/health"), {}, LIST_TIMEOUT);
    return r.ok;
  } catch {
    return false;
  }
}

export async function fetchSimulators(): Promise<ApiSimulator[] | null> {
  try {
    const r = await fetchWithTimeout(
      joinUrl(API_BASE, `${API_V1}/simulation/simulators`),
      {},
      LIST_TIMEOUT,
    );
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
      joinUrl(API_BASE, `${API_V1}/simulation/simulators/${encodeURIComponent(id)}`),
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
      joinUrl(API_BASE, `${API_V1}/simulation/run`),
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
    const raw = d.outputs?.series;
    if (Array.isArray(raw)) {
      series = raw
        .filter((s: { values?: unknown }) => Array.isArray(s?.values))
        .map((s: { key?: string; label?: string; color?: string; values: number[]; kind?: string; fill?: boolean }, i: number) => ({
          labelKey: s.key || `s${i}`,
          label: s.label || s.key || `Series ${i}`,
          color: s.color ?? PALETTE[i % PALETTE.length],
          values: s.values,
          kind: (s.kind as Series["kind"]) ?? "line",
          fill: !!s.fill,
        }));
    }
    return series.length ? { series, metrics: d.metrics ?? {} } : null;
  } catch {
    return null;
  }
}
