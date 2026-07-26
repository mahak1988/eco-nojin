import { apiFetch, v1 } from "./http";

export interface LoginPayload {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type?: string;
  expires_in?: number;
}

export interface RegisterPayload {
  email: string;
  password: string;
  full_name?: string;
}

export const authApi = {
  login: (body: LoginPayload) =>
    apiFetch<TokenResponse>(v1("/auth/login"), {
      method: "POST",
      body: JSON.stringify(body),
    }),

  register: (body: RegisterPayload) =>
    apiFetch(v1("/auth/register"), {
      method: "POST",
      body: JSON.stringify(body),
    }),

  me: () => apiFetch(v1("/users/me")).catch(() => null),
};
