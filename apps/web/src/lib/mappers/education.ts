import type { Course, AccentColor, LevelKey } from "../../components/education/educationData";

const ACCENTS: AccentColor[] = ["green", "amber", "rose", "blue", "violet", "teal"];

const LEVEL_MAP: Record<string, LevelKey> = {
  beginner: "level_beginner",
  intermediate: "level_intermediate",
  advanced: "level_advanced",
};

const CAT_ICON: Record<string, string> = {
  agriculture: "🌾",
  "water-management": "💧",
  "environmental-science": "🌍",
  economics: "📊",
  technology: "🛰️",
};

export interface ApiCourse {
  id: number | string;
  title: string;
  description?: string | null;
  category?: string;
  level?: string;
  duration_hours?: number;
  instructor?: string | null;
  is_active?: boolean;
  lessons?: unknown[];
  enrollments?: unknown[];
}

export function mapApiCourseToUi(c: ApiCourse, index = 0): Course {
  const levelKey = LEVEL_MAP[(c.level || "beginner").toLowerCase()] || "level_beginner";
  const lessonsCount = Array.isArray(c.lessons) ? c.lessons.length : Math.max(1, Number(c.duration_hours) || 6);
  return {
    id: String(c.id),
    titleKey: `api_${c.id}`,
    titleLiteral: c.title,
    icon: CAT_ICON[c.category || ""] || "📚",
    accent: ACCENTS[index % ACCENTS.length],
    levelKey,
    tagKey: "tag_climate",
    rating: 4.6,
    learners: Array.isArray(c.enrollments) ? c.enrollments.length : 0,
    durationH: Number(c.duration_hours) || 0,
    durationM: 0,
    lessonsCount,
    completedLessons: 0,
    enrolled: false,
  };
}

export function extractCourseList(payload: unknown): ApiCourse[] {
  if (!payload) return [];
  if (Array.isArray(payload)) return payload as ApiCourse[];
  const p = payload as { items?: ApiCourse[]; data?: ApiCourse[] };
  if (Array.isArray(p.items)) return p.items;
  if (Array.isArray(p.data)) return p.data;
  return [];
}
