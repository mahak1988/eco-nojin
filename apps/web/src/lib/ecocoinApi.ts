/** EcoCoin API client — wallet, challenges, rewards, chain. */

const BASE = "/api/v1/ecocoin";

export const DEFAULT_ECO_ADDRESS =
  "0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18";

async function json<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    credentials: "include",
    headers: { "Content-Type": "application/json", Accept: "application/json", ...(init?.headers || {}) },
    ...init,
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg =
      typeof body?.detail === "string"
        ? body.detail
        : body?.error?.message || body?.message || `HTTP ${res.status}`;
    throw new Error(msg);
  }
  return body as T;
}

export type EcoWallet = {
  address: string;
  currency: string;
  available: number;
  staked: number;
  pending_rewards: number;
  impact_credits_tco2e: number;
  total_equity: number;
};

export type ApiChallenge = {
  id: string;
  title: string;
  metric: string;
  target: number;
  pool_eco: number;
  starts_at: string;
  ends_at: string;
  status: string;
  participants: number;
  total_score: number;
};

export type ChainStatus = {
  mode: string;
  rpc_url: string | null;
  contract_address: string | null;
  chain_id: number | string;
  ledger_depth: number;
  recent?: unknown[];
};

export async function fetchWallet(address = DEFAULT_ECO_ADDRESS) {
  return json<EcoWallet>(`/wallet/${address}`);
}

export async function fetchBalance(address = DEFAULT_ECO_ADDRESS) {
  return json<{ address: string; balance: number; currency: string }>(`/balance/${address}`);
}

export async function fetchChallenges(status?: string) {
  const q = status ? `?status=${encodeURIComponent(status)}` : "";
  return json<{ challenges: ApiChallenge[]; total: number }>(`/challenges${q}`);
}

export async function joinChallenge(challengeId: string, address = DEFAULT_ECO_ADDRESS) {
  return json<{ status: string; participants: number }>(`/challenges/${challengeId}/join`, {
    method: "POST",
    body: JSON.stringify({ address }),
  });
}

export async function claimChallenge(
  challengeId: string,
  score: number,
  address = DEFAULT_ECO_ADDRESS,
) {
  return json<{
    status: string;
    reward_eco: number;
    pending_rewards: number;
    chain?: { tx_hash: string };
  }>(`/challenges/${challengeId}/claim`, {
    method: "POST",
    body: JSON.stringify({ address, score }),
  });
}

export async function fetchRewards(address = DEFAULT_ECO_ADDRESS) {
  return json<{ address: string; pending_rewards: number; claimable: boolean }>(
    `/rewards/${address}`,
  );
}

export async function claimRewards(address = DEFAULT_ECO_ADDRESS, amount?: number) {
  return json<{ status: string; amount: number; tx_hash: string; remaining_pending: number }>(
    "/rewards/claim",
    {
      method: "POST",
      body: JSON.stringify({ address, amount: amount ?? null }),
    },
  );
}

export async function fetchStats() {
  return json<Record<string, number>>("/stats");
}

export async function fetchChainStatus() {
  return json<ChainStatus>("/chain/status");
}

export async function impactMint(body: {
  recipient: string;
  project_id: string;
  credit_type: number;
  measured_value: number;
  quality_score?: number;
  region_multiplier?: number;
  verification_hash: string;
}) {
  return json<Record<string, unknown>>("/mining/impact-mint", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function stake(address: string, amount: number, tier_id: number) {
  return json<Record<string, unknown>>("/staking/stake", {
    method: "POST",
    body: JSON.stringify({ address, amount, tier_id }),
  });
}

export async function transfer(from_address: string, to_address: string, amount: number) {
  return json<{ tx_hash: string; status: string; amount: number }>("/transfer", {
    method: "POST",
    body: JSON.stringify({ from_address, to_address, amount }),
  });
}
