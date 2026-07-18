/**
 * ============================================================================
 *  adminService — typed API client for the Admin Panel
 * ============================================================================
 *
 *  Wraps every backend endpoint under /admin/* and the user-management
 *  endpoints under /users/* that require superuser privileges.
 *
 *  All return types live in @/types so backend ↔ frontend contracts stay
 *  in one place.
 * ============================================================================
 */

import { apiClient } from "../lib/api-client";
import type {
  AdminDashboardSummary,
  AdminSetting,
  AuditLog,
  SystemReport,
  User,
} from "../types";
import { API_ENDPOINTS } from "../types/api";

// ---------------------------------------------------------------------------
// Query parameter shapes
// ---------------------------------------------------------------------------

export interface AdminListQuery {
  limit?: number;
  offset?: number;
}

export interface AuditLogsQuery extends AdminListQuery {
  eventType?: string;
}

export interface UpdateSettingPayload {
  value?: string;
  description?: string;
  isActive?: boolean;
}

// ---------------------------------------------------------------------------
// Users (superuser-only endpoints on /api/v1/users/*)
// ---------------------------------------------------------------------------

export const adminUserService = {
  /** GET /users — list all users (paginated). */
  async list(params?: AdminListQuery): Promise<User[]> {
    const response = await apiClient.get<User[]>(API_ENDPOINTS.users.list, {
      params,
    });
    return response.data;
  },

  /** DELETE /users/{id} — deactivate (soft delete) a user. */
  async deactivate(userId: number): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.users.byId(userId));
  },
};

// ---------------------------------------------------------------------------
// Settings (CRUD on /admin/settings)
// ---------------------------------------------------------------------------

export const adminSettingsService = {
  /** GET /admin/settings — paginated list. */
  async list(params?: AdminListQuery): Promise<AdminSetting[]> {
    const response = await apiClient.get<AdminSetting[]>(
      API_ENDPOINTS.admin.settings,
      { params },
    );
    return response.data;
  },

  /** PUT /admin/settings/{key} — upsert a setting by key. */
  async upsert(key: string, payload: UpdateSettingPayload): Promise<AdminSetting> {
    const response = await apiClient.put<AdminSetting>(
      API_ENDPOINTS.admin.settingByKey(key),
      payload,
    );
    return response.data;
  },
};

// ---------------------------------------------------------------------------
// Audit logs
// ---------------------------------------------------------------------------

export const adminAuditLogsService = {
  /** GET /admin/audit-logs — optional eventType filter + pagination. */
  async list(params?: AuditLogsQuery): Promise<AuditLog[]> {
    const response = await apiClient.get<AuditLog[]>(
      API_ENDPOINTS.admin.auditLogs,
      { params },
    );
    return response.data;
  },
};

// ---------------------------------------------------------------------------
// System reports
// ---------------------------------------------------------------------------

export const adminReportsService = {
  /** GET /admin/reports — paginated list of system reports. */
  async list(params?: AdminListQuery): Promise<SystemReport[]> {
    const response = await apiClient.get<SystemReport[]>(
      API_ENDPOINTS.admin.reports,
      { params },
    );
    return response.data;
  },
};

// ---------------------------------------------------------------------------
// Dashboard summary
// ---------------------------------------------------------------------------

export const adminDashboardService = {
  /** GET /admin — top-level KPI summary. */
  async getSummary(): Promise<AdminDashboardSummary> {
    const response = await apiClient.get<AdminDashboardSummary>(
      API_ENDPOINTS.admin.dashboard,
    );
    return response.data;
  },
};

// ---------------------------------------------------------------------------
// Backward-compatible flat export (legacy code used adminService.* directly)
// ---------------------------------------------------------------------------

export const adminService = {
  // Dashboard
  getDashboardSummary: adminDashboardService.getSummary,

  // Settings
  listSettings: adminSettingsService.list,
  updateSetting: (key: string, payload: Partial<AdminSetting>) =>
    adminSettingsService.upsert(key, {
      value: payload.value,
      description: payload.description,
      isActive: payload.is_active,
    }),

  // Audit logs
  listAuditLogs: adminAuditLogsService.list,

  // Reports
  listReports: adminReportsService.list,

  // Users
  listUsers: adminUserService.list,
  deactivateUser: adminUserService.deactivate,
};

export default adminService;
