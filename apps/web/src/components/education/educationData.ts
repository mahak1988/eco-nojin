// apps/web/src/components/education/educationData.ts
export type LevelKey = "level_beginner" | "level_intermediate" | "level_advanced";
export type CertStatusKey = "cert_verified" | "cert_pending" | "cert_progress";
export type AccentColor = "green" | "blue" | "amber" | "violet" | "rose" | "teal";

export interface Course {
  id: string;
  titleKey: string;
  icon: string;          // emoji
  accent: AccentColor;
  levelKey: LevelKey;
  tagKey: string;
  rating: number;        // 0..5
  learners: number;
  durationH: number;
  durationM: number;
  lessonsCount: number;
  completedLessons: number;
  enrolled: boolean;
}

export interface PathStep {
  id: string;
  titleKey: string;
  done: boolean;
}
export interface LearningPathData {
  id: string;
  titleKey: string;
  descKey: string;
  icon: string;
  accent: AccentColor;
  steps: PathStep[];
}

export interface Certification {
  id: string;
  nameKey: string;
  date: string;          // ISO
  statusKey: CertStatusKey;
  icon: string;
}

// دانشجویان فعال سراسری (مفهوم global — mock)
export const GLOBAL_LEARNERS = 1240;

export const INITIAL_COURSES: Course[] = [
  { id: "co1", titleKey: "co1_t", icon: "🌍", accent: "green",  levelKey: "level_beginner",     tagKey: "tag_climate",  rating: 4.8, learners: 820,  durationH: 4, durationM: 30, lessonsCount: 12, completedLessons: 0, enrolled: false },
  { id: "co2", titleKey: "co2_t", icon: "🌾", accent: "amber",  levelKey: "level_intermediate", tagKey: "tag_farming",  rating: 4.9, learners: 540,  durationH: 6, durationM: 45, lessonsCount: 18, completedLessons: 7, enrolled: true },
  { id: "co3", titleKey: "co3_t", icon: "☀️", accent: "rose",   levelKey: "level_advanced",     tagKey: "tag_energy",   rating: 4.7, learners: 310,  durationH: 8, durationM: 15, lessonsCount: 24, completedLessons: 0, enrolled: false },
  { id: "co4", titleKey: "co4_t", icon: "💧", accent: "blue",   levelKey: "level_intermediate", tagKey: "tag_water",    rating: 4.6, learners: 430,  durationH: 5, durationM: 10, lessonsCount: 15, completedLessons: 15, enrolled: true },
  { id: "co5", titleKey: "co5_t", icon: "🛰️", accent: "violet", levelKey: "level_advanced",     tagKey: "tag_satellite",rating: 4.9, learners: 260,  durationH: 7, durationM: 0,  lessonsCount: 20, completedLessons: 0, enrolled: false },
  { id: "co6", titleKey: "co6_t", icon: "🦋", accent: "teal",   levelKey: "level_beginner",     tagKey: "tag_bio",      rating: 4.5, learners: 390,  durationH: 3, durationM: 50, lessonsCount: 10, completedLessons: 0, enrolled: false },
];

export const INITIAL_PATHS: LearningPathData[] = [
  {
    id: "pa1", titleKey: "pa1_t", descKey: "pa1_d", icon: "🎓", accent: "green",
    steps: [
      { id: "s1", titleKey: "pa1_s1", done: true },
      { id: "s2", titleKey: "pa1_s2", done: true },
      { id: "s3", titleKey: "pa1_s3", done: false },
      { id: "s4", titleKey: "pa1_s4", done: false },
    ],
  },
  {
    id: "pa2", titleKey: "pa2_t", descKey: "pa2_d", icon: "🔬", accent: "violet",
    steps: [
      { id: "s1", titleKey: "pa2_s1", done: true },
      { id: "s2", titleKey: "pa2_s2", done: false },
      { id: "s3", titleKey: "pa2_s3", done: false },
    ],
  },
];

export const CERTIFICATIONS: Certification[] = [
  { id: "ce1", nameKey: "ce1_n", date: "2024-01-10", statusKey: "cert_verified", icon: "🛡️" },
  { id: "ce2", nameKey: "ce2_n", date: "2024-01-05", statusKey: "cert_pending", icon: "🌱" },
  { id: "ce3", nameKey: "ce3_n", date: "2026-07-21", statusKey: "cert_progress", icon: "🗺️" },
];