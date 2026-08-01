/**
 * Hydroma MRV offline store — evidence, points, claims, ledger.
 * Aligned with L1/L2/L3 + VCS/GS/FAO spirit.
 */

export type AssuranceLevel = "L1" | "L2" | "L3";
export type ClaimStatus = "draft" | "submitted" | "under_review" | "verified" | "rejected" | "issued";

export type MonitoringPoint = {
  id: string;
  farmId?: string;
  name: string;
  lat: number;
  lon: number;
  kind: "soil_sample" | "plot_centroid" | "sensor" | "photo_plot";
  notes?: string;
  createdAt: string;
};

export type EvidenceItem = {
  id: string;
  type: "satellite" | "field" | "lab" | "model" | "document";
  label: string;
  value?: number;
  unit?: string;
  source?: string;
  at: string;
};

export type MrvClaim = {
  id: string;
  title: string;
  farmId?: string;
  status: ClaimStatus;
  level: AssuranceLevel;
  measured_tco2e: number;
  quality_score: number;
  permanence_buffer: number;
  issuable_eco: number;
  evidenceIds: string[];
  pointIds: string[];
  methodology: string;
  createdAt: string;
  updatedAt: string;
};

export type LedgerEvent = {
  id: string;
  claimId: string;
  action: string;
  actor: string;
  at: string;
  note?: string;
};

export type SatelliteCard = {
  id: string;
  name: string;
  provider: string;
  resolution_m: number;
  revisit_days: number;
  indices: string[];
  priority_mrv: boolean;
  notes: string;
};

const K_POINTS = "econojin_mrv_points_v1";
const K_EV = "econojin_mrv_evidence_v1";
const K_CLAIMS = "econojin_mrv_claims_v1";
const K_LEDGER = "econojin_mrv_ledger_v1";

export const SATELLITE_CARDS: SatelliteCard[] = [
  { id: "s2", name: "Sentinel-2 MSI", provider: "ESA Copernicus", resolution_m: 10, revisit_days: 5, indices: ["NDVI", "NDMI", "NDRE", "BSI"], priority_mrv: true, notes: "Core optical for vegetation & practice detection" },
  { id: "l8", name: "Landsat 8/9", provider: "USGS/NASA", resolution_m: 30, revisit_days: 8, indices: ["NDVI", "NDMI"], priority_mrv: true, notes: "Long archive for baseline" },
  { id: "s1", name: "Sentinel-1 SAR", provider: "ESA", resolution_m: 10, revisit_days: 6, indices: ["VV/VH", "tillage proxy"], priority_mrv: true, notes: "All-weather structure / tillage" },
  { id: "modis", name: "MODIS/VIIRS", provider: "NASA", resolution_m: 250, revisit_days: 1, indices: ["NDVI", "LST"], priority_mrv: false, notes: "Regional context" },
  { id: "planet", name: "PlanetScope", provider: "Planet (commercial)", resolution_m: 3, revisit_days: 1, indices: ["NDVI", "RGB"], priority_mrv: false, notes: "High-res optional" },
];

export const LEVEL_POLICY: Record<AssuranceLevel, { fa: string; en: string; buffer: number; sources: string }> = {
  L1: {
    fa: "یک منبع (مدل یا ماهواره). بافر ماندگاری ۲۰٪. برای آزمایش داخلی.",
    en: "Single source (model or satellite). 20% permanence buffer. Internal trials.",
    buffer: 0.2,
    sources: "1 of {satellite, field, model}",
  },
  L2: {
    fa: "دو کلاس شواهد مستقل. بافر ۱۲٪. نزدیک پروتکل‌های هیبرید.",
    en: "Two independent evidence classes. 12% buffer. Hybrid-protocol style.",
    buffer: 0.12,
    sources: "2 of {satellite, field/lab, model}",
  },
  L3: {
    fa: "ماهواره + میدان/آزمایشگاه + مدل. بافر ۸٪. اولویت صدور توکن.",
    en: "Satellite + field/lab + model. 8% buffer. Preferred for issuance.",
    buffer: 0.08,
    sources: "all three",
  },
};

function read<T>(key: string, fb: T): T {
  try {
    const r = localStorage.getItem(key);
    if (r) return JSON.parse(r) as T;
  } catch { /* */ }
  return fb;
}
function write(key: string, data: unknown) {
  try { localStorage.setItem(key, JSON.stringify(data)); } catch { /* */ }
}

export function readPoints(): MonitoringPoint[] {
  return read(K_POINTS, [
    { id: "mp1", farmId: "f1", name: "Plot A centroid", lat: 34.52, lon: 69.18, kind: "plot_centroid", createdAt: new Date().toISOString() },
    { id: "mp2", farmId: "f1", name: "Soil sample N1", lat: 34.521, lon: 69.181, kind: "soil_sample", notes: "0–30 cm", createdAt: new Date().toISOString() },
  ]);
}
export function addPoint(p: Omit<MonitoringPoint, "id" | "createdAt">): MonitoringPoint {
  const next = { ...p, id: `mp${Date.now()}`, createdAt: new Date().toISOString() };
  write(K_POINTS, [next, ...readPoints()]);
  return next;
}

