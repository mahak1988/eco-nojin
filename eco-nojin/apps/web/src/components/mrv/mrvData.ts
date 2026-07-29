// apps/web/src/components/mrv/mrvData.ts
// MRV = Monitoring, Reporting, Verification. واحد استاندارد = tCO₂e (تن معادل CO₂).
export type MrvStatus = "verified" | "pending" | "rejected";
export type SortKey = "date" | "carbon";
export type SortDir = "asc" | "desc";

export interface MrvReport {
  id: string;
  projectKey: string;     // کلید نام پروژه در i18n
  status: MrvStatus;
  date: string;           // ISO
  carbon: number;         // تن CO₂e — فقط verifiedها در offset کل شمرده می‌شوند
  methodology: string;    // کلید متدولوژی
}

export interface Safeguard {
  id: string;
  nameKey: string;
  descKey: string;
  passed: boolean;
}

const daysAgo = (d: number) => new Date(Date.now() - d * 86_400_000).toISOString();

export const INITIAL_REPORTS: MrvReport[] = [
  { id: "m1", projectKey: "p1", status: "verified", date: daysAgo(2),  carbon: 1250, methodology: "meth_vcs" },
  { id: "m2", projectKey: "p2", status: "pending",  date: daysAgo(1),  carbon: 890,  methodology: "meth_gs" },
  { id: "m3", projectKey: "p3", status: "rejected", date: daysAgo(5),  carbon: 0,    methodology: "meth_vcs" },
  { id: "m4", projectKey: "p4", status: "verified", date: daysAgo(8),  carbon: 2100, methodology: "meth_gold" },
  { id: "m5", projectKey: "p5", status: "pending",  date: daysAgo(3),  carbon: 640,  methodology: "meth_gs" },
  { id: "m6", projectKey: "p6", status: "verified", date: daysAgo(12), carbon: 1470, methodology: "meth_vcs" },
];

// چک‌لیست انطباق safeguard (اصل «additionality/permanence/...» در استانداردهای کربن)
export const INITIAL_SAFEGUARDS: Safeguard[] = [
  { id: "s1", nameKey: "sg1_n", descKey: "sg1_d", passed: true },
  { id: "s2", nameKey: "sg2_n", descKey: "sg2_d", passed: true },
  { id: "s3", nameKey: "sg3_n", descKey: "sg3_d", passed: false },
  { id: "s4", nameKey: "sg4_n", descKey: "sg4_d", passed: true },
  { id: "s5", nameKey: "sg5_n", descKey: "sg5_d", passed: false },
];

export const STATUS_FILTERS: ("all" | MrvStatus)[] = ["all", "verified", "pending", "rejected"];

// ── helpers ──
export function countByStatus(reports: MrvReport[], status: MrvStatus): number {
  return reports.filter((r) => r.status === status).length;
}
// فقط verifiedها در offset کل معتبرند (منطق MRV)
export function totalVerifiedOffset(reports: MrvReport[]): number {
  return reports.filter((r) => r.status === "verified").reduce((s, r) => s + r.carbon, 0);
}
export function complianceRate(safeguards: Safeguard[]): number {
  if (safeguards.length === 0) return 0;
  return Math.round((safeguards.filter((s) => s.passed).length / safeguards.length) * 100);
}
export function formatCarbon(t: number, locale: string): string {
  return new Intl.NumberFormat(locale, { maximumFractionDigits: 0 }).format(t);
}
export function formatDate(iso: string, locale: string): string {
  return new Date(iso).toLocaleDateString(locale, { year: "numeric", month: "short", day: "numeric" });
}

// ── CSV (BOM برای Excel فارسی/عربی) ──
export function mrvToCSV(reports: MrvReport[], resolve: (r: MrvReport) => string[], headers: string[]): string {
  const rows = reports.map((r) => resolve(r).map((c) => `"${c.replace(/"/g, '""')}"`).join(","));
  return [headers.join(","), ...rows].join("\n");
}
export function downloadCSV(filename: string, csv: string): void {
  const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}