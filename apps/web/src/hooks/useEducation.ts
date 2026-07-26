import { useQuery } from "@tanstack/react-query";
import { educationApi } from "../api/education.api";
import type { Course, Paginated } from "../types/education";

function normalizeCourses(data: Paginated<Course> | Course[] | null | undefined): Course[] {
  if (!data) return [];
  if (Array.isArray(data)) return data;
  if (Array.isArray(data.items)) return data.items;
  return [];
}

export function useCourses(limit = 50) {
  return useQuery({
    queryKey: ["education", "courses", limit],
    queryFn: async () => {
      try {
        const data = await educationApi.listCourses({ limit });
        return { items: normalizeCourses(data), source: "api" as const };
      } catch {
        return { items: [] as Course[], source: "mock" as const };
      }
    },
  });
}
