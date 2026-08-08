import { apiClient } from "../lib/api/api-client";
import { clearLegacyTokens } from "./http";

export interface LoginPayload {
  email: string;
  password: string;
}

export interface AuthUserDto {
  id: string; // Updated to string based on minimal schema
  email: string;
  full_name?: string | null;
  is_active?: boolean;
  is_superuser?: boolean;
  is_verified?: boolean;
  locale?: string;
}

export interface AuthResponse {
  access_token: string;
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

// Special function for login since it requires form URL encoding
export async function login(credentials: { username: string; password: string }) {
  // Get the base URL from environment
  const baseURL = typeof window !== "undefined" 
    ? window.location.origin 
    : process.env.API_BASE_URL || "http://localhost:8000";

  const response = await fetch(`${baseURL}/api/v1/login/access-token`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      username: credentials.username,
      password: credentials.password,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Login failed: ${response.status} ${response.statusText}`);
  }

  const result = await response.json();
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
    
    return result;
  },

  me: async () => {
    const result = await apiClient({
      endpoint: "/api/v1/users/me",
      method: "GET"
    });
    
    return result;
  },

  update: async (body: { email?: string; full_name?: string; locale?: string }) => {
    const result = await apiClient({
      endpoint: "/api/v1/users/me",
      method: "PUT",
      body: body
    });
    
    return result;
  },

  logout: async () => {
    try {
      // We don't have a dedicated logout endpoint in the minimal schema
      // So we'll just clear local storage
    } catch {
      /* ignore */
    }
    clearLegacyTokens();
  },
};