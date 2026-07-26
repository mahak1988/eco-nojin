/**
 * Shared fetch helper (R19: no axios).
 * R1: mock only when VITE_USE_MOCK=true.
 */

function readEnv(key: string): string | undefined {
  try {
    return (import.meta as ImportMeta & { env?: Record<string, string> }).env?.[key];
  } catch {
    return undefined;
  }
}

/** Empty = same-origin (Vite proxy). */
export const API_BASE =
  readEnv("VITE_API_BASE_URL") ||
  readEnv("VITE_API_BASE") ||
  readEnv("VITE_API_URL") ||
  "";

export const API_V1 = readEnv("VITE_API_V1") || "/api/v1";

/** R1: explicit mock mode — never silent fake success without this flag. */
export const USE_MOCK = (readEnv("VITE_USE_MOCK") || "").toLowerCase() === "true";

export class ApiError extends Error {
  status: number;
  requestId?: string;
  code?: string;
  data?: unknown;

  constructor(
    message: string,
    status: number,
    requestId?: string,
    data?: unknown,
    code?: string,
  ) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.requestId = requestId;
    this.data = data;
    this.code = code;
  }
}

function authHeader(): Record<string, string> {
  // Temporary until R5 HttpOnly cookies fully replace bearer storage
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
      credentials: "include", // prepare for R5 HttpOnly cookies
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
      const errObj = data as {
        error?: { message?: string; code?: string };
        message?: string;
        detail?: string;
      };
      const msg =
        errObj?.error?.message ||
        errObj?.message ||
        errObj?.detail ||
        res.statusText ||
        "Request failed";
      throw new ApiError(String(msg), res.status, requestId, data, errObj?.error?.code);
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
