import { apiFetch, clearLegacyTokens, v1 } from "./http";

export interface LoginPayload {
  email: string;
  password: string;
}

export interface AuthUserDto {
  id: number;
  email: string;
  full_name?: string | null;
  role?: string;
  is_active?: boolean;
  is_superuser?: boolean;
}

export interface AuthResponse {
  accessToken?: string;
  refreshToken?: string;
  access_token?: string;
  token_type?: string;
  user?: AuthUserDto;
}

export interface RegisterPayload {
  email: string;
  password: string;
  full_name?: string;
  role?: string;
}

function accessOf(res: AuthResponse): string {
  return res.accessToken || res.access_token || "";
}

export const authApi = {
  login: async (body: LoginPayload) => {
    const res = await apiFetch<AuthResponse>(v1("/auth/login"), {
      method: "POST",
      body: JSON.stringify(body),
    });
    return { ...res, access_token: accessOf(res) };
  },

  register: async (body: RegisterPayload) => {
    const res = await apiFetch<AuthResponse>(v1("/auth/register"), {
      method: "POST",
      body: JSON.stringify(body),
    });
    return { ...res, access_token: accessOf(res) };
  },

  me: () =>
    apiFetch<AuthUserDto>(v1("/auth/me")).catch(() =>
      apiFetch<AuthUserDto>(v1("/users/me")).catch(() => null),
    ),

  logout: async () => {
    try {
      await apiFetch(v1("/auth/logout"), { method: "POST" });
    } catch {
      /* ignore */
    }
    clearLegacyTokens();
  },

  refresh: () =>
    apiFetch<AuthResponse>(v1("/auth/refresh"), { method: "POST" }).then((res) => ({
      ...res,
      access_token: accessOf(res),
    })),
};
