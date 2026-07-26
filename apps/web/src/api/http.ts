/**
 * Shared fetch helper for Vite frontend.
 * English-only module per engineering standards.
 */

export const API_BASE =
  (typeof import.meta !== "undefined" &&
    (import.meta as ImportMeta & { env?: Record<string, string> }).env?.VITE_API_BASE_URL) ||
  (typeof import.meta !== "undefined" &&
    (import.meta as ImportMeta & { env?: Record<string, string> }).env?.VITE_API_BASE) ||
  "http://localhost:8000";

export const API_V1 =
  (typeof import.meta !== "undefined" &&
    (import.meta as ImportMeta & { env?: Record<string, string> }).env?.VITE_API_V1) ||
  "/api/v1";

export class ApiError extends Error {
  status: number;
  requestId?: string;
  data?: unknown;

  constructor(message: string, status: number, requestId?: string, data?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.requestId = requestId;
    this.data = data;
  }
}

function authHeader(): Record<string, string> {
  try {
    const token =
      localStorage.getItem("access_token") || localStorage.getItem("token") || "";
    return token ? { Authorization: `Bearer ${token}` } : {};
  } catch {
    return {};
  }
}

export async function apiFetch<T>(
  path: string,
  init: RequestInit = {},
  timeoutMs = 12000,
): Promise<T> {
  const url = path.startsWith("http") ? path : `${API_BASE}${path.startsWith("/") ? path : `/${path}`}`;
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(url, {
      ...init,
      signal: ctrl.signal,
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        ...authHeader(),
        ...(init.headers || {}),
      },
    });
    const requestId = res.headers.get("x-request-id") || undefined;
    const text = await res.text();
    let data: unknown = null;
    if (text) {
      try {
        data = JSON.parse(text);
      } catch {
        data = text;
      }
    }
    if (!res.ok) {
      const msg =
        (data as { message?: string; detail?: string; error?: string })?.message ||
        (data as { detail?: string })?.detail ||
        (data as { error?: string })?.error ||
        res.statusText ||
        "Request failed";
      throw new ApiError(String(msg), res.status, requestId, data);
    }
    return data as T;
  } finally {
    clearTimeout(timer);
  }
}

export function v1(path: string): string {
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${API_V1}${p}`;
}
