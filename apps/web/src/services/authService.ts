/**
 * ============================================================================
 *  authService — typed API client for authentication endpoints
 * ============================================================================
 * 
 * بازنویسی شده برای استفاده از api-client جدید
 */

import { apiClient } from "@/lib/api-client";
import type {
  ApiError,
  AuthCredentials,
  AuthSession,
  ForgotPasswordRequest,
  MeResponse,
  RegisterPayload,
  ResetPasswordRequest,
  User,
} from "@/types";
import { API_ENDPOINTS } from "@/types/api";

// ---------------------------------------------------------------------------
// Token storage (SSR-safe)
// ---------------------------------------------------------------------------

const TOKEN_STORAGE_KEY = "econojin.access_token";
const REFRESH_TOKEN_STORAGE_KEY = "econojin.refresh_token";

export const tokenStorage = {
  getAccessToken(): string | null {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem(TOKEN_STORAGE_KEY);
  },
  getRefreshToken(): string | null {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY);
  },
  set(session: AuthSession): void {
    if (typeof window === "undefined") return;
    window.localStorage.setItem(TOKEN_STORAGE_KEY, session.accessToken);
    if (session.refreshToken) {
      window.localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, session.refreshToken);
    }
  },
  clear(): void {
    if (typeof window === "undefined") return;
    window.localStorage.removeItem(TOKEN_STORAGE_KEY);
    window.localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY);
  },
} as const;

// ---------------------------------------------------------------------------
// Public auth API
// ---------------------------------------------------------------------------

export async function login(credentials: AuthCredentials): Promise<AuthSession> {
  const response = await apiClient.post<AuthSession>(
    API_ENDPOINTS.auth.login,
    credentials
  );
  tokenStorage.set(response.data);
  return response.data;
}

export async function register(payload: RegisterPayload): Promise<AuthSession> {
  const response = await apiClient.post<AuthSession>(
    API_ENDPOINTS.auth.register,
    payload
  );
  tokenStorage.set(response.data);
  return response.data;
}

export async function logout(): Promise<void> {
  try {
    await apiClient.post(API_ENDPOINTS.auth.logout);
  } catch {
    // Even if the server call fails, clear locally.
  } finally {
    tokenStorage.clear();
  }
}

export async function getCurrentUser(): Promise<User> {
  const response = await apiClient.get<MeResponse>(API_ENDPOINTS.auth.me);
  const me = response.data;
  
  return {
    id: (me as any).id ?? "",
    email: (me as any).email ?? "",
    username: (me as any).username ?? (me as any).email ?? "",
    displayName: (me as any).displayName ?? (me as any).full_name ?? (me as any).email ?? "",
    status: (me as any).status ?? "active",
    createdAt: (me as any).createdAt ?? new Date().toISOString(),
    updatedAt: (me as any).updatedAt ?? new Date().toISOString(),
    is_active: (me as any).is_active ?? true,
    role: (me as any).role ?? "user",
    emailVerified: (me as any).emailVerified ?? (me as any).email_verified ?? false,
  } as User;
}

export async function forgotPassword(payload: ForgotPasswordRequest): Promise<void> {
  await apiClient.post(API_ENDPOINTS.auth.forgotPassword, payload);
}

export async function resetPassword(payload: ResetPasswordRequest): Promise<void> {
  await apiClient.post(API_ENDPOINTS.auth.resetPassword, payload);
}

export async function refreshSession(): Promise<AuthSession> {
  const refreshToken = tokenStorage.getRefreshToken();
  if (!refreshToken) {
    throw {
      statusCode: 401,
      error: "Unauthorized",
      message: "auth.sessionExpired",
    } as ApiError;
  }
  
  const response = await apiClient.post<AuthSession>(
    API_ENDPOINTS.auth.refresh,
    { refreshToken }
  );
  tokenStorage.set(response.data);
  return response.data;
}