export function readEvidence(): EvidenceItem[] {
  return read(K_EV, [
    { id: "e1", type: "satellite", label: "Mean NDVI 30d", value: 0.62, unit: "ndvi", source: "Sentinel-2", at: new Date().toISOString() },
    { id: "e2", type: "model", label: "RothC ΔSOC", value: 0.35, unit: "tC/ha", source: "RothC-26.3", at: new Date().toISOString() },
    { id: "e3", type: "lab", label: "Lab SOC final", value: 41.2, unit: "tC/ha", source: "lab", at: new Date().toISOString() },
  ]);
}
export function addEvidence(e: Omit<EvidenceItem, "id" | "at">): EvidenceItem {
  const next = { ...e, id: `e${Date.now()}`, at: new Date().toISOString() };
  write(K_EV, [next, ...readEvidence()]);
  return next;
}

export function classifyLevel(ev: EvidenceItem[]): AssuranceLevel {
  const hasSat = ev.some((x) => x.type === "satellite");
  const hasField = ev.some((x) => x.type === "field" || x.type === "lab");
  const hasModel = ev.some((x) => x.type === "model");
  const n = [hasSat, hasField, hasModel].filter(Boolean).length;
  if (n >= 3) return "L3";
  if (n >= 2) return "L2";
  return "L1";
}

/** Client-side Q estimate mirroring backend spirit */
export function estimateQuality(ev: EvidenceItem[], additionality = 1, leakage = 0): {
  quality_score: number;
  level: AssuranceLevel;
  permanence_buffer: number;
  effective_mint_factor: number;
} {
  const level = classifyLevel(ev);
  const buffer = LEVEL_POLICY[level].buffer;
  let q = 0.75;
  if (ev.some((x) => x.type === "satellite")) q += 0.08;
  if (ev.some((x) => x.type === "lab" || x.type === "field")) q += 0.1;
  if (ev.some((x) => x.type === "model")) q += 0.06;
  if (level === "L3") q += 0.05;
  q = Math.min(level === "L3" ? 1.2 : level === "L2" ? 1.1 : 1.0, Math.max(0.45, q));
  const u = level === "L1" ? 0.25 : level === "L2" ? 0.15 : 0.08;
  q = q * (1 - u * 0.5);
  const eff = q * additionality * (1 - leakage) * (1 - buffer);
  return {
    quality_score: Math.round(q * 1000) / 1000,
    level,
    permanence_buffer: buffer,
    effective_mint_factor: Math.round(eff * 1000) / 1000,
  };
}

export function readClaims(): MrvClaim[] {
  return read(K_CLAIMS, [
    {
      id: "c1",
      title: "Soil SOC pilot claim A",
      farmId: "f1",
      status: "under_review",
      level: "L2",
      measured_tco2e: 42,
      quality_score: 0.92,
      permanence_buffer: 0.12,
      issuable_eco: 980,
      evidenceIds: ["e1", "e2"],
      pointIds: ["mp1"],
      methodology: "hydroma_hybrid_soc_v1",
      createdAt: new Date(Date.now() - 864e5 * 3).toISOString(),
      updatedAt: new Date().toISOString(),
    },
  ]);
}

export function upsertClaim(c: MrvClaim) {
  const list = readClaims().filter((x) => x.id !== c.id);
  write(K_CLAIMS, [c, ...list]);
}

export function appendLedger(ev: Omit<LedgerEvent, "id" | "at">) {
  const next: LedgerEvent = { ...ev, id: `lg${Date.now()}`, at: new Date().toISOString() };
  write(K_LEDGER, [next, ...read(K_LEDGER, [] as LedgerEvent[])]);
  return next;
}

export function readLedger(claimId?: string): LedgerEvent[] {
  const all = read(K_LEDGER, [] as LedgerEvent[]);
  return claimId ? all.filter((e) => e.claimId === claimId) : all;
}

export function verifyClaim(id: string, actor: string, approve: boolean) {
  const list = readClaims();
  const i = list.findIndex((c) => c.id === id);
  if (i < 0) return;
  list[i] = {
    ...list[i],
    status: approve ? "verified" : "rejected",
    updatedAt: new Date().toISOString(),
  };
  write(K_CLAIMS, list);
  appendLedger({
    claimId: id,
    action: approve ? "verified" : "rejected",
    actor,
    note: approve ? "Independent review passed" : "Insufficient evidence",
  });
}

export function issueClaim(id: string, actor: string) {
  const list = readClaims();
  const i = list.findIndex((c) => c.id === id);
  if (i < 0 || list[i].status !== "verified") return;
  list[i] = { ...list[i], status: "issued", updatedAt: new Date().toISOString() };
  write(K_CLAIMS, list);
  appendLedger({ claimId: id, action: "issued_eco", actor, note: `Mint preview ${list[i].issuable_eco} ECO` });
}
