/** Free EO stack client — Planetary + Open-Meteo + RUSLE-lite (no paid APIs). */
import { apiFetch, v1 } from "../api/http";

export type EoCatalog = {
  policy?: string;
  primary_hub?: string;
  collections?: Array<{ id: string; family?: string; use?: string }>;
  derived_products?: string[];
  endpoints?: Record<string, string>;
};

export type EoSensors = {
  lat: number;
  lon: number;
  days: number;
  sensors: Array<{ collection: string; family?: string; count: number; error?: string; sample_id?: string }>;
};

export type EoDem = {
  lat: number;
  lon: number;
  elevation_m?: number | null;
  slope_pct_proxy?: number;
  elevation_source?: string;
};

export type EoErosion = {
  lat: number;
  lon: number;
  elevation_m?: number;
  slope_pct_proxy?: number;
  ndvi_latest?: number;
  rain_proxy_mm?: number;
  erosion?: {
    risk_score_0_100?: number;
    label?: string;
    factors?: Record<string, number>;
    model?: string;
  };
  mitigation_hints?: string[];
};

export type EoClimate = {
  lat: number;
  lon: number;
  open_meteo?: Record<string, unknown>;
  nasa_modis_lst_scenes?: { count?: number; use?: string };
};

export type EoSummary = {
  lat: number;
  lon: number;
  policy?: string;
  sensors?: EoSensors["sensors"];
  topography?: EoDem;
  erosion?: EoErosion["erosion"];
  climate?: { open_meteo?: Record<string, unknown>; modis_lst_count?: number };
  vegetation?: Record<string, unknown>;
};

export type NdviPoint = {
  date?: string;
  mean_ndvi?: number;
  max_ndvi?: number;
  min_ndvi?: number;
  source?: string;
  provider?: string;
  cloud_free_percentage?: number;
};

export type VciPack = {
  lat: number;
  lon: number;
  count?: number;
  mode?: string;
  provider?: string;
  latest_vci?: { vci?: number; label?: string };
  timeseries?: Array<Record<string, unknown>>;
};

/** Planetary raster NDVI often needs 20–45s on first cold hit. */
const T_FAST = 20_000;
const T_NDVI = 60_000;
const T_BATCH = 90_000;

const q = (lat: number, lon: number, extra = "") =>
  `?lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}${extra}`;

export async function fetchEoCatalog() {
  return apiFetch<EoCatalog>(v1("/satellite/eo/catalog"), {}, T_FAST);
}

export async function fetchEoSensors(lat: number, lon: number, days = 60) {
  return apiFetch<EoSensors>(v1(`/satellite/eo/sensors${q(lat, lon, `&days=${days}`)}`), {}, T_BATCH);
}

export async function fetchEoVegetation(lat: number, lon: number, days = 60) {
  return apiFetch<Record<string, unknown>>(v1(`/satellite/eo/vegetation${q(lat, lon, `&days=${days}`)}`), {}, T_BATCH);
}

export async function fetchEoDem(lat: number, lon: number) {
  return apiFetch<EoDem>(v1(`/satellite/eo/dem${q(lat, lon)}`), {}, T_FAST);
}

export async function fetchEoErosion(lat: number, lon: number, days = 30) {
  return apiFetch<EoErosion>(v1(`/satellite/eo/erosion${q(lat, lon, `&days=${days}`)}`), {}, T_NDVI);
}

export async function fetchEoClimate(lat: number, lon: number) {
  return apiFetch<EoClimate>(v1(`/satellite/eo/climate${q(lat, lon)}`), {}, T_FAST);
}

export async function fetchEoSummary(lat: number, lon: number) {
  return apiFetch<EoSummary>(v1(`/satellite/eo/summary${q(lat, lon)}`), {}, T_BATCH);
}

export async function fetchNdvi(lat: number, lon: number) {
  return apiFetch<NdviPoint>(v1(`/satellite/ndvi${q(lat, lon)}`), {}, T_NDVI);
}

export async function fetchVci(lat: number, lon: number, days = 60, raster = 0) {
  return apiFetch<VciPack>(v1(`/satellite/vci${q(lat, lon, `&days=${days}&raster=${raster}`)}`), {}, T_BATCH);
}

export async function fetchEoScenes(
  lat: number,
  lon: number,
  collection = "sentinel-2-l2a",
  days = 60,
) {
  return apiFetch<Record<string, unknown>>(
    v1(`/satellite/eo/scenes${q(lat, lon, `&collection=${encodeURIComponent(collection)}&days=${days}`)}`),
    {},
    T_BATCH,
  );
}
