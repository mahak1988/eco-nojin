// apps/web/src/api/water.ts

export type WaterBalance = {
  id: number;
  scenario_id: number;
  soil_profile_id: number | null;
  date: string;
  precipitation: number | null;
  irrigation: number | null;
  evapotranspiration: number | null;
  runoff: number | null;
  deep_drainage: number | null;
  soil_moisture: number | null;
  model_version: string;
};

export type DailyInput = {
  date: string;
  precipitation?: number | null;
  irrigation?: number | null;
  evapotranspiration?: number | null;
};

export type SimulationRequest = {
  scenario_id: number;
  soil_profile_id: number;
  daily_inputs: DailyInput[];
};

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function simulateWaterBalance(
  payload: SimulationRequest
): Promise<WaterBalance[]> {
  const res = await fetch(`${BASE_URL}/water/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail ?? "Failed to simulate water balance");
  }

  return res.json();
}

export async function getWaterBalance(
  scenarioId: number,
  params?: { startDate?: string; endDate?: string }
): Promise<WaterBalance[]> {
  const search = new URLSearchParams({ scenario_id: String(scenarioId) });
  if (params?.startDate) search.set("start_date", params.startDate);
  if (params?.endDate) search.set("end_date", params.endDate);

  const res = await fetch(`${BASE_URL}/water/balance?${search.toString()}`, {
    method: "GET",
  });

  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail ?? "Failed to fetch water balance");
  }

  return res.json();
}