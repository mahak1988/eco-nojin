// ============================================================================
// Soil & Water Types - Professional Version
// ============================================================================

export interface LDNResult {
  ldn_score: number;
  status: "healthy" | "degraded" | "critical";
  soil_organic_carbon: number;
  vegetation_cover: number;
  erosion_risk: number;
}

export interface NDVIResult {
  ndvi: number;
  vegetation_health: string;
}

export interface NDWIResult {
  ndwi: number;
  water_presence: boolean;
}

export interface RUSLEResult {
  soil_loss_tons_per_ha: number;
  erosion_risk_category: "low" | "moderate" | "high" | "very_high";
  r_factor: number;
  k_factor: number;
  ls_factor: number;
  c_factor: number;
  p_factor: number;
}

export interface WaterBalanceResult {
  precipitation: number;
  evapotranspiration: number;
  runoff: number;
  net_water: number;
  soil_moisture_initial: number;
  soil_moisture_final: number;
  soil_moisture_change: number;
  water_surplus: boolean;
}

export interface IrrigationResult {
  water_requirement_mm: number;
  irrigation_interval_days: number;
  efficiency_percentage: number;
  depletion_fraction: number;
  crop_type: string;
  recommended_date: string;
}

export interface DroughtResult {
  spi: number;
  drought_category: string;
}

export interface CarbonResult {
  carbon_stock_tons_per_ha: number;
  soil_organic_carbon_pct: number;
  bulk_density: number;
  depth_cm: number;
}

export interface AnalysisIndices {
  ldn?: LDNResult;
  ndvi?: NDVIResult;
  ndwi?: NDWIResult;
  rusle?: RUSLEResult;
  water_balance?: WaterBalanceResult;
  irrigation?: IrrigationResult;
  drought?: DroughtResult;
  carbon?: CarbonResult;
}

export interface ComprehensiveAnalysisRequest {
  ldn?: { soil_organic_carbon: number; vegetation_cover: number; erosion_risk: number };
  ndvi?: { nir: number; red: number };
  ndwi?: { green: number; nir: number };
  rusle?: { r_factor: number; k_factor: number; ls_factor: number; c_factor: number; p_factor: number };
  water_balance?: { precipitation: number; evapotranspiration: number; runoff_coefficient: number; soil_moisture_initial: number };
  irrigation?: { crop_type: string; field_capacity: number; wilting_point: number; current_moisture: number; et_crop: number; efficiency: number };
  drought?: { spi: number };
  carbon?: { soil_organic_carbon_pct: number; bulk_density: number; depth_cm: number };
}

export interface ComprehensiveAnalysisResponse {
  indices: AnalysisIndices;
  overall_health: "excellent" | "good" | "warning" | "critical";
  overall_score: number;
  recommendations: string[];
  timestamp: string;
}

export interface Project {
  id: number;
  title: string;
  description?: string;
  location?: string;
  farmer_id?: number;
  area_hectares?: number;
  soil_type?: string;
  crop_type?: string;
  status: string;
  created_at: string;
  updated_at?: string;
  analysis_count?: number;
  analyses?: AnalysisReport[];
}

export interface AnalysisReport {
  id: number;
  project_id?: number;
  title: string;
  inputs?: ComprehensiveAnalysisRequest;
  results?: ComprehensiveAnalysisResponse;
  overall_score?: number;
  overall_health?: string;
  notes?: string;
  created_at: string;
}

export interface DashboardStats {
  total_projects: number;
  active_projects: number;
  total_analyses: number;
  avg_score: number;
  health_distribution: Record<string, number>;
  recent_analyses: AnalysisReport[];
}
