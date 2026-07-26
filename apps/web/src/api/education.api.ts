import { apiFetch, v1 } from "./http";
import type { Course, Paginated } from "../types/education";

export const educationApi = {
  listCourses: (params?: { skip?: number; limit?: number; search?: string }) => {
    const q = new URLSearchParams();
    if (params?.skip != null) q.set("skip", String(params.skip));
    if (params?.limit != null) q.set("limit", String(params.limit));
    if (params?.search) q.set("search", params.search);
    const qs = q.toString();
    return apiFetch<Paginated<Course> | Course[]>(
      v1(`/education/courses${qs ? `?${qs}` : ""}`),
    );
  },

  getCourse: (id: number | string) =>
    apiFetch<Course>(v1(`/education/courses/${id}`)),

  stats: () => apiFetch(v1("/education/courses/stats")),
};
