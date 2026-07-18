/**
 * Agriculture Schools API Service
 */
const API_BASE = (import.meta as any)?.env/?VITE_API_BASE_URL || "";

export interface School {
  id: number;
  name: string;
  province: string;
  city: string;
  type: "university" | "institute" | "training-center";
  established: number | null;
  students_count: number;
  fields: string[];
  website: string | null;
  logo: string;
  created_at: string;
  updated_at: string;
}

export interface SchoolsResponse {
  schools: School[];
  total: number;
}

export interface SchoolsStats {
  total_schools: number;
  total_students: number;
  provinces_count: number;
  by_type: Record<string, number>;
}

export const agricultureSchoolsApi = {
  async list(params?: { search?: string; type?: string; limit?: number; offset?: number }): Promise<SchoolsResponse> {
    const searchParams = new URLSearchParams();
    if (params?.search) searchParams.set("search", params.search);
    if (params?.type) searchParams.set("type", params.type);
    if (params?.limit) searchParams.set("limit", String(params.limit));
    if (params?.offset) searchParams.set("offset", String(params.offset));
    const qs = searchParams.toString();
    const res = await fetch(`${API_BASE}/api/v1/agriculture-schools/${qs ? `?${qs}` : ""}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  },

  async stats(): Promise<SchoolsStats> {
    const res = await fetch(`${API_BASE}/api/v1/agriculture-schools/stats`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  },
};
