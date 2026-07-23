// apps/web/src/components/pilots/pilotsData.ts
// phase = منبع حقیقت چرخهٔ حیات پایلوت (جایگزین status تک‌مقداری فایل اصلی).
export type PilotPhase = "planning" | "active" | "monitoring" | "completed";
export type SortKey = "progress" | "beneficiaries" | "name";
export type SortDir = "asc" | "desc";

export const PHASE_ORDER: PilotPhase[] = ["planning", "active", "monitoring", "completed"];

// رنگ per-phase (رشته، قابل استفاده در .ts)
export const PHASE_STYLE: Record<PilotPhase, { bar: string; chip: string; text: string; dot: string; grad: string }> = {
  planning:  { bar: "bg-amber-500",  chip: "bg-amber-50 text-amber-700 ring-amber-600/15",  text: "text-amber-700",  dot: "bg-amber-500",  grad: "linear-gradient(135deg,#d97706,#f59e0b)" },
  active:    { bar: "bg-green-600",  chip: "bg-green-50 text-green-700 ring-green-600/15",  text: "text-green-700",  dot: "bg-green-600",  grad: "linear-gradient(135deg,#059669,#10b981)" },
  monitoring:{ bar: "bg-blue-600",   chip: "bg-blue-50 text-blue-700 ring-blue-600/15",     text: "text-blue-700",   dot: "bg-blue-600",   grad: "linear-gradient(135deg,#2563eb,#0ea5e9)" },
  completed: { bar: "bg-violet-600", chip: "bg-violet-50 text-violet-700 ring-violet-600/15",text: "text-violet-700", dot: "bg-violet-600", grad: "linear-gradient(135deg,#7c3aed,#a855f7)" },
};

export interface PilotObjective { key: string; }

export interface Pilot {
  id: string;
  nameKey: string;
  descKey: string;
  goalKey: string;
  locationKey: string;
  phase: PilotPhase;
  progress: number;        // 0..100
  beneficiaries: number;
  teamSize: number;
  budgetUsd: number;
  startDate: string;       // ISO
  image: string;
  objectives: PilotObjective[];
}

const d = (y: number, m: number, day: number) => new Date(y, m - 1, day).toISOString();

export const PILOTS: Pilot[] = [
  { id: "pi1", nameKey: "p1", descKey: "d1", goalKey: "g1", locationKey: "loc_tehran", phase: "active", progress: 75, beneficiaries: 500, teamSize: 8, budgetUsd: 120000, startDate: d(2025, 9, 1), image: "https://images.unsplash.com/photo-1509391366360-2e959784a276?auto=format&fit=crop&w=800&q=80",
    objectives: [{ key: "o_install" }, { key: "o_train" }, { key: "o_grid" }] },
  { id: "pi2", nameKey: "p2", descKey: "d2", goalKey: "g2", locationKey: "loc_mazandaran", phase: "active", progress: 60, beneficiaries: 300, teamSize: 6, budgetUsd: 85000, startDate: d(2025, 10, 12), image: "https://images.unsplash.com/photo-1473773508845-188df298d2d1?auto=format&fit=crop&w=800&q=80",
    objectives: [{ key: "o_sensors" }, { key: "o_irrigation" }] },
  { id: "pi3", nameKey: "p3", descKey: "d3", goalKey: "g3", locationKey: "loc_isfahan", phase: "planning", progress: 20, beneficiaries: 200, teamSize: 4, budgetUsd: 60000, startDate: d(2026, 2, 1), image: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=800&q=80",
    objectives: [{ key: "o_soil" }, { key: "o_crop" }, { key: "o_pilot" }] },
  { id: "pi4", nameKey: "p4", descKey: "d4", goalKey: "g4", locationKey: "loc_khuzestan", phase: "monitoring", progress: 90, beneficiaries: 720, teamSize: 10, budgetUsd: 210000, startDate: d(2025, 4, 5), image: "https://images.unsplash.com/photo-1466611653911-95081537e5b7?auto=format&fit=crop&w=800&q=80",
    objectives: [{ key: "o_ndvi" }, { key: "o_report" }] },
  { id: "pi5", nameKey: "p5", descKey: "d5", goalKey: "g5", locationKey: "loc_gilan", phase: "completed", progress: 100, beneficiaries: 410, teamSize: 7, budgetUsd: 95000, startDate: d(2024, 11, 20), image: "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=800&q=80",
    objectives: [{ key: "o_restore" }, { key: "o_handover" }] },
  { id: "pi6", nameKey: "p6", descKey: "d6", goalKey: "g6", locationKey: "loc_yazd", phase: "planning", progress: 10, beneficiaries: 150, teamSize: 3, budgetUsd: 48000, startDate: d(2026, 3, 15), image: "https://images.unsplash.com/photo-1473448912268-2022ce9509d8?auto=format&fit=crop&w=800&q=80",
    objectives: [{ key: "o_design" }] },
];

export const PHASE_FILTERS: ("all" | PilotPhase)[] = ["all", "planning", "active", "monitoring", "completed"];

// ── helpers ──
export function countByPhase(pilots: Pilot[], phase: PilotPhase): number {
  return pilots.filter((p) => p.phase === phase).length;
}
export function totalBeneficiaries(pilots: Pilot[]): number {
  return pilots.reduce((s, p) => s + p.beneficiaries, 0);
}
export function avgProgress(pilots: Pilot[]): number {
  if (pilots.length === 0) return 0;
  return Math.round(pilots.reduce((s, p) => s + p.progress, 0) / pilots.length);
}
export function formatNumber(n: number, locale: string): string {
  return new Intl.NumberFormat(locale, { maximumFractionDigits: 0 }).format(n);
}
export function formatBudget(usd: number, locale: string): string {
  return new Intl.NumberFormat(locale, { style: "currency", currency: "USD", notation: "compact", maximumFractionDigits: 1 }).format(usd);
}
export function formatDate(iso: string, locale: string): string {
  return new Date(iso).toLocaleDateString(locale, { year: "numeric", month: "long" });
}
export function phaseIndex(phase: PilotPhase): number {
  return PHASE_ORDER.indexOf(phase);
}