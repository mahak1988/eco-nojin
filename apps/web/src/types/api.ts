/**
 * ============================================================================
 *  API request/response contracts — typed end-to-end
 * ============================================================================
 */

import type {
  AuthCredentials,
  AuthSession,
  CarbonMetric,
  Document,
  PaginationMeta,
  RegisterPayload,
  SoilMetric,
  User,
  Watershed,
} from "@/types";

// ---------------------------------------------------------------------------
// HTTP method types
// ---------------------------------------------------------------------------

export type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

export interface RequestOptions<
  TBody = unknown,
  TQuery extends Record<string, unknown> = Record<string, never>,
> {
  method?: HttpMethod;
  body?: TBody;
  query?: TQuery;
  headers?: Readonly<Record<string, string>>;
  signal?: AbortSignal;
  baseUrl?: string;
  raw?: boolean;
}

// ---------------------------------------------------------------------------
// Endpoint path constants
// ---------------------------------------------------------------------------

export const API_ENDPOINTS = {
  auth: {
    login: "/auth/login",
    register: "/auth/register",
    logout: "/auth/logout",
    refresh: "/auth/refresh",
    me: "/auth/me",
    forgotPassword: "/auth/forgot-password",
    resetPassword: "/auth/reset-password",
  },
  users: {
    list: "/users",
    byId: (id: string | number): string => `/users/${id}`,
    me: "/users/me",
    register: "/users/register",
    login: "/users/login",
  },
  admin: {
    dashboard: "/admin",
    settings: "/admin/settings",
    settingByKey: (key: string): string => `/admin/settings/${encodeURIComponent(key)}`,
    auditLogs: "/admin/audit-logs",
    reports: "/admin/reports",
  },
  documents: {
    list: "/documents",
    byId: (id: string): string => `/documents/${id}`,
    upload: "/documents/upload",
  },
  watersheds: {
    list: "/hydrology/watersheds",
    byId: (id: string): string => `/hydrology/watersheds/${id}`,
  },
  carbon: {
    list: "/carbon/metrics",
  },
  soil: {
    list: "/soil/metrics",
  },
} as const;

// ---------------------------------------------------------------------------
// Request payloads
// ---------------------------------------------------------------------------

export type LoginRequest = AuthCredentials;
export type RegisterRequest = RegisterPayload;

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  newPassword: string;
}

export interface DocumentListQuery {
  page?: number;
  pageSize?: number;
  search?: string;
  tags?: readonly string[];
  status?: "draft" | "published" | "archived";
}

export interface WatershedListQuery {
  page?: number;
  pageSize?: number;
  province?: string;
  status?: "monitored" | "unmonitored" | "critical";
}

// ---------------------------------------------------------------------------
// Response payloads
// ---------------------------------------------------------------------------

export type LoginResponse = AuthSession;
export type RegisterResponse = AuthSession;
export type MeResponse = User;

export interface DocumentListResponse {
  items: readonly Document[];
  meta: PaginationMeta;
}

export interface WatershedListResponse {
  items: readonly Watershed[];
  meta: PaginationMeta;
}

export interface CarbonListResponse {
  items: readonly CarbonMetric[];
  meta: PaginationMeta;
}

export interface SoilListResponse {
  items: readonly SoilMetric[];
  meta: PaginationMeta;
}

// ---------------------------------------------------------------------------
// Pagination helper types
// ---------------------------------------------------------------------------

export interface PaginatedResult<T> {
  items: readonly T[];
  meta: PaginationMeta;
}

export interface ListParams {
  page?: number;
  pageSize?: number;
  search?: string;
}
