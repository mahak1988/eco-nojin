/**
 * ============================================================================
 *  Type Definitions — Core types for the Eco Nojin platform
 * ============================================================================
 */

// ---------------------------------------------------------------------------
// User Roles
// ---------------------------------------------------------------------------

export type UserRole = 'farmer' | 'student' | 'expert' | 'manager' | 'researcher' | 'user';

export interface User {
  id: string | number;
  email: string;
  username?: string;
  displayName?: string;
  full_name?: string;
  role: UserRole;
  status?: string;
  is_active?: boolean;
  is_superuser?: boolean;
  createdAt?: string;
  updatedAt?: string;
  emailVerified?: boolean;
}

// ---------------------------------------------------------------------------
// Authentication Types
// ---------------------------------------------------------------------------

export interface AuthCredentials {
  email?: string;
  username?: string;
  password: string;
  rememberMe?: boolean;
}

export interface AuthSession {
  accessToken: string;
  refreshToken?: string;
  user: User;
  expiresAt?: number;
}

export interface RegisterPayload {
  email: string;
  password: string;
  full_name?: string;
  role?: UserRole;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  new_password: string;
}

export interface MeResponse {
  id: string | number;
  email: string;
  username?: string;
  full_name?: string;
  role?: UserRole;
  is_active?: boolean;
  is_superuser?: boolean;
  created_at?: string;
  updated_at?: string;
  email_verified?: boolean;
}

// ---------------------------------------------------------------------------
// API Error Types
// ---------------------------------------------------------------------------

export interface ApiError {
  statusCode: number;
  error: string;
  message: string | string[];
  detail?: string | Record<string, any>;
}

// ---------------------------------------------------------------------------
// Common Types
// ---------------------------------------------------------------------------

export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}