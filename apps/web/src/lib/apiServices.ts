// Domain API helpers. R1: mock only if VITE_USE_MOCK=true.

import { USE_MOCK } from "../api/http";

const TIMEOUT = 45000;

function readEnv(key: string): string | undefined {
  try {
    return (import.meta as ImportMeta & { env?: Record<string, string> }).env?.[key];
  } catch {
    return undefined;
  }
}

const API_BASE =
  readEnv("VITE_API_BASE_URL") ||
  readEnv("VITE_API_BASE") ||
  readEnv("VITE_API_URL") ||
  "";

function url(path: string): string {
  if (path.startsWith("http")) return path;
  const p = path.startsWith("/") ? path : `/${path}`;
  if (!API_BASE) return p;
  return `${API_BASE.replace(/\/$/, "")}${p}`;
}

export type DataSource = "api" | "mock" | "error";

async function fetchSafe<T>(
  path: string,
  fallback: T,
  init?: RequestInit,
): Promise<{ data: T; source: DataSource; errorMessage?: string }> {
  if (USE_MOCK) {
    return { data: fallback, source: "mock" };
  }
  try {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), TIMEOUT);
    const res = await fetch(url(path), {
      signal: ctrl.signal,
      credentials: "include",
      headers: { Accept: "application/json", ...(init?.headers || {}) },
      ...init,
    });
    clearTimeout(timer);
    if (!res.ok) {
      return {
        data: fallback,
        source: "error",
        errorMessage: `HTTP ${res.status}`,
      };
    }
    const data = (await res.json()) as T;
    return { data, source: "api" };
  } catch (e) {
    const msg = e instanceof Error ? e.message : "network_error";
    return { data: fallback, source: "error", errorMessage: msg };
  }
}

export async function getAccountingSummary() {
  return fetchSafe("/api/v1/accounting/summary", {
    total_income: 0,
    total_expense: 0,
    net_profit: 0,
    current_balance: 0,
    transactions_count: 0,
  });
}

export async function getAccountingAccounts() {
  return fetchSafe("/api/v1/accounting/accounts?limit=20", { items: [], total: 0 });
}

export async function getEducationCourses(page = 1, size = 50) {
  return fetchSafe(`/api/v1/education/courses?page=${page}&size=${size}&sort=-id`, {
    data: [],
    items: [],
    meta: { total: 0, page: 1, pages: 0, size },
    total: 0,
  });
}

export async function getEducationStats() {
  return fetchSafe("/api/v1/education/courses/stats", {
    total_courses: 0,
    total_lessons: 0,
    total_enrollments: 0,
    by_category: {},
    by_level: {},
  });
}

export async function getDashboardStats() {
  return fetchSafe("/api/v1/dashboard/stats", {
    totalUsers: 0,
    totalProjects: 0,
    carbonOffset: 0,
    activeRegions: 0,
  });
}

export async function getCommunityPosts() {
  return fetchSafe("/api/v1/community/posts", { items: [], total: 0 });
}

export async function getSimulatorList() {
  return fetchSafe("/api/v1/simulation/list", []);
}

export async function runSimulation(id: string, params: Record<string, number>) {
  return fetchSafe("/api/v1/simulation/run", {
    id,
    status: "idle",
    metrics: {},
    parameters: params,
  });
}

export async function getApiHealth() {
  return fetchSafe("/health", { status: "unreachable" });
}

export async function seedEducationDemo() {
  if (USE_MOCK) return { data: { seeded: 0, message: "mock" }, source: "mock" as const };
  try {
    const res = await fetch(url("/api/v1/education/seed-demo"), {
      method: "POST",
      credentials: "include",
      headers: { Accept: "application/json" },
    });
    if (!res.ok) throw new Error(String(res.status));
    return { data: await res.json(), source: "api" as const };
  } catch {
    return { data: { seeded: 0, message: "failed" }, source: "error" as const };
  }
}

export async function getScienceStatus() {
  return fetchSafe("/api/v1/science/status", { ok: false, phase: 3 });
}

export async function getScienceRuns() {
  return fetchSafe("/api/v1/science/runs", { data: [], count: 0 });
}

export async function getScienceNdviCanopy(lat: number, lon: number, days = 60) {
  return fetchSafe(`/api/v1/science/ndvi-canopy?lat=${lat}&lon=${lon}&days=${days}`, {
    ndvi: [],
    canopy_cover: [],
    provider: "none",
    count: 0,
  });
}

export async function postAquaCropAdvanced(body: Record<string, unknown>) {
  return fetchSafe(
    "/api/v1/science/aquacrop-advanced",
    { model: "error" },
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    },
  );
}

export async function postSwat(body: Record<string, unknown>) {
  return fetchSafe(
    "/api/v1/science/swat",
    { model: "error" },
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    },
  );
}

export async function postRothC(opts: {
  years?: number;
  soc_t_ha?: number;
  c_input_t_ha_y?: number;
  clay_pct?: number;
}) {
  const q = new URLSearchParams({
    years: String(opts.years ?? 15),
    soc_t_ha: String(opts.soc_t_ha ?? 40),
    c_input_t_ha_y: String(opts.c_input_t_ha_y ?? 1.5),
    clay_pct: String(opts.clay_pct ?? 25),
  });
  return fetchSafe(`/api/v1/science/rothc?${q.toString()}`, { model: "error" }, { method: "POST" });
}

export async function postScienceWatch(body: {
  lat: number;
  lon: number;
  days?: number;
  include_sensors?: boolean;
}) {
  return fetchSafe(
    "/api/v1/science/monitors/watch",
    { events: [], counts: { ok: 0, warning: 0, critical: 0 } },
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    },
  );
}

export async function getScienceMonitors() {
  return fetchSafe("/api/v1/science/monitors", { items: [], count: 0, presets: {} });
}

export async function getScienceThresholds() {
  return fetchSafe("/api/v1/science/monitors/thresholds", {
    effective: [],
    defaults: [],
    overrides: {},
    preset: "default",
  });
}

export async function putScienceThresholds(body: {
  overrides: Record<string, { warning?: number; critical?: number; operator?: string; enabled?: boolean }>;
  merge?: boolean;
  preset?: string;
}) {
  return fetchSafe(
    "/api/v1/science/monitors/thresholds",
    { ok: false },
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    },
  );
}

export async function setScienceThresholdPreset(preset: string) {
  return fetchSafe(
    "/api/v1/science/monitors/thresholds/preset",
    { ok: false },
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ preset }),
    },
  );
}

export async function resetScienceThresholds() {
  return fetchSafe(
    "/api/v1/science/monitors/thresholds/reset",
    { ok: false },
    { method: "POST" },
  );
}
