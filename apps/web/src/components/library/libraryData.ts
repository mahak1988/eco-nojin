// apps/web/src/components/library/libraryData.ts
export type ResourceType = "pdf" | "video" | "audio" | "doc";
export type CategoryKey =
  | "cat_training" | "cat_documentation" | "cat_video" | "cat_podcast" | "cat_guide" | "cat_report";
export type SortKey = "popular" | "title" | "newest";

export interface Resource {
  id: string;
  titleKey: string;
  summaryKey: string;   // محتوای mock دانلود + توضیح کارت
  type: ResourceType;
  category: CategoryKey;
  downloads: number;
  sizeKb: number;
  updated: string;      // ISO
}

const daysAgo = (d: number) => new Date(Date.now() - d * 86_400_000).toISOString();

export const RESOURCES: Resource[] = [
  { id: "r1", titleKey: "t1", summaryKey: "sum1", type: "pdf",   category: "cat_training",      downloads: 1234, sizeKb: 2450, updated: daysAgo(3) },
  { id: "r2", titleKey: "t2", summaryKey: "sum2", type: "doc",   category: "cat_documentation", downloads: 856,  sizeKb: 1180, updated: daysAgo(8) },
  { id: "r3", titleKey: "t3", summaryKey: "sum3", type: "video", category: "cat_video",         downloads: 2341, sizeKb: 48200, updated: daysAgo(1) },
  { id: "r4", titleKey: "t4", summaryKey: "sum4", type: "audio", category: "cat_podcast",       downloads: 567,  sizeKb: 15600, updated: daysAgo(5) },
  { id: "r5", titleKey: "t5", summaryKey: "sum5", type: "pdf",   category: "cat_guide",         downloads: 1780, sizeKb: 3320, updated: daysAgo(12) },
  { id: "r6", titleKey: "t6", summaryKey: "sum6", type: "video", category: "cat_training",      downloads: 940,  sizeKb: 36800, updated: daysAgo(2) },
  { id: "r7", titleKey: "t7", summaryKey: "sum7", type: "doc",   category: "cat_report",        downloads: 412,  sizeKb: 920,  updated: daysAgo(20) },
  { id: "r8", titleKey: "t8", summaryKey: "sum8", type: "audio", category: "cat_podcast",       downloads: 688,  sizeKb: 12400, updated: daysAgo(6) },
];

export const TYPE_FILTERS: ("all" | ResourceType)[] = ["all", "pdf", "video", "audio", "doc"];

// ── helpers ──
export function countByType(resources: Resource[], type?: ResourceType): number {
  return resources.filter((r) => (type ? r.type === type : true)).length;
}
export function formatSize(kb: number, locale: string): string {
  if (kb >= 1024) return `${(kb / 1024).toLocaleString(locale, { maximumFractionDigits: 1 })} MB`;
  return `${kb.toLocaleString(locale)} KB`;
}
export function formatDate(iso: string, locale: string): string {
  return new Date(iso).toLocaleDateString(locale, { year: "numeric", month: "short", day: "numeric" });
}

// ── دانلود واقعی (بدون کتابخانهٔ ZIP) ──
function triggerDownload(filename: string, content: string, mime: string, bom = false): void {
  const blob = new Blob([(bom ? "\uFEFF" : "") + content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// دانلود یک منبع → فایل متنی چندزبانه با metadata + خلاصه
export function downloadResource(
  r: Resource, title: string, summary: string, metaLines: string[], ext: string
): void {
  const body = [title, "=".repeat(title.length), "", summary, "", ...metaLines, ""].join("\n");
  triggerDownload(`${r.id}-${title.replace(/[^\p{L}\p{N}]+/gu, "_")}.${ext}`, body, "text/plain;charset=utf-8;");
}

// Download All → manifest CSV (BOM برای Excel فارسی/عربی)
export function downloadManifest(resources: Resource[], headers: string[], rows: string[][]): void {
  const csv = [headers.join(","), ...rows.map((row) => row.map((c) => `"${c.replace(/"/g, '""')}"`).join(","))].join("\n");
  triggerDownload("knowledge-hub-manifest.csv", csv, "text/csv;charset=utf-8;", true);
}

export function extForType(type: ResourceType): string {
  return type === "video" ? "txt" : type === "audio" ? "txt" : type === "pdf" ? "txt" : "txt";
  // محتوای واقعی فایل‌ها در دسترس نیست؛ همه به‌صورت .txt توضیحی دانلود می‌شوند.
}