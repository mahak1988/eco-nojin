/** Farms API client */

import { USE_MOCK } from "../api/http";

function readEnv(key: string): string | undefined {
  try {
    return (import.meta as ImportMeta & { env?: Record<string, string> }).env?.[key];
  } catch {
    return undefined;
  }
}

const API_BASE =
  readEnv("VITE_API_BASE_URL") || readEnv("VITE_API_BASE") || readEnv("VITE_API_URL") || "";

function url(path: string): string {
  if (path.startsWith("http")) return path;
  const p = path.startsWith("/") ? path : `/${path}`;
  if (!API_BASE) return p;
  return `${API_BASE.replace(/\/$/, "")}${p}`;
}

export interface FarmDto {
  id: number;
  name: string;
  description?: string | null;
  region?: string | null;
  area_ha?: number | null;
  latitude?: number | null;
  longitude?: number | null;
  geojson?: string | null;
  is_active?: boolean;
  created_at?: string;
}

export interface FarmList {
  data: FarmDto[];
  meta: { total: number; page: number; pages: number; size: number };
}

export interface FarmCreateBody {
  name: string;
  description?: string;
  region?: string;
  area_ha?: number;
  latitude?: number;
  longitude?: number;
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  if (USE_MOCK) throw new Error("Mock mode — farms need live API");
  const res = await fetch(url(path), {
    credentials: "include",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    let msg = `HTTP ${res.status}`;
    try {
      const j = await res.json();
      msg = j.detail || j.error?.message || msg;
      if (Array.isArray(j.detail)) msg = j.detail.map((d: { msg?: string }) => d.msg).join(", ");
    } catch {
      /* ignore */
    }
    throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const farmsApi = {
  list: (page = 1, size = 20, search = "") =>
    req<FarmList>(
      `/api/v1/farms?page=${page}&size=${size}${search ? `&search=${encodeURIComponent(search)}` : ""}`,
    ),
  get: (id: number) => req<FarmDto>(`/api/v1/farms/${id}`),
  create: (body: FarmCreateBody) =>
    req<FarmDto>(`/api/v1/farms`, { method: "POST", body: JSON.stringify(body) }),
  update: (id: number, body: Partial<FarmCreateBody>) =>
    req<FarmDto>(`/api/v1/farms/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
  remove: (id: number) => req<void>(`/api/v1/farms/${id}`, { method: "DELETE" }),
  geojson: (id: number) => req<Record<string, unknown>>(`/api/v1/farms/${id}/geojson`),
};
