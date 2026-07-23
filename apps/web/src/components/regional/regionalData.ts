// apps/web/src/components/regional/regionalData.ts
export type RegionStatus = "active" | "planning";

export interface RegionHighlight { key: string; }
export interface Region {
  id: string;
  nameKey: string;
  code: string;          // مخفف کشور (AF/IQ/JO) — cross-platform، برخلاف پرچم emoji که در ویندوز render نمی‌شود
  status: RegionStatus;
  progress: number;      // 0..100
  projects: number;
  programs: number;
  beneficiaries: number;
  carbonT: number;       // تن CO₂e
  since: string;         // سال شروع
  highlights: RegionHighlight[];
}

export const REGIONS: Region[] = [
  { id: "afghanistan", nameKey: "r_af", code: "AF", status: "active", progress: 75, projects: 12, programs: 24, beneficiaries: 12500, carbonT: 4820, since: "2023",
    highlights: [{ key: "h_af1" }, { key: "h_af2" }, { key: "h_af3" }] },
  { id: "iraq", nameKey: "r_iq", code: "IQ", status: "active", progress: 60, projects: 8, programs: 15, beneficiaries: 8200, carbonT: 2100, since: "2024",
    highlights: [{ key: "h_iq1" }, { key: "h_iq2" }, { key: "h_iq3" }] },
  { id: "jordan", nameKey: "r_jo", code: "JO", status: "planning", progress: 30, projects: 5, programs: 8, beneficiaries: 3100, carbonT: 0, since: "2026",
    highlights: [{ key: "h_jo1" }, { key: "h_jo2" }, { key: "h_jo3" }] },
  { id: "mena", nameKey: "r_mena", code: "MN", status: "active", progress: 85, projects: 15, programs: 40, beneficiaries: 45000, carbonT: 15200, since: "2022",
    highlights: [{ key: "h_mn1" }, { key: "h_mn2" }, { key: "h_mn3" }] },
];

// ── helpers (KPI سراسری derived) ──
export function sumProjects(regions: Region[]): number {
  return regions.reduce((s, r) => s + r.projects, 0);
}
export function sumBeneficiaries(regions: Region[]): number {
  return regions.reduce((s, r) => s + r.beneficiaries, 0);
}
export function sumCarbon(regions: Region[]): number {
  return regions.reduce((s, r) => s + r.carbonT, 0);
}
export function countActive(regions: Region[]): number {
  return regions.filter((r) => r.status === "active").length;
}
export function formatNumber(n: number, locale: string): string {
  return new Intl.NumberFormat(locale, { maximumFractionDigits: 0 }).format(n);
}