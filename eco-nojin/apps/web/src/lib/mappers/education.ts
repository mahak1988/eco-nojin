/** Map education API → UI Course model. Supports R14 data/meta + legacy items. */

import type { AccentColor, Course, LevelKey } from "../../components/education/educationData";

const ACCENTS: AccentColor[] = ["green", "amber", "blue", "violet", "teal", "rose"];
const ICONS = ["🌍", "🌾", "💧", "🛰️", "☀️", "🦋", "📚", "🌱"];

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
  lessonsCount?: number;
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
  lessons?: unknown[];
  enrollments?: unknown[];
}

interface CoursesPayload {
  data?: ApiCourse[];
  items?: ApiCourse[];
  meta?: { total?: number; page?: number; pages?: number; size?: number };
  total?: number;
}

function levelToKey(level?: string): LevelKey {
  const l = (level || "").toLowerCase();
  if (l.includes("adv") || l === "advanced") return "level_advanced";
  if (l.includes("inter") || l === "intermediate") return "level_intermediate";
  return "level_beginner";
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
    lessonsCount: Array.isArray(raw.lessons) ? raw.lessons.length : undefined,
  };
}

/** Full UI Course for CourseCard */
export function mapApiCourseToUi(raw: ApiCourse, index = 0): Course {
  const hours = Number(raw.duration_hours) || 0;
  const lessons =
    Array.isArray(raw.lessons) && raw.lessons.length > 0
      ? raw.lessons.length
      : Math.max(3, Math.round(hours) || 3);
  const title = raw.title || `Course ${raw.id}`;
  return {
    id: String(raw.id),
    titleKey: "",
    titleLiteral: title,
    icon: ICONS[index % ICONS.length],
    accent: ACCENTS[index % ACCENTS.length],
    levelKey: levelToKey(raw.level),
    tagKey: raw.category || "tag_climate",
    rating: 4.5 + (index % 5) * 0.1,
    learners: Array.isArray(raw.enrollments) ? raw.enrollments.length : 0,
    durationH: Math.floor(hours),
    durationM: Math.round((hours % 1) * 60),
    lessonsCount: lessons,
    completedLessons: 0,
    enrolled: false,
  };
}

export function extractCourseList(payload: unknown): ApiCourse[] {
  const p = (payload || {}) as CoursesPayload;
  if (Array.isArray(p.data)) return p.data;
  if (Array.isArray(p.items)) return p.items;
  if (Array.isArray(payload)) return payload as ApiCourse[];
  return [];
}

export function mapCoursesResponse(payload: unknown): {
  courses: Course[];
  total: number;
  page: number;
  pages: number;
} {
  const p = (payload || {}) as CoursesPayload;
  const list = extractCourseList(payload);
  const courses = list.map((c, i) => mapApiCourseToUi(c, i));
  const total = p.meta?.total ?? p.total ?? courses.length;
  const page = p.meta?.page ?? 1;
  const pages = p.meta?.pages ?? 1;
  return { courses, total, page, pages };
}
