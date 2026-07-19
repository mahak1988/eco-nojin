/**
 * ============================================================================
 *  authService — typed API client for authentication endpoints
 * ============================================================================
 */

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
// Configuration
// ---------------------------------------------------------------------------

const API_BASE_URL: string =
  (import.meta.env["VITE_API_BASE_URL"] as string | undefined) ??
  "http://localhost:1337/api";

const TOKEN_STORAGE_KEY = "econojin.access_token";
const REFRESH_TOKEN_STORAGE_KEY = "econojin.refresh_token";

// ---------------------------------------------------------------------------
// Token storage (SSR-safe)
// ---------------------------------------------------------------------------

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
// Internal fetch wrapper
// ---------------------------------------------------------------------------

interface FetchOptions<TBody = unknown> {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  body?: TBody;
  query?: Record<string, string | number | boolean | undefined>;
  signal?: AbortSignal;
  authenticated?: boolean;
}

async function apiFetch<TResponse, TBody = unknown>(
  path: string,
  options: FetchOptions<TBody> = {},
): Promise<TResponse> {
  const { method = "GET", body, query, signal, authenticated = true } = options;

  const url = new URL(`${API_BASE_URL}${path}`);
  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value !== undefined) url.searchParams.set(key, String(value));
    }
  }

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (authenticated) {
    const token = tokenStorage.getAccessToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(url.toString(), {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
    signal,
  });

  if (response.status === 204) {
    return null as unknown as TResponse;
  }

  const payload = (await response.json().catch(() => null)) as
    | { data?: TResponse; message?: string }
    | TResponse
    | ApiError
    | null;

  if (!response.ok) {
    const err = (payload as ApiError | undefined) ?? {
      statusCode: response.status,
      error: response.statusText,
      message: "auth.unknownError",
    };
    throw err as ApiError;
  }

  if (
    payload !== null &&
    typeof payload === "object" &&
    "data" in payload &&
    payload.data !== undefined
  ) {
    return payload.data as TResponse;
  }

  return payload as TResponse;
}

// ---------------------------------------------------------------------------
// Public auth API
// ---------------------------------------------------------------------------

export async function login(credentials: AuthCredentials): Promise<AuthSession> {
  const session = await apiFetch<AuthSession, AuthCredentials>(
    API_ENDPOINTS.auth.login,
    { method: "POST", body: credentials, authenticated: false },
  );
  tokenStorage.set(session);
  return session;
}

export async function register(payload: RegisterPayload): Promise<AuthSession> {
  const session = await apiFetch<AuthSession, RegisterPayload>(
    API_ENDPOINTS.auth.register,
    { method: "POST", body: payload, authenticated: false },
  );
  tokenStorage.set(session);
  return session;
}

export async function logout(): Promise<void> {
  try {
    await apiFetch<void>(API_ENDPOINTS.auth.logout, { method: "POST" });
  } catch {
    // Even if the server call fails, clear locally.
  } finally {
    tokenStorage.clear();
  }
}

export async function getCurrentUser(): Promise<User> {
  return apiFetch<MeResponse>(API_ENDPOINTS.auth.me);
}

export async function forgotPassword(payload: ForgotPasswordRequest): Promise<void> {
  await apiFetch<void, ForgotPasswordRequest>(
    API_ENDPOINTS.auth.forgotPassword,
    { method: "POST", body: payload, authenticated: false },
  );
}

export async function resetPassword(payload: ResetPasswordRequest): Promise<void> {
  await apiFetch<void, ResetPasswordRequest>(
    API_ENDPOINTS.auth.resetPassword,
    { method: "POST", body: payload, authenticated: false },
  );
}

export async function refreshSession(): Promise<AuthSession> {
  const refreshToken = tokenStorage.getRefreshToken();
  if (!refreshToken) {
    throw {
      statusCode: 401,
      error: "Unauthorized",
      message: "auth.sessionExpired",
    } satisfies ApiError;
  }

  const session = await apiFetch<AuthSession, { refreshToken: string }>(
    API_ENDPOINTS.auth.refresh,
    { method: "POST", body: { refreshToken }, authenticated: false },
  );
  tokenStorage.set(session);
  return session;
}
