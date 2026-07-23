// apps/web/src/components/tourism/tourismData.ts
export type Conservation = "high" | "medium" | "low";
export type Accessibility = "access_easy" | "access_moderate" | "access_hard";
export type SeasonKey = "season_spring" | "season_summer" | "season_autumn" | "season_winter";
export type AmenityKey =
  | "amenity_guide" | "amenity_camping" | "amenity_trail" | "amenity_photo"
  | "amenity_wildlife" | "amenity_water" | "amenity_shelter" | "amenity_permit";
export type SortKey = "rating" | "visitors" | "name";
export type SortDir = "asc" | "desc";

export interface Destination {
  id: string;
  nameKey: string;
  regionKey: string;
  descKey: string;
  rating: number;        // 0..5
  visitors: number;
  conservation: Conservation;
  conservationScore: number; // 0..100
  accessibility: Accessibility;
  seasons: SeasonKey[];
  amenities: AmenityKey[];
  image: string;
  accent: string;        // gradient fallback
  pos: { x: number; y: number }; // درصد روی نقشهٔ CSS
  openKey: string;
}

export const IMAGES = [
  "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=80",
  "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
  "https://images.unsplash.com/photo-1509316785289-025f5b846b35?auto=format&fit=crop&w=1200&q=80",
  "https://images.unsplash.com/photo-1454496522488-7a8e488e8606?auto=format&fit=crop&w=1200&q=80",
  "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1200&q=80",
  "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=1200&q=80",
];

export const DESTINATIONS: Destination[] = [
  { id: "d1", nameKey: "n1", regionKey: "r_tehran", descKey: "x1", rating: 4.8, visitors: 1200, conservation: "high", conservationScore: 88, accessibility: "access_moderate",
    seasons: ["season_spring", "season_autumn"], amenities: ["amenity_guide", "amenity_trail", "amenity_photo", "amenity_wildlife"],
    image: IMAGES[0], accent: "linear-gradient(135deg,#065f46,#059669 55%,#34d399)", pos: { x: 52, y: 38 }, openKey: "open_all" },
  { id: "d2", nameKey: "n2", regionKey: "r_mazandaran", descKey: "x2", rating: 4.6, visitors: 850, conservation: "medium", conservationScore: 71, accessibility: "access_easy",
    seasons: ["season_spring", "season_summer"], amenities: ["amenity_trail", "amenity_camping", "amenity_water", "amenity_photo"],
    image: IMAGES[1], accent: "linear-gradient(135deg,#0c4a6e,#0284c7 55%,#38bdf8)", pos: { x: 55, y: 30 }, openKey: "open_all" },
  { id: "d3", nameKey: "n3", regionKey: "r_kerman", descKey: "x3", rating: 4.9, visitors: 650, conservation: "high", conservationScore: 92, accessibility: "access_hard",
    seasons: ["season_autumn", "season_winter"], amenities: ["amenity_guide", "amenity_camping", "amenity_photo", "amenity_permit"],
    image: IMAGES[2], accent: "linear-gradient(135deg,#7c2d12,#c2410c 55%,#f59e0b)", pos: { x: 65, y: 60 }, openKey: "open_seasonal" },
  { id: "d4", nameKey: "n4", regionKey: "r_zagros", descKey: "x4", rating: 4.7, visitors: 540, conservation: "high", conservationScore: 85, accessibility: "access_hard",
    seasons: ["season_spring", "season_summer"], amenities: ["amenity_guide", "amenity_trail", "amenity_wildlife", "amenity_shelter"],
    image: IMAGES[3], accent: "linear-gradient(135deg,#1e3a8a,#2563eb 55%,#60a5fa)", pos: { x: 38, y: 35 }, openKey: "open_seasonal" },
  { id: "d5", nameKey: "n5", regionKey: "r_gulf", descKey: "x5", rating: 4.5, visitors: 720, conservation: "medium", conservationScore: 68, accessibility: "access_moderate",
    seasons: ["season_autumn", "season_winter"], amenities: ["amenity_guide", "amenity_wildlife", "amenity_photo", "amenity_permit"],
    image: IMAGES[4], accent: "linear-gradient(135deg,#155e75,#0891b2 55%,#22d3ee)", pos: { x: 42, y: 72 }, openKey: "open_seasonal" },
  { id: "d6", nameKey: "n6", regionKey: "r_gilan", descKey: "x6", rating: 4.8, visitors: 980, conservation: "high", conservationScore: 90, accessibility: "access_moderate",
    seasons: ["season_spring", "season_autumn"], amenities: ["amenity_trail", "amenity_camping", "amenity_wildlife", "amenity_water"],
    image: IMAGES[5], accent: "linear-gradient(135deg,#14532d,#16a34a 55%,#4ade80)", pos: { x: 45, y: 28 }, openKey: "open_all" },
];

export const REGIONS = Array.from(new Set(DESTINATIONS.map((d) => d.regionKey)));

export const CONSERVATION_STYLE: Record<Conservation, { chip: string; bar: string; text: string }> = {
  high: { chip: "bg-green-50 text-green-700 ring-green-600/15", bar: "bg-green-600", text: "text-green-700" },
  medium: { chip: "bg-amber-50 text-amber-700 ring-amber-600/15", bar: "bg-amber-500", text: "text-amber-700" },
  low: { chip: "bg-red-50 text-red-700 ring-red-600/15", bar: "bg-red-500", text: "text-red-700" },
};

// ── KPI derived ──
export const mean = (xs: number[]): number => (xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : 0);
export const avgRating = (d: Destination[]): number => mean(d.map((x) => x.rating));
export const totalVisitors = (d: Destination[]): number => d.reduce((s, x) => s + x.visitors, 0);
export const avgConservation = (d: Destination[]): number => Math.round(mean(d.map((x) => x.conservationScore)));

export function formatNumber(n: number, locale: string): string {
  return new Intl.NumberFormat(locale, { maximumFractionDigits: 0 }).format(n);
}
export function formatRating(n: number, locale: string): string {
  return new Intl.NumberFormat(locale, { minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(n);
}
export function downloadCSV(filename: string, csv: string): void {
  const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = filename;
  document.body.appendChild(a); a.click(); document.body.removeChild(a);
  URL.revokeObjectURL(url);
}