/**
 * Admin Panel API Client
 * Connected to backend /admin/* endpoints via proxy (Vite → FastAPI)
 * Phase 1 remaining: Authorization interceptor + consistent error handling
 */

import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1/admin',
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
})

// ==========================================
// Auth interceptor (Phase 1 remaining task)
// ==========================================

api.interceptors.request.use((config) => {
  // Prefer explicit Bearer token from localStorage (legacy / hybrid auth)
  const token =
    localStorage.getItem('access_token') ||
    localStorage.getItem('accessToken') ||
    localStorage.getItem('token')
  if (token) {
    config.headers = (config.headers ?? {}) as any
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear stale tokens; redirect only if not already on login
      localStorage.removeItem('access_token')
      localStorage.removeItem('accessToken')
      localStorage.removeItem('token')
      if (typeof window !== 'undefined' && !window.location.pathname.includes('login')) {
        // Soft signal – admin shell may handle redirect via auth context
        console.warn('[adminApi] 401 Unauthorized – token cleared')
      }
    }
    return Promise.reject(error)
  }
)

export { api }

// ==========================================
// Types
// ==========================================

export interface DashboardData {
  user_count: number
  active_user_count: number
  superuser_count: number
  total_settings: number
  total_audit_logs: number
  total_reports: number
}

export interface AdminSetting {
  id: number
  key: string
  value: string
  description: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface AdminUser {
  id: number
  email: string
  full_name: string | null
  phone: string | null
  organization: string | null
  role: string
  is_active: boolean
  is_superuser: boolean
  created_at: string
  updated_at: string
}

export interface AuditLog {
  id: number
  actor_id: number | null
  actor_email: string | null
  event_type: string
  event_data: string | null
  created_at: string
}

export interface SystemReport {
  id: number
  report_name: string
  status: string
  report_data: string | null
  created_at: string
  completed_at: string | null
}

export interface SystemHealth {
  database: string
  database_latency_ms: number | null
  redis: string
  redis_latency_ms: number | null
  uptime_seconds: number | null
  total_users: number
  active_users_last_24h: number
  total_api_routes: number
  environment: string
  python_version: string
  cache_status?: Record<string, unknown>
}

export interface ReportGenerateResponse {
  id: number
  report_name: string
  status: string
  message: string
}

// ==========================================
// Dashboard
// ==========================================

export async function fetchDashboard(): Promise<DashboardData> {
  const { data } = await api.get('/')
  return data
}

// ==========================================
// Settings
// ==========================================

export async function fetchSettings(limit = 100, offset = 0): Promise<AdminSetting[]> {
  const { data } = await api.get('/settings', { params: { limit, offset } })
  return data
}

export async function upsertSetting(
  key: string,
  payload: { value?: string; description?: string; is_active?: boolean }
): Promise<AdminSetting> {
  const { data } = await api.put(`/settings/${key}`, payload)
  return data
}

// ==========================================
// Users
// ==========================================

export interface UserQueryParams {
  search?: string
  role?: string
  is_active?: boolean
  is_superuser?: boolean
  limit?: number
  offset?: number
}

export async function fetchUsers(params: UserQueryParams = {}): Promise<AdminUser[]> {
  const { data } = await api.get('/users', { params })
  return data
}

export async function fetchUserDetail(userId: number): Promise<AdminUser> {
  const { data } = await api.get(`/users/${userId}`)
  return data
}

export async function updateUserStatus(userId: number, isActive: boolean): Promise<AdminUser> {
  const { data } = await api.patch(`/users/${userId}/status`, { is_active: isActive })
  return data
}

export async function updateUserRole(userId: number, isSuperuser: boolean): Promise<AdminUser> {
  const { data } = await api.patch(`/users/${userId}/role`, { is_superuser: isSuperuser })
  return data
}

export async function deleteUser(userId: number): Promise<void> {
  await api.delete(`/users/${userId}`)
}

// ==========================================
// Audit Logs
// ==========================================

export interface AuditLogQueryParams {
  event_type?: string
  actor_email?: string
  date_from?: string
  date_to?: string
  limit?: number
  offset?: number
}

export async function fetchAuditLogs(params: AuditLogQueryParams = {}): Promise<AuditLog[]> {
  const { data } = await api.get('/audit-logs', { params })
  return data
}

// ==========================================
// Reports
// ==========================================

export async function fetchReports(limit = 100, offset = 0): Promise<SystemReport[]> {
  const { data } = await api.get('/reports', { params: { limit, offset } })
  return data
}

export async function generateReport(
  reportName: string,
  reportType: string = 'csv'
): Promise<ReportGenerateResponse> {
  const { data } = await api.post('/reports', { report_name: reportName, report_type: reportType })
  return data
}

// ==========================================
// System Health
// ==========================================

export async function fetchSystemHealth(): Promise<SystemHealth> {
  const { data } = await api.get('/health')
  return data
}
