/**
 * Econojin API Client — Phase 2
 * Centralized fetch with credentials + optional Bearer token
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

interface FetchOptions extends Omit<RequestInit, 'body'> {
  body?: unknown
}

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

function authHeaders(): Record<string, string> {
  const token =
    localStorage.getItem('access_token') ||
    localStorage.getItem('accessToken') ||
    localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function apiFetch<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const { body, headers, ...rest } = options
  const res = await fetch(`${BASE_URL}${path}`, {
    ...rest,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders(),
      ...headers,
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  if (!res.ok) {
    let message = `HTTP ${res.status}`
    try {
      const err = await res.json()
      message = err.detail ?? err.message ?? message
    } catch {
      /* ignore */
    }
    throw new ApiError(res.status, typeof message === 'string' ? message : JSON.stringify(message))
  }

  if (res.status === 204) return undefined as unknown as T
  return res.json() as Promise<T>
}

// ── Auth ───────────────────────────────────────────────────────────────────────

export interface LoginPayload {
  email: string
  password: string
}
export interface AuthResponse {
  access_token: string
  token_type: string
  user?: unknown
}
export interface UserResponse {
  id: number
  email: string
  full_name?: string
  is_active: boolean
  is_superuser: boolean
}

export const auth = {
  login: (data: LoginPayload) => apiFetch<AuthResponse>('/auth/login', { method: 'POST', body: data }),
  logout: () => apiFetch<void>('/auth/logout', { method: 'POST' }),
  me: () => apiFetch<UserResponse>('/auth/me'),
  refresh: () => apiFetch<AuthResponse>('/auth/refresh', { method: 'POST' }),
}

// ── Farms ──────────────────────────────────────────────────────────────────────

export interface FarmCreate {
  name: string
  region?: string
  area_ha?: number
  latitude?: number
  longitude?: number
  description?: string
}

export interface Farm extends FarmCreate {
  id: number
  is_active: boolean
  created_at?: string
  updated_at?: string
}

export interface ListResponse<T> {
  data: T[]
  meta: { total: number; page: number; size: number; pages: number }
}

export const farms = {
  list: (page = 1, size = 20, search?: string) => {
    const params = new URLSearchParams({ page: String(page), size: String(size) })
    if (search) params.set('search', search)
    return apiFetch<ListResponse<Farm>>(`/farms?${params}`)
  },
  get: (id: number) => apiFetch<Farm>(`/farms/${id}`),
  create: (data: FarmCreate) => apiFetch<Farm>('/farms', { method: 'POST', body: data }),
  update: (id: number, data: Partial<FarmCreate>) =>
    apiFetch<Farm>(`/farms/${id}`, { method: 'PATCH', body: data }),
  delete: (id: number) => apiFetch<void>(`/farms/${id}`, { method: 'DELETE' }),
  seedDemo: () => apiFetch<unknown>('/farms/seed-demo', { method: 'POST' }),
}

// ── Weather ────────────────────────────────────────────────────────────────────

export const weather = {
  current: (lat: number, lon: number) =>
    apiFetch<Record<string, unknown>>(`/weather/current?lat=${lat}&lon=${lon}`),
  forecast: (lat: number, lon: number, days = 7) =>
    apiFetch<unknown>(`/weather/forecast?lat=${lat}&lon=${lon}&days=${days}`),
  alerts: (lat: number, lon: number) =>
    apiFetch<unknown[]>(`/weather/alerts?lat=${lat}&lon=${lon}`),
}

// ── Risks ──────────────────────────────────────────────────────────────────────

export interface RiskPredictRequest {
  latitude: number
  longitude: number
  crop_type: string
  area_ha: number
  soil_type?: string
  irrigation_method?: string
  season?: string
}

export const risks = {
  predict: (data: RiskPredictRequest) =>
    apiFetch<Record<string, unknown>>('/risks/predict', { method: 'POST', body: data }),
  predictDemo: () => apiFetch<Record<string, unknown>>('/risks/predict/demo'),
}

// ── Economics ──────────────────────────────────────────────────────────────────

export const economics = {
  listAnalyses: (page = 1, size = 20) =>
    apiFetch<ListResponse<Record<string, unknown>>>(`/economics/analyses?page=${page}&size=${size}`),
  costBenefit: (data: {
    initial_investment: number
    annual_benefits: number
    annual_costs: number
    years: number
    discount_rate: number
  }) => apiFetch<Record<string, unknown>>('/economics/cost-benefit', { method: 'POST', body: data }),
}

// ── Satellite ──────────────────────────────────────────────────────────────────

export const satellite = {
  geeStatus: () => apiFetch<{ available: boolean; provider?: string }>('/satellite/gee/status'),
  timeseries: (lat: number, lon: number, days: number) =>
    apiFetch<{ data?: unknown[] }>(`/satellite/timeseries?lat=${lat}&lon=${lon}&days=${days}`),
  changeDetection: (lat: number, lon: number, days: number) =>
    apiFetch<Record<string, unknown>>(`/satellite/change-detection?lat=${lat}&lon=${lon}&days=${days}`, {
      method: 'POST',
    }),
  mrvBands: (red: number, nir: number) =>
    apiFetch<Record<string, number>>('/satellite/mrv/bands', {
      method: 'POST',
      body: { red, nir },
    }),
}

// ── Simulators ─────────────────────────────────────────────────────────────────

export const simulators = {
  list: (lang = 'fa') => apiFetch<{ simulators?: unknown[] }>(`/simulators?lang=${lang}`),
  get: (id: string, lang = 'fa') => apiFetch<Record<string, unknown>>(`/simulators/${id}?lang=${lang}`),
  run: (simulator_id: string, parameters: Record<string, unknown>) =>
    apiFetch<Record<string, unknown>>('/simulators/run', {
      method: 'POST',
      body: { simulator_id, parameters },
    }),
}

// ── Accounting ─────────────────────────────────────────────────────────────────

export interface Account {
  id: number | string
  code: string
  name: string
  type?: string
  account_type?: string
  balance?: number
  currency?: string
  is_active?: boolean
  created_at?: string
}

export const accounting = {
  listAccounts: () => apiFetch<Account[] | { data: Account[]; items?: Account[] }>('/accounting/accounts'),
  seedDemo: () => apiFetch<unknown>('/accounting/seed-demo', { method: 'POST' }),
  summary: () => apiFetch<Record<string, unknown>>('/accounting/summary'),
  listInvoices: () => apiFetch<unknown[] | { data: unknown[] }>('/accounting/invoices'),
  listPayments: () => apiFetch<unknown[] | { data: unknown[] }>('/accounting/payments'),
  listJournals: () => apiFetch<unknown[] | { data: unknown[] }>('/accounting/journals'),
}

export { apiFetch, BASE_URL }
