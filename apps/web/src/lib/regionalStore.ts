/**
 * User-registered regions on map + field linkage.
 * Offline-first. No local pilot village names — climate/country codes only.
 */

const KEY = "econojin_user_regions_v1";

export type UserRegion = {
  id: string;
  name: string;
  code: string;
  lat: number;
  lon: number;
  status: "planning" | "active" | "approved";
  areaHa?: number;
  notes?: string;
  sourcePilotId?: string;
  createdAt: string;
};

const SEED: UserRegion[] = [
  {
    id: "ur1",
    name: "Arid highland zone A",
    code: "AF",
    lat: 34.5,
    lon: 69.2,
    status: "active",
    areaHa: 1200,
    notes: "SPI/VHI monitoring active",
    createdAt: new Date(Date.now() - 86400000 * 40).toISOString(),
  },
  {
    id: "ur2",
    name: "Mesopotamia irrigation belt",
    code: "IQ",
    lat: 33.3,
    lon: 44.4,
    status: "active",
    areaHa: 2400,
    createdAt: new Date(Date.now() - 86400000 * 20).toISOString(),
  },
];

export function readUserRegions(): UserRegion[] {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) {
      const p = JSON.parse(raw) as UserRegion[];
      if (Array.isArray(p) && p.length) return p;
    }
  } catch {
    /* ignore */
  }
  return [...SEED];
}

export function writeUserRegions(list: UserRegion[]) {
  try {
    localStorage.setItem(KEY, JSON.stringify(list));
  } catch {
    /* ignore */
  }
}

export function addUserRegion(
  data: {
    name: string;
    code: string;
    lat: number;
    lon: number;
    areaHa?: number;
    notes?: string;
    sourcePilotId?: string;
    status?: UserRegion["status"];
  },
  current: UserRegion[]
): UserRegion[] {
  const next: UserRegion = {
    id: `ur${Date.now()}`,
    name: data.name.trim(),
    code: data.code.trim().toUpperCase().slice(0, 4) || "MN",
    lat: data.lat,
    lon: data.lon,
    areaHa: data.areaHa,
    notes: data.notes,
    sourcePilotId: data.sourcePilotId,
    status: data.status ?? "planning",
    createdAt: new Date().toISOString(),
  };
  const list = [next, ...current];
  writeUserRegions(list);
  return list;
}

export function updateUserRegionStatus(
  id: string,
  status: UserRegion["status"],
  current: UserRegion[]
): UserRegion[] {
  const list = current.map((r) => (r.id === id ? { ...r, status } : r));
  writeUserRegions(list);
  return list;
}

export function removeUserRegion(id: string, current: UserRegion[]): UserRegion[] {
  const list = current.filter((r) => r.id !== id);
  writeUserRegions(list);
  return list;
}
