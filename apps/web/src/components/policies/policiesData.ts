// apps/web/src/components/policies/policiesData.ts
export type PolicyStatus = "active" | "review" | "draft";
export type PolicyCategory =
  | "privacy" | "terms" | "environmental" | "data" | "security" | "sustainability" | "compliance";
export type SortKey = "updated" | "title" | "version";
export type SortDir = "asc" | "desc";

export interface PolicyClause { key: string; }
export interface Policy {
  id: string;
  titleKey: string;
  summaryKey: string;
  category: PolicyCategory;
  version: string;
  updated: string;      // ISO
  status: PolicyStatus;
  clauses: PolicyClause[];
}

const d = (y: number, m: number, day: number) => new Date(y, m - 1, day).toISOString();

export const POLICIES: Policy[] = [
  { id: "pol1", titleKey: "p1_t", summaryKey: "p1_s", category: "privacy", version: "2.1", updated: d(2026, 1, 1), status: "active",
    clauses: [{ key: "p1_c1" }, { key: "p1_c2" }, { key: "p1_c3" }] },
  { id: "pol2", titleKey: "p2_t", summaryKey: "p2_s", category: "terms", version: "1.5", updated: d(2026, 1, 5), status: "active",
    clauses: [{ key: "p2_c1" }, { key: "p2_c2" }, { key: "p2_c3" }] },
  { id: "pol3", titleKey: "p3_t", summaryKey: "p3_s", category: "environmental", version: "3.0", updated: d(2026, 1, 10), status: "active",
    clauses: [{ key: "p3_c1" }, { key: "p3_c2" }, { key: "p3_c3" }] },
  { id: "pol4", titleKey: "p4_t", summaryKey: "p4_s", category: "data", version: "1.2", updated: d(2026, 1, 12), status: "review",
    clauses: [{ key: "p4_c1" }, { key: "p4_c2" }, { key: "p4_c3" }] },
  { id: "pol5", titleKey: "p5_t", summaryKey: "p5_s", category: "security", version: "2.0", updated: d(2025, 11, 20), status: "active",
    clauses: [{ key: "p5_c1" }, { key: "p5_c2" }, { key: "p5_c3" }] },
  { id: "pol6", titleKey: "p6_t", summaryKey: "p6_s", category: "sustainability", version: "1.8", updated: d(2026, 2, 2), status: "review",
    clauses: [{ key: "p6_c1" }, { key: "p6_c2" }, { key: "p6_c3" }] },
  { id: "pol7", titleKey: "p7_t", summaryKey: "p7_s", category: "compliance", version: "1.0", updated: d(2026, 3, 1), status: "draft",
    clauses: [{ key: "p7_c1" }, { key: "p7_c2" }, { key: "p7_c3" }] },
];

export const CATEGORY_ORDER: PolicyCategory[] =
  ["privacy", "terms", "environmental", "data", "security", "sustainability", "compliance"];
export const STATUS_FILTERS: ("all" | PolicyStatus)[] = ["all", "active", "review", "draft"];

// ── helpers ──
export function countByStatus(policies: Policy[], status: PolicyStatus): number {
  return policies.filter((p) => p.status === status).length;
}
export function countByCategory(policies: Policy[], category: PolicyCategory): number {
  return policies.filter((p) => p.category === category).length;
}
export function formatDate(iso: string, locale: string): string {
  return new Date(iso).toLocaleDateString(locale, { year: "numeric", month: "long", day: "numeric" });
}
export function compareVersion(a: string, b: string): number {
  const pa = a.split(".").map(Number), pb = b.split(".").map(Number);
  for (let i = 0; i < Math.max(pa.length, pb.length); i++) {
    const diff = (pa[i] || 0) - (pb[i] || 0);
    if (diff !== 0) return diff;
  }
  return 0;
}

// ── دانلود واقعی (بدون وابستگی) ──
export function downloadText(filename: string, content: string): void {
  const blob = new Blob(["\uFEFF" + content], { type: "text/plain;charset=utf-8;" });
  triggerDownload(filename, blob);
}
export function downloadCSV(filename: string, csv: string): void {
  const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8;" });
  triggerDownload(filename, blob);
}
function triggerDownload(filename: string, blob: Blob): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
export function policiesToCSV(policies: Policy[], resolve: (p: Policy) => string[], headers: string[]): string {
  const rows = policies.map((p) => resolve(p).map((c) => `"${c.replace(/"/g, '""')}"`).join(","));
  return [headers.join(","), ...rows].join("\n");
}