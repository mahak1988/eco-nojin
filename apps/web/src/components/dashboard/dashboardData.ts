// apps/web/src/components/dashboard/dashboardData.ts
// دادهٔ داشبورد — بعداً با API جایگزین می‌شود.
import type { DonutSegment } from "../charts/DonutChart";

export type KpiColor = "green" | "blue" | "amber" | "violet";
export type ActivityKind = "user" | "project" | "payment" | "alert" | "report";

export interface Kpi {
  key: string;
  value: number;
  prefix?: string;
  suffix?: string;
  decimals?: number;
  trend: number;
  color: KpiColor;
}

export interface Activity {
  id: string;
  kind: ActivityKind;
  titleKey: string;
  timestamp: string; // ISO
}

const hoursAgo = (h: number) => new Date(Date.now() - h * 3_600_000).toISOString();
const minsAgo = (m: number) => new Date(Date.now() - m * 60_000).toISOString();

export const KPIS: Kpi[] = [
  { key: "totalUsers", value: 4256, trend: 12.4, color: "green" },
  { key: "activeUsers", value: 3456, trend: 8.1, color: "blue" },
  { key: "totalProjects", value: 124, trend: 5.6, color: "amber" },
  { key: "revenue", value: 48.5, prefix: "$", suffix: "K", decimals: 1, trend: 15.3, color: "violet" },
];

// روند کاربران فعال ۷ روز اخیر (برای LineChart)
export const ACTIVE_USERS_SERIES = [2980, 3120, 3050, 3240, 3380, 3410, 3456];

// توزیع کاربران بر اساس نقش (برای DonutChart)
export const USER_ROLES: DonutSegment[] = [
  { value: 42, color: "#15803d" }, // farmer
  { value: 26, color: "#1d4ed8" }, // expert
  { value: 18, color: "#d97706" }, // researcher
  { value: 14, color: "#7c3aed" }, // student
];

export const RECENT_ACTIVITY: Activity[] = [
  { id: "a1", kind: "user", titleKey: "act1", timestamp: minsAgo(12) },
  { id: "a2", kind: "project", titleKey: "act2", timestamp: minsAgo(48) },
  { id: "a3", kind: "payment", titleKey: "act3", timestamp: hoursAgo(2) },
  { id: "a4", kind: "alert", titleKey: "act4", timestamp: hoursAgo(5) },
  { id: "a5", kind: "report", titleKey: "act5", timestamp: hoursAgo(9) },
  { id: "a6", kind: "user", titleKey: "act6", timestamp: hoursAgo(14) },
];