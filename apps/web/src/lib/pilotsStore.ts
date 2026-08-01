/**
 * Pilots workflow — request, phase advance, convert to Hydroma-approved region.
 * Offline-first; no local pilot village names in user-facing defaults.
 */

import {
  PILOTS,
  PHASE_ORDER,
  type Pilot,
  type PilotPhase,
} from "../components/pilots/pilotsData";

const KEY = "econojin_pilots_v1";
const REQ_KEY = "econojin_pilot_requests_v1";

export type PilotRequest = {
  id: string;
  title: string;
  climateZoneId?: string;
  regionCode: string;
  lat?: number;
  lon?: number;
  researchNote: string;
  contact: string;
  status: "submitted" | "review" | "approved" | "rejected";
  createdAt: string;
};

export function readPilots(): Pilot[] {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) {
      const p = JSON.parse(raw) as Pilot[];
      if (Array.isArray(p) && p.length) return p;
    }
  } catch {
    /* ignore */
  }
  return PILOTS.map((x) => ({ ...x }));
}

export function writePilots(list: Pilot[]) {
  try {
    localStorage.setItem(KEY, JSON.stringify(list));
  } catch {
    /* ignore */
  }
}

export function readRequests(): PilotRequest[] {
  try {
    const raw = localStorage.getItem(REQ_KEY);
    if (raw) {
      const p = JSON.parse(raw) as PilotRequest[];
      if (Array.isArray(p)) return p;
    }
  } catch {
    /* ignore */
  }
  return [];
}

export function writeRequests(list: PilotRequest[]) {
  try {
    localStorage.setItem(REQ_KEY, JSON.stringify(list));
  } catch {
    /* ignore */
  }
}

export function submitPilotRequest(data: {
  title: string;
  regionCode: string;
  researchNote: string;
  contact: string;
  climateZoneId?: string;
  lat?: number;
  lon?: number;
}): PilotRequest[] {
  const req: PilotRequest = {
    id: `pr${Date.now()}`,
    title: data.title.trim(),
    regionCode: data.regionCode.trim() || "MN",
    researchNote: data.researchNote.trim(),
    contact: data.contact.trim(),
    climateZoneId: data.climateZoneId,
    lat: data.lat,
    lon: data.lon,
    status: "submitted",
    createdAt: new Date().toISOString(),
  };
  const list = [req, ...readRequests()];
  writeRequests(list);
  return list;
}

export function setRequestStatus(
  id: string,
  status: PilotRequest["status"]
): PilotRequest[] {
  const list = readRequests().map((r) => (r.id === id ? { ...r, status } : r));
  writeRequests(list);
  return list;
}

export function advancePilotPhase(id: string, current: Pilot[]): Pilot[] {
  const list = current.map((p) => {
    if (p.id !== id) return p;
    const i = PHASE_ORDER.indexOf(p.phase);
    if (i < 0 || i >= PHASE_ORDER.length - 1) return p;
    const next = PHASE_ORDER[i + 1];
    const progress =
      next === "active" ? Math.max(p.progress, 40)
      : next === "monitoring" ? Math.max(p.progress, 75)
      : next === "completed" ? 100
      : p.progress;
    return { ...p, phase: next, progress };
  });
  writePilots(list);
  return list;
}

export function pilotToRegionPayload(p: Pilot): {
  id: string;
  name: string;
  code: string;
  lat: number;
  lon: number;
  status: "active";
  sourcePilotId: string;
} {
  const loc = p.locationKey.replace(/^loc_/, "").toUpperCase().slice(0, 2) || "MN";
  return {
    id: `reg-from-${p.id}`,
    name: `Hydroma-approved · ${p.nameKey}`,
    code: loc,
    lat: 32.5 + (p.id.charCodeAt(2) % 10) * 0.4,
    lon: 51.5 + (p.id.charCodeAt(3) % 10) * 0.5,
    status: "active",
    sourcePilotId: p.id,
  };
}

export function approveRequestAsPilot(
  req: PilotRequest,
  current: Pilot[]
): Pilot[] {
  const pilot: Pilot = {
    id: `pi-req-${req.id}`,
    nameKey: "p_custom",
    descKey: "d_custom",
    goalKey: "g_custom",
    locationKey: "loc_custom",
    phase: "planning",
    progress: 5,
    beneficiaries: 0,
    teamSize: 2,
    budgetUsd: 25000,
    startDate: new Date().toISOString(),
    image: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=800&q=80",
    objectives: [{ key: "o_design" }],
  };
  try {
    const labels = JSON.parse(localStorage.getItem("econojin_pilot_labels_v1") || "{}");
    labels[pilot.id] = {
      name: req.title,
      desc: req.researchNote || req.title,
      goal: "Hydroma pilot research & monitoring",
      location: req.regionCode,
    };
    localStorage.setItem("econojin_pilot_labels_v1", JSON.stringify(labels));
  } catch {
    /* ignore */
  }
  const list = [pilot, ...current];
  writePilots(list);
  setRequestStatus(req.id, "approved");
  return list;
}

export function readPilotLabels(): Record<
  string,
  { name: string; desc: string; goal: string; location: string }
> {
  try {
    return JSON.parse(localStorage.getItem("econojin_pilot_labels_v1") || "{}");
  } catch {
    return {};
  }
}
