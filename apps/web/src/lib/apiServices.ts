// apps/web/src/lib/apiServices.ts — Phase 2 unified API service layer
// Uses apiClient from packages/api-client with timeout + graceful fallback

// apiClient import deferred - using native fetch

const TIMEOUT = 8000;

async function fetchSafe<T>(url: string, fallback: T): Promise<{ data: T; source: 'api' | 'mock' }> {
  try {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), TIMEOUT);
    const res = await fetch(url, { signal: ctrl.signal });
    clearTimeout(timer);
    if (!res.ok) throw new Error('API error');
    const data = await res.json();
    return { data, source: 'api' };
  } catch {
    return { data: fallback, source: 'mock' };
  }
}

// —— Accounting ——
export async function getAccountingSummary() {
  return fetchSafe('/api/v1/accounting/summary', {
    revenue: 0, expenses: 0, profit: 0, balance: 0, accounts: [],
  });
}

// —— Education ——
export async function getEducationCourses() {
  return fetchSafe('/api/v1/education/courses', []);
}

export async function getEducationStats() {
  return fetchSafe('/api/v1/education/stats', {
    totalCourses: 0, totalLearners: 0, totalPaths: 0, totalCerts: 0,
  });
}

// —— Dashboard ——
export async function getDashboardStats() {
  return fetchSafe('/api/v1/dashboard/stats', {
    totalUsers: 0, totalProjects: 0, carbonOffset: 0, activeRegions: 0,
  });
}

// —— Community ——
export async function getCommunityPosts() {
  return fetchSafe('/api/v1/community/posts', []);
}

// —— Simulators ——
export async function getSimulatorList() {
  return fetchSafe('/api/v1/simulation/list', []);
}

export async function runSimulation(id: string, params: Record<string, number>) {
  return fetchSafe('/api/v1/simulation/run', { id, status: 'idle', metrics: {} });
}
