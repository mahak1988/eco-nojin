/** Typed API helpers for Phase 4 pages (English identifiers only). */

import { apiFetch, v1 } from "./http";

export type ListMeta = {
  total: number;
  page: number;
  size: number;
  pages: number;
};

export type ListEnvelope<T> = {
  data: T[];
  meta: ListMeta;
};

export type Farm = {
  id: number;
  name: string;
  description?: string | null;
  region?: string | null;
  area_ha?: number | null;
  latitude?: number | null;
  longitude?: number | null;
  is_active?: boolean;
};

export type Crop = {
  id: number;
  name: string;
  name_fa?: string | null;
  category: string;
  season?: string | null;
  water_need_mm?: number | null;
  growth_days?: number | null;
};

export type DashboardStats = {
  farms_count?: number;
  crops_count?: number;
  sensors_count?: number;
  status?: string;
  ok?: boolean;
};

export async function fetchFarms(page = 1, size = 20): Promise<ListEnvelope<Farm>> {
  return apiFetch(v1(`/farms?page=${page}&size=${size}`));
}

export async function fetchCrops(page = 1, size = 20): Promise<ListEnvelope<Crop>> {
  return apiFetch(v1(`/crops?page=${page}&size=${size}`));
}

export async function fetchDashboardStats(): Promise<DashboardStats> {
  return apiFetch(v1("/dashboard/stats"));
}

export async function loginRequest(email: string, password: string): Promise<unknown> {
  return apiFetch(v1("/auth/login"), {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function registerRequest(body: {
  email: string;
  password: string;
  full_name?: string;
  role?: string;
  accept_terms?: boolean;
}): Promise<unknown> {
  return apiFetch(v1("/auth/register"), {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function fetchMe(): Promise<unknown> {
  return apiFetch(v1("/auth/me"));
}
