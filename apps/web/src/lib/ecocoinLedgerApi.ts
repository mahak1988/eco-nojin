/**
 * Phase 4 — EcoCoin ledger API client (local_ledger / dual-write).
 * Base URL from Vite env or same-origin /api/v1.
 */
const BASE =
  (import.meta as any).env?.VITE_API_BASE?.replace(/\/$/, "") || "/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const j = await res.json();
      detail = j.detail || JSON.stringify(j);
    } catch {
      /* ignore */
    }
    throw new Error(`${res.status}: ${detail}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export type AssuranceLevel = "L1" | "L2" | "L3" | "L4";

export type ClaimOut = {
  id: number;
  claim_uid: string;
  user_id: string;
  category: string;
  level: AssuranceLevel;
  status: string;
  title?: string | null;
  description?: string | null;
  evidence_hash?: string | null;
  geo_lat?: string | number | null;
  geo_lng?: string | number | null;
  quality_score?: string | number | null;
  reward_amount?: string | number | null;
  verifier_id?: string | null;
  rejection_reason?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
  rewarded_at?: string | null;
};

export type ClaimListOut = {
  data: ClaimOut[];
  meta: { total: number; page: number; size: number; pages: number };
};

export type ClaimCreateBody = {
  user_id: string;
  category: string;
  level?: AssuranceLevel;
  title?: string;
  description?: string;
  evidence_hash?: string;
  geo_lat?: number;
  geo_lng?: number;
  metadata?: Record<string, unknown>;
  submit?: boolean;
};

export type BucketOut = {
  code: string;
  name?: string;
  allocation_pct?: string | number;
  total_allocated?: string | number;
  remaining?: string | number;
  released?: string | number;
};

export type TreasuryOut = {
  mode: string;
  max_supply: string | number;
  total_minted?: string | number;
  buckets: BucketOut[];
  disclaimer?: string;
};

export type BalanceOut = {
  user_id: string;
  balance: string | number;
  currency?: string;
};

export async function createClaim(body: ClaimCreateBody): Promise<ClaimOut> {
  return request<ClaimOut>("/ecocoin/claims", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function listClaims(params: {
  user_id?: string;
  status?: string;
  category?: string;
  page?: number;
  size?: number;
}): Promise<ClaimListOut> {
  const q = new URLSearchParams();
  if (params.user_id) q.set("user_id", params.user_id);
  if (params.status) q.set("status", params.status);
  if (params.category) q.set("category", params.category);
  q.set("page", String(params.page ?? 1));
  q.set("size", String(params.size ?? 20));
  return request<ClaimListOut>(`/ecocoin/claims?${q.toString()}`);
}

export async function getClaim(claimUid: string): Promise<ClaimOut> {
  return request<ClaimOut>(`/ecocoin/claims/${encodeURIComponent(claimUid)}`);
}

export async function getTreasury(): Promise<TreasuryOut> {
  return request<TreasuryOut>("/ecocoin/treasury");
}

export async function getBalance(userId: string): Promise<BalanceOut> {
  return request<BalanceOut>(`/ecocoin/balance/${encodeURIComponent(userId)}`);
}
