/** Offline-first farms — Hydroma sustainable + restoration; no local village names. */
export type FarmKind = "crop" | "livestock" | "greenhouse" | "pasture" | "mixed" | "aquaculture" | "agroforestry";
export type FarmStatus = "active" | "planning" | "restoring" | "archived";
export type Farm = {
  id: string; name: string; kind: FarmKind; status: FarmStatus; regionCode: string;
  climateZoneId?: string; areaHa: number; lat?: number; lon?: number; description?: string;
  hydromaScore: number; restorationGoals: string[]; createdAt: string; updatedAt: string;
};
export type FarmField = { id: string; farmId: string; name: string; areaHa: number; cropOrCover?: string; soilHealth?: "poor" | "fair" | "good" | "excellent"; notes?: string };
export type LivestockGroup = { id: string; farmId: string; species: string; headCount: number; paddock?: string; healthNote?: string };
export type FarmTask = { id: string; farmId: string; title: string; due?: string; status: "todo" | "doing" | "done"; category: "water" | "soil" | "livestock" | "crop" | "restoration" | "compliance" };

const KEY = "econojin_farms_v2";
const KEY_FIELDS = "econojin_farm_fields_v1";
const KEY_LIVE = "econojin_farm_livestock_v1";
const KEY_TASKS = "econojin_farm_tasks_v1";

const SEED: Farm[] = [
  { id: "f1", name: "Highland mixed unit A", kind: "mixed", status: "active", regionCode: "AF", climateZoneId: "arid_mountain", areaHa: 42, lat: 34.52, lon: 69.18, description: "Crop + small ruminants · SPI monitoring", hydromaScore: 72, restorationGoals: ["soil_organic", "water_efficiency"], createdAt: new Date(Date.now() - 864e5 * 60).toISOString(), updatedAt: new Date().toISOString() },
  { id: "f2", name: "Greenhouse cluster B", kind: "greenhouse", status: "active", regionCode: "IQ", climateZoneId: "semi_arid_plain", areaHa: 1.8, lat: 33.31, lon: 44.36, description: "Protected cultivation · IPM", hydromaScore: 81, restorationGoals: ["ipm", "energy_solar"], createdAt: new Date(Date.now() - 864e5 * 30).toISOString(), updatedAt: new Date().toISOString() },
  { id: "f3", name: "Rotational pasture C", kind: "pasture", status: "restoring", regionCode: "JO", climateZoneId: "semi_arid_plain", areaHa: 120, lat: 31.95, lon: 35.91, description: "Paddock rest cycles · forage recovery", hydromaScore: 65, restorationGoals: ["pasture_recovery", "biodiversity"], createdAt: new Date(Date.now() - 864e5 * 90).toISOString(), updatedAt: new Date().toISOString() },
];

function readJson<T>(key: string, fallback: T): T {
  try { const raw = localStorage.getItem(key); if (raw) return JSON.parse(raw) as T; } catch { /* */ }
  return fallback;
}
function writeJson(key: string, data: unknown) {
  try { localStorage.setItem(key, JSON.stringify(data)); } catch { /* */ }
}

export function readFarms(): Farm[] {
  const list = readJson<Farm[]>(KEY, []);
  if (list.length) return list;
  writeJson(KEY, SEED);
  return [...SEED];
}
export function writeFarms(list: Farm[]) { writeJson(KEY, list); }
export function getFarm(id: string) { return readFarms().find((f) => f.id === id); }
export function addFarm(data: Omit<Farm, "id" | "createdAt" | "updatedAt" | "hydromaScore"> & { hydromaScore?: number }): Farm {
  const farm: Farm = { ...data, id: `f${Date.now()}`, hydromaScore: data.hydromaScore ?? 50, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() };
  writeFarms([farm, ...readFarms()]);
  return farm;
}
export function updateFarm(id: string, patch: Partial<Farm>) {
  const list = readFarms(); const i = list.findIndex((f) => f.id === id); if (i < 0) return undefined;
  list[i] = { ...list[i], ...patch, updatedAt: new Date().toISOString() }; writeFarms(list); return list[i];
}
export function removeFarm(id: string) { writeFarms(readFarms().filter((f) => f.id !== id)); }

