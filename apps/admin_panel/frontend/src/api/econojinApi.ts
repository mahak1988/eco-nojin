/**
 * Econojin API Client
 * Centralized fetch wrapper برای تمام endpoint‌های بک‌اند
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

// ── Generic Fetch ──────────────────────────────────────────────────────────────

interface FetchOptions extends Omit<RequestInit, 'body'> {
  body?: unknown;
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function apiFetch<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const { body, headers, ...rest } = options;
  const res = await fetch(`${BASE_URL}${path}`, {
    ...rest,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    let message = `HTTP ${res.status}`;
    try {
      const err = await res.json();
      message = err.detail ?? err.message ?? message;
    } catch {}
    throw new ApiError(res.status, message);
  }

  if (res.status === 204) return undefined as unknown as T;
  return res.json() as Promise<T>;
}

// ── Auth ───────────────────────────────────────────────────────────────────────

export interface LoginPayload { email: string; password: string }
export interface AuthResponse { access_token: string; token_type: string; user?: unknown }
export interface UserResponse { id: number; email: string; full_name?: string; is_active: boolean; is_superuser: boolean }

export const auth = {
  login: (data: LoginPayload) => apiFetch<AuthResponse>('/auth/login', { method: 'POST', body: data }),
  logout: () => apiFetch<void>('/auth/logout', { method: 'POST' }),
  me: () => apiFetch<UserResponse>('/auth/me'),
  refresh: () => apiFetch<AuthResponse>('/auth/refresh', { method: 'POST' }),
};

// ── Dashboard ─────────────────────────────────────────────────────────────────

export const dashboard = {
  stats: () => apiFetch<Record<string, unknown>>('/dashboard/stats'),
  overview: () => apiFetch<Record<string, unknown>>('/dashboard/overview'),
};

// ── Farms ──────────────────────────────────────────────────────────────────────

export interface FarmCreate {
  name: string;
  region?: string;
  area_ha?: number;
  latitude?: number;
  longitude?: number;
  description?: string;
}

export interface Farm extends FarmCreate {
  id: number;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface ListResponse<T> {
  data: T[];
  meta: { total: number; page: number; size: number; pages: number };
}

export const farms = {
  list: (page = 1, size = 20, search?: string) => {
    const params = new URLSearchParams({ page: String(page), size: String(size) });
    if (search) params.set('search', search);
    return apiFetch<ListResponse<Farm>>(`/farms?${params}`);
  },
  get: (id: number) => apiFetch<Farm>(`/farms/${id}`),
  create: (data: FarmCreate) => apiFetch<Farm>('/farms', { method: 'POST', body: data }),
  update: (id: number, data: Partial<FarmCreate>) => apiFetch<Farm>(`/farms/${id}`, { method: 'PATCH', body: data }),
  delete: (id: number) => apiFetch<void>(`/farms/${id}`, { method: 'DELETE' }),
  seedDemo: () => apiFetch<unknown>('/farms/seed-demo', { method: 'POST' }),
  geojson: (id: number) => apiFetch<unknown>(`/farms/${id}/geojson`),
};

// ── Crops ──────────────────────────────────────────────────────────────────────

export interface CropCreate {
  name: string;
  category?: string;
  water_need_mm?: number;
  growth_days?: number;
  description?: string;
  name_fa?: string;
  scientific_name?: string;
  season?: string;
}

export interface Crop extends CropCreate {
  id: number;
  is_active: boolean;
  created_at?: string;
}

export interface IrrigationCalcRequest {
  area_ha: number;
  et0_mm_day: number;
  kc?: number;
  efficiency?: number;
  days?: number;
}

export interface IrrigationCalcResponse {
  etc_mm_day: number;
  etc_mm_period: number;
  gross_mm_period: number;
  volume_m3: number;
  volume_liters: number;
  recommended_interval_days?: number;
}

export const crops = {
  list: (page = 1, size = 20) => apiFetch<ListResponse<Crop>>(`/crops?page=${page}&size=${size}`),
  get: (id: number) => apiFetch<Crop>(`/crops/${id}`),
  create: (data: CropCreate) => apiFetch<Crop>('/crops', { method: 'POST', body: data }),
  update: (id: number, data: Partial<CropCreate>) => apiFetch<Crop>(`/crops/${id}`, { method: 'PATCH', body: data }),
  delete: (id: number) => apiFetch<void>(`/crops/${id}`, { method: 'DELETE' }),
  calculateIrrigation: (data: IrrigationCalcRequest) =>
    apiFetch<IrrigationCalcResponse>('/crops/irrigation/calculate', { method: 'POST', body: data }),
  diseaseRules: () => apiFetch<unknown>('/crops/disease-rules'),
  yieldPrediction: () => apiFetch<unknown>('/crops/yield-prediction'),
  rotationPlan: (data: unknown) => apiFetch<unknown>('/crops/rotation-plan', { method: 'POST', body: data }),
  seedDemo: () => apiFetch<unknown>('/crops/seed-demo', { method: 'POST' }),
};

// ── Water ──────────────────────────────────────────────────────────────────────

export const water = {
  dashboard: () => apiFetch<Record<string, unknown>>('/water/dashboard'),
  balance: () => apiFetch<unknown>('/water/balance'),
  sources: () => apiFetch<unknown[]>('/water/sources'),
  quality: () => apiFetch<unknown[]>('/water/quality'),
  irrigationSystems: () => apiFetch<unknown>('/water/irrigation/systems'),
  irrigationSchedules: () => apiFetch<unknown>('/water/irrigation/schedules'),
  createIrrigationSchedule: (data: unknown) =>
    apiFetch<unknown>('/water/irrigation/schedules', { method: 'POST', body: data }),
  calculateIrrigation: (data: unknown) =>
    apiFetch<unknown>('/water/irrigation/calculate', { method: 'POST', body: data }),
};

// ── Weather ────────────────────────────────────────────────────────────────────

export const weather = {
  current: (lat: number, lon: number) => apiFetch<unknown>(`/weather/current?lat=${lat}&lon=${lon}`),
  forecast: (lat: number, lon: number, days = 7) =>
    apiFetch<unknown>(`/weather/forecast?lat=${lat}&lon=${lon}&days=${days}`),
  historical: (lat: number, lon: number, start: string, end: string) =>
    apiFetch<unknown>(`/weather/historical?lat=${lat}&lon=${lon}&start=${start}&end=${end}`),
  alerts: (lat: number, lon: number) => apiFetch<unknown[]>(`/weather/alerts?lat=${lat}&lon=${lon}`),
  climate: (lat: number, lon: number) => apiFetch<unknown>(`/weather/climate?lat=${lat}&lon=${lon}`),
};

// ── Risks ──────────────────────────────────────────────────────────────────────

export interface RiskPredictRequest {
  latitude: number;
  longitude: number;
  crop_type: string;
  area_ha: number;
  soil_type?: string;
  irrigation_method?: string;
  season?: string;
}

export const risks = {
  predict: (data: RiskPredictRequest) => apiFetch<Record<string, unknown>>('/risks/predict', { method: 'POST', body: data }),
  predictDemo: () => apiFetch<Record<string, unknown>>('/risks/predict/demo'),
};

// ── Economics ──────────────────────────────────────────────────────────────────

export interface EconomicAnalysisCreate {
  title?: string;
  description?: string;
  [key: string]: unknown;
}

export interface CostBenefitRequest {
  initial_investment: number;
  annual_benefits: number;
  annual_costs: number;
  years: number;
  discount_rate: number;
}

export const economics = {
  listAnalyses: (page = 1, size = 20) =>
    apiFetch<ListResponse<Record<string, unknown>>>(`/economics/analyses?page=${page}&size=${size}`),
  getAnalysis: (id: number) => apiFetch<Record<string, unknown>>(`/economics/analyses/${id}`),
  createAnalysis: (data: EconomicAnalysisCreate) =>
    apiFetch<Record<string, unknown>>('/economics/analyses', { method: 'POST', body: data }),
  updateAnalysis: (id: number, data: Partial<EconomicAnalysisCreate>) =>
    apiFetch<Record<string, unknown>>(`/economics/analyses/${id}`, { method: 'PATCH', body: data }),
  deleteAnalysis: (id: number) => apiFetch<void>(`/economics/analyses/${id}`, { method: 'DELETE' }),
  costBenefit: (data: CostBenefitRequest) =>
    apiFetch<Record<string, unknown>>('/economics/cost-benefit', { method: 'POST', body: data }),
  npv: (cashFlows: number[], discountRate: number) =>
    apiFetch<{ npv: number }>('/economics/npv', { method: 'POST', body: { cash_flows: cashFlows, discount_rate: discountRate } }),
  irr: (cashFlows: number[]) =>
    apiFetch<{ irr: number }>('/economics/irr', { method: 'POST', body: { cash_flows: cashFlows } }),
};

// ── Users ──────────────────────────────────────────────────────────────────────

export const users = {
  list: () => apiFetch<UserResponse[]>('/users'),
  getMe: () => apiFetch<UserResponse>('/users/me'),
  updateMe: (data: Partial<UserResponse>) => apiFetch<UserResponse>('/users/me', { method: 'PUT', body: data }),
};
