// Unified API service layer with timeout + graceful mock fallback.
// Always prefixes VITE_API_BASE_URL so calls hit the backend, not Vite.

const TIMEOUT = 8000;

const API_BASE =
  (typeof import.meta !== "undefined" &&
    (import.meta as ImportMeta & { env?: Record<string, string> }).env?.VITE_API_BASE_URL) ||
  (typeof import.meta !== "undefined" &&
    (import.meta as ImportMeta & { env?: Record<string, string> }).env?.VITE_API_BASE) ||
  "http://localhost:8000";

function url(path: string): string {
  if (path.startsWith("http")) return path;
  return `${API_BASE}${path.startsWith("/") ? path : `/${path}`}`;
}

async function fetchSafe<T>(path: string, fallback: T): Promise<{ data: T; source: "api" | "mock" }> {
  try {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), TIMEOUT);
    const res = await fetch(url(path), {
      signal: ctrl.signal,
      headers: { Accept: "application/json" },
    });
    clearTimeout(timer);
    if (!res.ok) throw new Error(`API ${res.status}`);
    const data = (await res.json()) as T;
    return { data, source: "api" };
  } catch {
    return { data: fallback, source: "mock" };
  }
}

export async function getAccountingSummary() {
  return fetchSafe("/api/v1/accounting/summary", {
    revenue: 0,
    expenses: 0,
    profit: 0,
    balance: 0,
    accounts: [],
  });
}

export async function getEducationCourses() {
  return fetchSafe("/api/v1/education/courses", []);
}

export async function getEducationStats() {
  return fetchSafe("/api/v1/education/stats", {
    totalCourses: 0,
    totalLearners: 0,
    totalPaths: 0,
    totalCerts: 0,
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
  return fetchSafe("/api/v1/community/posts", []);
}

export async function getSimulatorList() {
  return fetchSafe("/api/v1/simulation/list", []);
}

export async function runSimulation(id: string, params: Record<string, number>) {
  return fetchSafe("/api/v1/simulation/run", { id, status: "idle", metrics: {}, parameters: params });
}

export async function getApiHealth() {
  return fetchSafe("/health", { status: "unreachable" });
}
