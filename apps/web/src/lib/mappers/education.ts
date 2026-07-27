/** Map education API payloads → UI models. Supports R14 envelope + legacy items. */

export interface UiCourse {
  id: string;
  title: string;
  titleLiteral?: string;
  description?: string;
  category?: string;
  level?: string;
  durationHours?: number;
  instructor?: string;
  isActive?: boolean;
}

interface ApiCourse {
  id: number | string;
  title?: string;
  description?: string | null;
  category?: string;
  level?: string;
  duration_hours?: number;
  instructor?: string | null;
  is_active?: boolean;
}

interface CoursesPayload {
  data?: ApiCourse[];
  items?: ApiCourse[];
  meta?: { total?: number; page?: number; pages?: number; size?: number };
  total?: number;
}

export function mapCourse(raw: ApiCourse): UiCourse {
  const title = raw.title || `Course ${raw.id}`;
  return {
    id: String(raw.id),
    title,
    titleLiteral: title,
    description: raw.description || undefined,
    category: raw.category,
    level: raw.level,
    durationHours: raw.duration_hours,
    instructor: raw.instructor || undefined,
    isActive: raw.is_active,
  };
}

export function mapCoursesResponse(payload: unknown): {
  courses: UiCourse[];
  total: number;
  page: number;
  pages: number;
} {
  const p = (payload || {}) as CoursesPayload;
  const list = p.data || p.items || [];
  const courses = list.map(mapCourse);
  const total = p.meta?.total ?? p.total ?? courses.length;
  const page = p.meta?.page ?? 1;
  const pages = p.meta?.pages ?? 1;
  return { courses, total, page, pages };
}
