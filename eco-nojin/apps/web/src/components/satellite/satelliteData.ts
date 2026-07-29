// apps/web/src/components/satellite/satelliteData.ts
export type Layer = "satellite" | "ndvi" | "thermal";
export type CloudFilter = "all" | "clear" | "moderate" | "cloudy";
export type SortKey = "ndvi" | "date" | "cloud";
export type SortDir = "asc" | "desc";

export interface Tile {
  id: string;
  nameKey: string;
  date: string;          // ISO
  cloud: number;         // 0..100
  ndvi: number;          // 0..1
  thermal: number;       // 0..1 (دمای سطح نسبی)
  coverage: number;      // 0..100
  imgIndex: number;      // index در SATELLITE_IMGS
  ndviHistory: number[]; // sparkline
}

// pool کوچک تصویر ماهواره — هر کدام SmartImg+fallback دارد (درس gamecoca)
export const SATELLITE_IMGS = [
  "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=900&q=80",
  "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=900&q=80",
  "https://images.unsplash.com/photo-1473773508845-188df298d2d1?auto=format&fit=crop&w=900&q=80",
];

const d = (y: number, m: number, day: number) => new Date(y, m - 1, day).toISOString();

export const TILES: Tile[] = [
  { id: "s1", nameKey: "t1", date: d(2026, 7, 18), cloud: 12, ndvi: 0.78, thermal: 0.42, coverage: 78, imgIndex: 0, ndviHistory: [0.62, 0.66, 0.7, 0.72, 0.75, 0.78] },
  { id: "s2", nameKey: "t2", date: d(2026, 7, 17), cloud: 5, ndvi: 0.82, thermal: 0.38, coverage: 82, imgIndex: 1, ndviHistory: [0.7, 0.73, 0.76, 0.79, 0.8, 0.82] },
  { id: "s3", nameKey: "t3", date: d(2026, 7, 16), cloud: 25, ndvi: 0.45, thermal: 0.71, coverage: 45, imgIndex: 2, ndviHistory: [0.5, 0.48, 0.47, 0.46, 0.45, 0.45] },
  { id: "s4", nameKey: "t4", date: d(2026, 7, 15), cloud: 8, ndvi: 0.69, thermal: 0.55, coverage: 70, imgIndex: 2, ndviHistory: [0.55, 0.58, 0.61, 0.64, 0.67, 0.69] },
  { id: "s5", nameKey: "t5", date: d(2026, 7, 14), cloud: 31, ndvi: 0.33, thermal: 0.8, coverage: 33, imgIndex: 0, ndviHistory: [0.4, 0.38, 0.37, 0.35, 0.34, 0.33] },
  { id: "s6", nameKey: "t6", date: d(2026, 7, 13), cloud: 3, ndvi: 0.88, thermal: 0.3, coverage: 90, imgIndex: 1, ndviHistory: [0.78, 0.8, 0.82, 0.84, 0.86, 0.88] },
];

export const LAYERS: Layer[] = ["satellite", "ndvi", "thermal"];
export const CLOUD_FILTERS: CloudFilter[] = ["all", "clear", "moderate", "cloudy"];

// ── color scales (محاسباتی، بدون وابستگی) ──
function lerp(a: number, b: number, t: number): number { return Math.round(a + (b - a) * t); }
function hex(r: number, g: number, b: number): string {
  return "#" + [r, g, b].map((v) => v.toString(16).padStart(2, "0")).join("");
}
function ramp(stops: [number, number, number][], t: number): string {
  const x = Math.max(0, Math.min(1, t)) * (stops.length - 1);
  const i = Math.floor(x);
  const f = x - i;
  const a = stops[i], b = stops[Math.min(i + 1, stops.length - 1)];
  return hex(lerp(a[0], b[0], f), lerp(a[1], b[1], f), lerp(a[2], b[2], f));
}
// NDVI: 0=برهنه(قرمز/قهوه‌ای) → 1=پوشش انبوه(سبز تیره)
const NDVI_STOPS: [number, number, number][] = [[150, 60, 40], [202, 138, 4], [132, 204, 22], [21, 128, 61], [6, 78, 59]];
// Thermal: 0=سرد(آبی) → 1=گرم(قرمز)
const THERMAL_STOPS: [number, number, number][] = [[37, 99, 235], [14, 165, 233], [250, 204, 21], [249, 115, 22], [220, 38, 38]];
export const ndviColor = (v: number): string => ramp(NDVI_STOPS, v);
export const thermalColor = (v: number): string => ramp(THERMAL_STOPS, v);
export const NDVI_GRADIENT = `linear-gradient(90deg, ${NDVI_STOPS.map((s, i) => hex(s[0], s[1], s[2]) + " " + Math.round((i / (NDVI_STOPS.length - 1)) * 100) + "%").join(", ")})`;
export const THERMAL_GRADIENT = `linear-gradient(90deg, ${THERMAL_STOPS.map((s, i) => hex(s[0], s[1], s[2]) + " " + Math.round((i / (THERMAL_STOPS.length - 1)) * 100) + "%").join(", ")})`;

// پس‌زمینهٔ viewport per layer/tile (همیشه کار می‌کند — درس Vite)
export function viewportBg(layer: Layer, t: Tile): string {
  if (layer === "ndvi") {
    const c = ndviColor(t.ndvi);
    return `radial-gradient(circle at 32% 30%, ${c}, ${ndviColor(t.ndvi * 0.6)} 55%, ${ndviColor(t.ndvi * 0.3)} 100%)`;
  }
  if (layer === "thermal") {
    const c = thermalColor(t.thermal);
    return `radial-gradient(circle at 62% 42%, ${c}, ${thermalColor(t.thermal * 0.55)} 60%, ${thermalColor(t.thermal * 0.25)} 100%)`;
  }
  return "linear-gradient(135deg, #0b1f17, #10331f 50%, #0a1a12)"; // satellite fallback tint
}

// ── KPI derived ──
export const mean = (xs: number[]): number => (xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : 0);
export const meanNdvi = (tiles: Tile[]): number => mean(tiles.map((t) => t.ndvi));
export const meanCloud = (tiles: Tile[]): number => mean(tiles.map((t) => t.cloud));
export const bestTile = (tiles: Tile[]): Tile | null =>
  tiles.length ? tiles.reduce((a, b) => (b.ndvi > a.ndvi ? b : a)) : null;
export const cloudBucket = (c: number): Exclude<CloudFilter, "all"> =>
  c < 10 ? "clear" : c <= 20 ? "moderate" : "cloudy";

export function formatNumber(n: number, locale: string): string {
  return new Intl.NumberFormat(locale, { maximumFractionDigits: 0 }).format(n);
}
export function formatNdvi(n: number, locale: string): string {
  return new Intl.NumberFormat(locale, { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n);
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