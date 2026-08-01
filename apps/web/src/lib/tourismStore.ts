/**
 * Eco-tourism visit requests — GSTC-aligned lightweight flow.
 */

const KEY = "econojin_tourism_requests_v1";

export type TourismRequest = {
  id: string;
  destinationId: string;
  destinationName: string;
  visitorName: string;
  email: string;
  partySize: number;
  date: string;
  interests: string;
  status: "requested" | "confirmed" | "cancelled";
  createdAt: string;
};

export function readTourRequests(): TourismRequest[] {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) {
      const p = JSON.parse(raw) as TourismRequest[];
      if (Array.isArray(p)) return p;
    }
  } catch {
    /* ignore */
  }
  return [];
}

export function writeTourRequests(list: TourismRequest[]) {
  try {
    localStorage.setItem(KEY, JSON.stringify(list));
  } catch {
    /* ignore */
  }
}

export function submitTourRequest(data: {
  destinationId: string;
  destinationName: string;
  visitorName: string;
  email: string;
  partySize: number;
  date: string;
  interests: string;
}): TourismRequest[] {
  const req: TourismRequest = {
    id: `tr${Date.now()}`,
    destinationId: data.destinationId,
    destinationName: data.destinationName,
    visitorName: data.visitorName.trim(),
    email: data.email.trim(),
    partySize: Math.max(1, data.partySize || 1),
    date: data.date || new Date().toISOString().slice(0, 10),
    interests: data.interests.trim(),
    status: "requested",
    createdAt: new Date().toISOString(),
  };
  const list = [req, ...readTourRequests()];
  writeTourRequests(list);
  return list;
}

export function setTourRequestStatus(
  id: string,
  status: TourismRequest["status"]
): TourismRequest[] {
  const list = readTourRequests().map((r) => (r.id === id ? { ...r, status } : r));
  writeTourRequests(list);
  return list;
}
