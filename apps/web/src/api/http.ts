/**
 * Shared fetch helper.
 * Default API_BASE is empty → same-origin requests (Vite proxy in dev).
 * Set VITE_API_BASE_URL only when FE and BE are on different hosts.
 */

function readEnv(key: string): string | undefined {
  try {
    return (import.meta as ImportMeta & { env?: Record<string, string> }).env?.[key];
  } catch {
    return undefined;
  }
}

/** Empty string = relative URL (recommended for Vite proxy). */
export const API_BASE =
  readEnv("VITE_API_BASE_URL") ||
  readEnv("VITE_API_BASE") ||
  readEnv("VITE_API_URL") ||
  "";

export const API_V1 = readEnv("VITE_API_V1") || "/api/v1";

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

export function buildUrl(path: string): string {
  if (path.startsWith("http")) return path;
  const p = path.startsWith("/") ? path : `/${path}`;
  if (!API_BASE) return p;
  return `${API_BASE.replace(/\/$/, "")}${p}`;
}

export async function apiFetch<T>(
  path: string,
  init: RequestInit = {},
  timeoutMs = 12000,
): Promise<T> {
  const url = buildUrl(path);
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(url, {
      ...init,
      signal: ctrl.signal,
      headers: {
        Accept: "application/json",
        ...(init.body ? { "Content-Type": "application/json" } : {}),
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
