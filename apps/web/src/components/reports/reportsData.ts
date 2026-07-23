// apps/web/src/components/reports/reportsData.ts
export type ReportType = "financial" | "impact" | "mrv" | "analytics";
export type ReportStatus = "published" | "draft" | "generating";
export type ReportPeriod = "last_7d" | "last_30d" | "last_90d" | "last_year";
export type SortKey = "date" | "name" | "downloads";
export type SortDir = "asc" | "desc";
export type UnitKey = "unit_usd" | "unit_t" | "unit_pct" | "unit_count";

export interface ReportMetric { labelKey: string; value: number; unitKey: UnitKey; }
export interface ReportTemplate { summaryKey: string; metrics: ReportMetric[]; }

export interface Report {
  id: string;
  nameKey?: string;        // seed: ترجمه‌شده؛ generate: undefined → نام از type+period ساخته می‌شود
  type: ReportType;
  period: ReportPeriod;
  status: ReportStatus;
  date: string;            // ISO
  downloads: number;
}

const d = (y: number, m: number, day: number) => new Date(y, m - 1, day).toISOString();

// منبع حقیقت محتوا — seed و generate و preview و download همه از اینجا می‌خوانند
export const REPORT_TEMPLATE: Record<ReportType, ReportTemplate> = {
  financial: {
    summaryKey: "sum_financial",
    metrics: [
      { labelKey: "m_revenue", value: 482000, unitKey: "unit_usd" },
      { labelKey: "m_expenses", value: 311000, unitKey: "unit_usd" },
      { labelKey: "m_net", value: 171000, unitKey: "unit_usd" },
    ],
  },
  impact: {
    summaryKey: "sum_impact",
    metrics: [
      { labelKey: "m_carbon", value: 4820, unitKey: "unit_t" },
      { labelKey: "m_beneficiaries", value: 12500, unitKey: "unit_count" },
      { labelKey: "m_projects", value: 24, unitKey: "unit_count" },
    ],
  },
  mrv: {
    summaryKey: "sum_mrv",
    metrics: [
      { labelKey: "m_verified", value: 3120, unitKey: "unit_t" },
      { labelKey: "m_pending", value: 640, unitKey: "unit_t" },
      { labelKey: "m_compliance", value: 92, unitKey: "unit_pct" },
    ],
  },
  analytics: {
    summaryKey: "sum_analytics",
    metrics: [
      { labelKey: "m_users", value: 3456, unitKey: "unit_count" },
      { labelKey: "m_sessions", value: 18200, unitKey: "unit_count" },
      { labelKey: "m_engagement", value: 68, unitKey: "unit_pct" },
    ],
  },
};

export const REPORT_TYPES: ReportType[] = ["financial", "impact", "mrv", "analytics"];
export const REPORT_PERIODS: ReportPeriod[] = ["last_7d", "last_30d", "last_90d", "last_year"];
export const TYPE_FILTERS: ("all" | ReportType)[] = ["all", "financial", "impact", "mrv", "analytics"];
export const STATUS_FILTERS: ("all" | ReportStatus)[] = ["all", "published", "draft", "generating"];

export const INITIAL_REPORTS: Report[] = [
  { id: "rp1", nameKey: "r1", type: "financial", period: "last_year", status: "published", date: d(2026, 1, 5), downloads: 64 },
  { id: "rp2", nameKey: "r2", type: "impact", period: "last_90d", status: "draft", date: d(2026, 1, 10), downloads: 0 },
  { id: "rp3", nameKey: "r3", type: "mrv", period: "last_90d", status: "published", date: d(2026, 1, 12), downloads: 41 },
  { id: "rp4", nameKey: "r4", type: "analytics", period: "last_30d", status: "published", date: d(2026, 1, 14), downloads: 51 },
  { id: "rp5", nameKey: "r5", type: "financial", period: "last_30d", status: "published", date: d(2025, 12, 20), downloads: 28 },
  { id: "rp6", nameKey: "r6", type: "impact", period: "last_year", status: "published", date: d(2025, 11, 30), downloads: 19 },
];

// ── helpers ──
export function countByStatus(reports: Report[], status: ReportStatus): number {
  return reports.filter((r) => r.status === status).length;
}
export function sumDownloads(reports: Report[]): number {
  return reports.reduce((s, r) => s + r.downloads, 0);
}
export function formatDate(iso: string, locale: string): string {
  return new Date(iso).toLocaleDateString(locale, { year: "numeric", month: "long", day: "numeric" });
}
export function formatNumber(n: number, locale: string): string {
  return new Intl.NumberFormat(locale, { maximumFractionDigits: 0 }).format(n);
}

// ── خروجی‌های robust (درس Vite: بدون وابستگی به chunk/شبکه) ──
export function downloadText(filename: string, content: string): void {
  const blob = new Blob(["\uFEFF" + content], { type: "text/plain;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = filename;
  document.body.appendChild(a); a.click(); document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
// clipboard با fallback execCommand (robust وقتی navigator.clipboard در دسترس نیست)
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch { /* fall through to legacy */ }
  try {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    const ok = document.execCommand("copy");
    document.body.removeChild(ta);
    return ok;
  } catch {
    return false;
  }
}
export function reportShareLink(id: string): string {
  const base = typeof window !== "undefined" ? window.location.origin : "";
  return `${base}/reports/${id}`;
}