// apps/web/src/lib/types/landSoilWater.ts

export type ScenarioType = "baseline" | "management";

export type GeometryType = "polygon" | "point" | "raster_cell";

export type IndicatorCode =
  | "runoff_mm"
  | "soil_loss_t_ha"
  | "soil_water_content_mm"
  | "infiltration_mm"
  | "erosion_risk_index";

export type AnalysisStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed"
  | "finalized"
  | "on_chain_registered";

export interface LandUnit {
  id: string;
  name: string;
  geometry_type: GeometryType;
  area_ha: number;
  centroid_lat: number;
  centroid_lon: number;
  region_id?: string | null;
}

export interface SoilProfile {
  land_unit_id: string;
  depth_cm: number;
  texture: string;
  organic_carbon_pct: number;
  bulk_density: number;
  available_water_capacity: number;
}

export interface ClimatePoint {
  date: string; // ISO date (YYYY-MM-DD)
  precipitation_mm: number;
  tmean_c?: number | null;
  et0_mm?: number | null;
}

export interface IndicatorTimeseriesPoint {
  date: string; // ISO date
  value: number;
}

export interface IndicatorTimeseries {
  indicator: IndicatorCode;
  unit: string;
  series: IndicatorTimeseriesPoint[];
}

export interface ScenarioPractice {
  code: string;
  description?: string | null;
}

export interface Scenario {
  id?: string;
  name: string;
  description?: string | null;
  scenario_type: ScenarioType;
  land_unit_ids: string[];
  practices: ScenarioPractice[];
  start_date?: string | null; // ISO date
  end_date?: string | null;   // ISO date
}

export interface AnalysisSummary {
  id: string;
  user_id: string;
  land_unit_id: string;
  scenario_id?: string | null;
  scenario_type: ScenarioType;
  status: AnalysisStatus;
  created_at: string; // ISO datetime
  updated_at: string; // ISO datetime
  period_start?: string | null; // ISO date
  period_end?: string | null;   // ISO date
  indicators_avg: Partial<Record<IndicatorCode, number>>;
}

export interface AnalysisDetail {
  summary: AnalysisSummary;
  soil_profile?: SoilProfile | null;
  climate?: ClimatePoint[] | null;
  timeseries: IndicatorTimeseries[];
}

export interface LandUnitWithIndicators {
  land_unit: LandUnit;
  indicators_avg: Partial<Record<IndicatorCode, number>>;
}

export interface LandUnitListResponse {
  items: LandUnitWithIndicators[];
  total: number;
}

export interface IndicatorDefinition {
  code: IndicatorCode;
  unit: string;
  title_fa: string;
  title_en: string;
  description_fa?: string | null;
  description_en?: string | null;
}

export interface IndicatorListResponse {
  indicators: IndicatorDefinition[];
}

export interface CreateAnalysisRequest {
  land_unit_id: string;
  scenario: Scenario;
  indicators?: IndicatorCode[];
}

export interface CreateAnalysisResponse {
  analysis_id: string;
  status: AnalysisStatus;
}