export function readFields(farmId?: string): FarmField[] {
  const all = readJson<FarmField[]>(KEY_FIELDS, [
    { id: "ff1", farmId: "f1", name: "Field North", areaHa: 12, cropOrCover: "wheat+legume", soilHealth: "fair" },
    { id: "ff2", farmId: "f1", name: "Field South", areaHa: 8, cropOrCover: "cover crop", soilHealth: "good" },
    { id: "ff3", farmId: "f3", name: "Paddock 1", areaHa: 40, cropOrCover: "native forage", soilHealth: "fair" },
  ]);
  return farmId ? all.filter((x) => x.farmId === farmId) : all;
}
export function addField(f: Omit<FarmField, "id">): FarmField {
  const next = { ...f, id: `ff${Date.now()}` }; writeJson(KEY_FIELDS, [next, ...readFields()]); return next;
}
export function readLivestock(farmId?: string): LivestockGroup[] {
  const all = readJson<LivestockGroup[]>(KEY_LIVE, [
    { id: "lv1", farmId: "f1", species: "sheep", headCount: 85, paddock: "Field South", healthNote: "vaccination OK" },
    { id: "lv2", farmId: "f3", species: "cattle", headCount: 40, paddock: "Paddock 1" },
  ]);
  return farmId ? all.filter((x) => x.farmId === farmId) : all;
}
export function addLivestock(g: Omit<LivestockGroup, "id">): LivestockGroup {
  const next = { ...g, id: `lv${Date.now()}` }; writeJson(KEY_LIVE, [next, ...readLivestock()]); return next;
}
export function readTasks(farmId?: string): FarmTask[] {
  const all = readJson<FarmTask[]>(KEY_TASKS, [
    { id: "t1", farmId: "f1", title: "Soil moisture check", status: "todo", category: "water", due: new Date().toISOString().slice(0, 10) },
    { id: "t2", farmId: "f1", title: "Plant cover crop strip", status: "doing", category: "restoration" },
    { id: "t3", farmId: "f2", title: "IPM sticky trap count", status: "todo", category: "crop" },
    { id: "t4", farmId: "f3", title: "Move herd to rest paddock", status: "todo", category: "livestock" },
  ]);
  return farmId ? all.filter((x) => x.farmId === farmId) : all;
}
export function addTask(t: Omit<FarmTask, "id">): FarmTask {
  const next = { ...t, id: `t${Date.now()}` }; writeJson(KEY_TASKS, [next, ...readTasks()]); return next;
}
export function setTaskStatus(id: string, status: FarmTask["status"]) {
  const all = readTasks().map((t) => (t.id === id ? { ...t, status } : t)); writeJson(KEY_TASKS, all); return all;
}

export const HYDROMA_POLICY = {
  principles: [
    { id: "p1", fa: "توسعه پایدار تولید بدون تخریب اکوسیستم", en: "Sustainable production without ecosystem degradation" },
    { id: "p2", fa: "احیای خاک، آب و تنوع زیستی به‌عنوان شاخص موفقیت", en: "Soil, water and biodiversity recovery as success metrics" },
    { id: "p3", fa: "پایش شفاف (ماهواره + زمینی) و آمادگی MRV", en: "Transparent monitoring (satellite + ground) and MRV readiness" },
    { id: "p4", fa: "بدون نام‌گذاری روستای محلی در داده‌های عمومی", en: "No local village names in public datasets" },
    { id: "p5", fa: "اولویت اقلیم‌هوشمند و بهره‌وری آب", en: "Climate-smart priority and water productivity" },
  ],
  scoreWeights: { water: 25, soil: 25, biodiversity: 20, energy: 15, community: 15 },
};

export const KIND_LABEL: Record<FarmKind, { fa: string; en: string; icon: string }> = {
  crop: { fa: "زراعی", en: "Crop", icon: "🌾" },
  livestock: { fa: "دامی", en: "Livestock", icon: "🐄" },
  greenhouse: { fa: "گلخانه", en: "Greenhouse", icon: "🏠" },
  pasture: { fa: "مرتع", en: "Pasture", icon: "🌿" },
  mixed: { fa: "ترکیبی", en: "Mixed", icon: "🔀" },
  aquaculture: { fa: "آبزی‌پروری", en: "Aquaculture", icon: "🐟" },
  agroforestry: { fa: "جنگل‌زراعی", en: "Agroforestry", icon: "🌳" },
};
