// Domain API helpers. R1: mock only if VITE_USE_MOCK=true.

import { USE_MOCK } from "../api/http";

const TIMEOUT = 60000;

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

function authHeaders(): Record<string, string> {
  try {
    const token =
      localStorage.getItem("access_token") || localStorage.getItem("token") || "";
    return token ? { Authorization: `Bearer ${token}` } : {};
  } catch {
    return {};
  }
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
      ...init,
      headers: {
        Accept: "application/json",
        ...authHeaders(),
        ...(init?.headers || {}),
      },
    });
    clearTimeout(timer);
    if (!res.ok) {
      let detail = "";
      try {
        const body = await res.json();
        detail =
          (body as { detail?: string | { message?: string } }).detail
            ? typeof (body as { detail: unknown }).detail === "string"
              ? String((body as { detail: string }).detail)
              : String(
                  ((body as { detail: { message?: string } }).detail as { message?: string })
                    ?.message || "",
                )
            : "";
      } catch {
        /* ignore */
      }
      const hint =
        res.status === 401
          ? " (ورود لازم است — /login)"
          : res.status === 403
            ? " (مجوز کافی نیست)"
            : "";
      return {
        data: fallback,
        source: "error",
        errorMessage: detail
          ? `HTTP ${res.status}: ${detail}${hint}`
          : `HTTP ${res.status}${hint}`,
      };
    }
    const data = (await res.json()) as T;
    return { data, source: "api" };
  } catch (e) {
    const msg = e instanceof Error ? e.message : "network_error";
    return { data: fallback, source: "error", errorMessage: msg };
  }
}

export type ClimateZone = {
  id: string;
  label_en?: string;
  label_fa?: string;
  koppen_hint?: string;
  traits?: string[];
  priority_packages?: string[];
  default_models?: string[];
  risk_triggers?: string[];
};

export type SatellitePlatform = {
  id: string;
  name: string;
  domains?: string[];
  api?: string[];
  assets?: string[];
  access?: string;
  priority_mrv?: boolean;
  notes_en?: string;
};

export async function getClimateZones() {
  return fetchSafe("/api/v1/science/climate-zones", {
    zones: [] as ClimateZone[],
    count: 0,
    note_fa: "",
    note_en: "",
  });
}

export async function applyClimateZonePackage(zoneId: string) {
  return fetchSafe(
    `/api/v1/science/climate-zones/${zoneId}/apply`,
    { ok: false },
    { method: "POST", headers: { "Content-Type": "application/json" } },
  );
}

export async function getSatelliteCatalog() {
  return fetchSafe("/api/v1/science/satellite-catalog", {
    platforms: [] as SatellitePlatform[],
    count: 0,
    mrv_stack_recommended: [] as string[],
  });
}

export async function getIndicesCatalog() {
  return fetchSafe("/api/v1/science/indices-catalog", {
    fao_water_models: [],
    drought_indices: [],
    process_models: [],
  });
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

export async function getDashboardOverview() {
  return fetchSafe("/api/v1/dashboard/overview", {
    ok: false,
    runs: [],
    science: { ok: false },
    soil_snapshot: {},
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
      headers: { Accept: "application/json", ...authHeaders() },
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

export async function postRothCFull(body: Record<string, unknown>) {
  return fetchSafe(
    "/api/v1/science/rothc/run",
    { model: "error" },
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    },
  );
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
  overrides: Record<
    string,
    { warning?: number; critical?: number; operator?: string; enabled?: boolean }
  >;
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

export async function postMlTrain(n_samples = 1000) {
  return fetchSafe(`/api/v1/ml/train?n_samples=${n_samples}`, { ok: false }, { method: "POST" });
}

export async function postMlPredict(body: Record<string, number>) {
  return fetchSafe(
    "/api/v1/ml/predict",
    { yield_relative_pred: 0, risk_label: "unknown" },
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    },
  );
}

export async function postMlPredictFromWatch(lat: number, lon: number, days = 40) {
  return fetchSafe(
    `/api/v1/ml/predict-from-watch?lat=${lat}&lon=${lon}&days=${days}`,
    { yield_relative_pred: 0, risk_label: "unknown" },
    { method: "POST" },
  );
}

export async function getMlStatus() {
  return fetchSafe("/api/v1/ml/status", { ok: false });
}

export async function getMlSensitivity(rel_step = 0.1) {
  return fetchSafe(`/api/v1/ml/sensitivity?rel_step=${rel_step}`, {
    oat: {},
    coefficient_importance: {},
    partial_dependence: [],
  });
}

export async function postMlSensitivity(body: {
  baseline?: Record<string, number>;
  rel_step?: number;
  pd_features?: string[];
  pd_points?: number;
}) {
  return fetchSafe(
    "/api/v1/ml/sensitivity",
    { oat: {}, coefficient_importance: {}, partial_dependence: [] },
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    },
  );
}