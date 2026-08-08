import { apiClient } from "../lib/api/api-client";
import { clearLegacyTokens } from "./http";

export interface LoginPayload {
  email: string;
  password: string;
}

export interface AuthUserDto {
  id: number;
  email: string;
  full_name?: string | null;
  is_active?: boolean;
  is_superuser?: boolean;
  created_at?: string;
}

export interface AuthResponse {
  access_token?: string;
  accessToken?: string;
  refreshToken?: string;
  token_type?: string;
  user?: AuthUserDto;
}

export interface RegisterPayload {
  email: string;
  password: string;
  full_name?: string;
  phone?: string;
  organization?: string;
  role?: "farmer" | "expert" | "viewer";
  accept_terms: boolean;
}

// Login via /api/v1/auth/login with JSON body
export async function login(credentials: { username: string; password: string }) {
  const baseURL = typeof window !== "undefined" 
    ? window.location.origin 
    : (typeof process !== "undefined" && (process as { env?: Record<string, string> }).env?.API_BASE_URL) || "http://localhost:8000";

  const response = await fetch(`${baseURL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: credentials.username, password: credentials.password }),
    credentials: "include",
  });, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: credentials.username, password: credentials.password }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Login failed: ${response.status}`);
  }

  const result = await response.json();
  // Normalize: backend returns accessToken (camelCase), some code expects access_token
  if (result.accessToken && !result.access_token) {
    result.access_token = result.accessToken;
  }
  return result;
}

export const authApi = {
  login,

  register: async (body: RegisterPayload) => {
    const result = await apiClient({
      endpoint: "/api/v1/auth/register",
      method: "POST",
      body: body
    });
    // Normalize token fields
    if (result.accessToken && !result.access_token) {
      result.access_token = result.accessToken;
    }
    return result;
  },

  me: async () => {
    const result = await apiClient({
      endpoint: "/api/v1/users/me",
      method: "GET"
    });
    return result;
  },

  update: async (body: { email?: string; full_name?: string }) => {
    const result = await apiClient({
      endpoint: "/api/v1/users/me",
      method: "PUT",
      body: body
    });
    return result;
  },

  logout: async () => {
    try {
      await fetch("/api/v1/auth/logout", { method: "POST" });
    } catch {
      /* ignore */
    }
    clearLegacyTokens();
  },
};
