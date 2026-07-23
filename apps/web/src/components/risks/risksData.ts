// apps/web/src/components/risks/risksData.ts
// مدل استاندارد مدیریت ریسک: severity(impact) × likelihood → score؛ mitigation و priority جدا.
export type Impact = "high" | "medium" | "low";          // شدت اثر
export type Likelihood = "high" | "medium" | "low";      // احتمال وقوع
export type RiskScore = "critical" | "high" | "medium" | "low";
export type Mitigation = "open" | "in_progress" | "monitored" | "mitigated";
export type Priority = "urgent" | "normal" | "low";
export type SortKey = "score" | "impact" | "priority" | "title";
export type SortDir = "asc" | "desc";

export const IMPACTS: Impact[] = ["high", "medium", "low"];
export const LIKELIHOODS: Likelihood[] = ["low", "medium", "high"]; // چپ→راست
export const MITIGATIONS: Mitigation[] = ["open", "in_progress", "monitored", "mitigated"];

// ماتریس استاندارد: impact × likelihood → score
export const SCORE_MATRIX: Record<Impact, Record<Likelihood, RiskScore>> = {
  high:   { high: "critical", medium: "high",  low: "medium" },
  medium: { high: "high",     medium: "medium", low: "low" },
  low:    { high: "medium",   medium: "low",   low: "low" },
};
// وزن عددی برای sort و رنگ
export const SCORE_NUM: Record<RiskScore, number> = { critical: 9, high: 6, medium: 3, low: 1 };
export const IMPACT_NUM: Record<Impact, number> = { high: 3, medium: 2, low: 1 };
export const PRIORITY_NUM: Record<Priority, number> = { urgent: 3, normal: 2, low: 1 };

export const SCORE_STYLE: Record<RiskScore, { chip: string; cell: string; text: string }> = {
  critical: { chip: "bg-red-100 text-red-800 ring-red-600/20",     cell: "bg-red-600 text-white",     text: "text-red-700" },
  high:     { chip: "bg-orange-100 text-orange-800 ring-orange-600/20", cell: "bg-orange-500 text-white", text: "text-orange-700" },
  medium:   { chip: "bg-amber-100 text-amber-800 ring-amber-600/20", cell: "bg-amber-400 text-stone-900", text: "text-amber-700" },
  low:      { chip: "bg-green-100 text-green-800 ring-green-600/20", cell: "bg-green-500 text-white",   text: "text-green-700" },
};
export const MITIGATION_STYLE: Record<Mitigation, string> = {
  open: "bg-red-50 text-red-700 ring-red-600/15",
  in_progress: "bg-amber-50 text-amber-700 ring-amber-600/15",
  monitored: "bg-blue-50 text-blue-700 ring-blue-600/15",
  mitigated: "bg-green-50 text-green-700 ring-green-600/15",
};
export const PRIORITY_STYLE: Record<Priority, string> = {
  urgent: "bg-red-50 text-red-700 ring-red-600/15",
  normal: "bg-amber-50 text-amber-700 ring-amber-600/15",
  low: "bg-stone-100 text-stone-600 ring-stone-600/15",
};

export interface Risk {
  id: string;
  titleKey: string;
  descKey: string;
  owner: string;          // اسم خاص (مثل نام افراد در Community) — ترجمه نمی‌شود
  impact: Impact;
  likelihood: Likelihood;
  mitigation: Mitigation;
  priority: Priority;
  due: string;            // ISO
}

export const scoreOf = (r: Risk): RiskScore => SCORE_MATRIX[r.impact][r.likelihood];
export const isOpen = (r: Risk): boolean => r.mitigation !== "mitigated";

const d = (y: number, m: number, day: number) => new Date(y, m - 1, day).toISOString();

export const INITIAL_RISKS: Risk[] = [
  { id: "rk1", titleKey: "t1", descKey: "d1", owner: "A. Karimi", impact: "high", likelihood: "high", mitigation: "in_progress", priority: "urgent", due: d(2026, 8, 1) },
  { id: "rk2", titleKey: "t2", descKey: "d2", owner: "S. Ahmadi", impact: "medium", likelihood: "medium", mitigation: "monitored", priority: "normal", due: d(2026, 9, 15) },
  { id: "rk3", titleKey: "t3", descKey: "d3", owner: "R. Nazari", impact: "low", likelihood: "low", mitigation: "mitigated", priority: "low", due: d(2026, 6, 10) },
  { id: "rk4", titleKey: "t4", descKey: "d4", owner: "M. Hosseini", impact: "high", likelihood: "medium", mitigation: "open", priority: "urgent", due: d(2026, 7, 28) },
  { id: "rk5", titleKey: "t5", descKey: "d5", owner: "H. Rezaei", impact: "medium", likelihood: "high", mitigation: "in_progress", priority: "normal", due: d(2026, 8, 20) },
  { id: "rk6", titleKey: "t6", descKey: "d6", owner: "L. Tehrani", impact: "low", likelihood: "medium", mitigation: "mitigated", priority: "low", due: d(2026, 5, 30) },
  { id: "rk7", titleKey: "t7", descKey: "d7", owner: "O. Yazdi", impact: "high", likelihood: "low", mitigation: "monitored", priority: "normal", due: d(2026, 10, 5) },
];

// ── KPI derived ──
export function countOpen(risks: Risk[]): number { return risks.filter(isOpen).length; }
export function countMitigated(risks: Risk[]): number { return risks.filter((r) => r.mitigation === "mitigated").length; }
export function countHighCritical(risks: Risk[]): number {
  return risks.filter((r) => isOpen(r) && (scoreOf(r) === "high" || scoreOf(r) === "critical")).length;
}
// شمارش per-cell برای ماتریس (فقط open)
export function matrixCounts(risks: Risk[]): Record<string, number> {
  const c: Record<string, number> = {};
  for (const r of risks) if (isOpen(r)) c[`${r.impact}|${r.likelihood}`] = (c[`${r.impact}|${r.likelihood}`] || 0) + 1;
  return c;
}
export function formatDate(iso: string, locale: string): string {
  return new Date(iso).toLocaleDateString(locale, { year: "numeric", month: "short", day: "numeric" });
}
export function downloadCSV(filename: string, csv: string): void {
  const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = filename;
  document.body.appendChild(a); a.click(); document.body.removeChild(a);
  URL.revokeObjectURL(url);
}