// Domain API helpers. R1: mock only if VITE_USE_MOCK=true.

import { USE_MOCK } from "../api/http";

const TIMEOUT = 12000;

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
      headers: { Accept: "application/json" },
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
