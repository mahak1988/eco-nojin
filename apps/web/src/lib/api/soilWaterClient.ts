// AUTO-GENERATED & REFINED CLIENT FOR SOIL & WATER DOMAIN/MODULE
// Based on modules/soil_water/schemas.py and related API design in the backend.

// ---------------------------------------------------------------------------
// Shared HTTP utilities
// ---------------------------------------------------------------------------

export type HttpMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH";

export interface ApiClientOptions {
  baseUrl: string;
  token?: string;
}

function buildHeaders(options?: ApiClientOptions): HeadersInit {
  const headers: HeadersInit = { "Content-Type": "application/json" };
  if (options?.token) {
    (headers as any)["Authorization"] = `Bearer ${options.token}`;
  }
  return headers;
}

async function apiRequest<TResponse = any, TBody = any>(
  path: string,
  method: HttpMethod,
  body?: TBody,
  options?: ApiClientOptions
): Promise<TResponse> {
  const url = `${options?.baseUrl ?? ""}${path}`;
  const res = await fetch(url, {
    method,
    headers: buildHeaders(options),
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Request failed ${res.status}: ${text}`);
  }

  const contentType = res.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return (await res.json()) as TResponse;
  }
  return (await res.text()) as unknown as TResponse;
}

// ---------------------------------------------------------------------------
// Types mirrored from modules/soil_water/schemas.py
// ---------------------------------------------------------------------------

// Project & analysis project-level metadata
export interface ProjectCreate {
  title: string;
  description?: string | null;
  location?: string | null;
  farmer_id?: number | null;
  area_hectares?: number | null;
  soil_type?: string | null;
  crop_type?: string | null;
}

export interface ProjectResponse {
  id: number;
  title: string;
  description?: string | null;
  location?: string | null;
  farmer_id?: number | null;
  area_hectares?: number | null;
  soil_type?: string | null;
  crop_type?: string | null;
  status: string;
  created_at: string; // datetime ISO
  updated_at?: string | null; // datetime ISO
  analysis_count: number;
}

export interface ProjectUpdate {
  title?: string | null;
  description?: string | null;
  location?: string | null;
  area_hectares?: number | null;
  soil_type?: string | null;
  crop_type?: string | null;
  status?: string | null;
}

// High-level dashboard stats for soil & water
export interface DashboardStats {
  total_projects: number;
  active_projects: number;
  total_analyses: number;
  avg_score: number;
  health_distribution: Record<string, number>;
  recent_analyses: AnalysisReportResponse[];
}

// Individual analysis reports
export interface AnalysisReportCreate {
  project_id?: number | null;
  title: string;
  inputs: Record<string, any>;
  results: Record<string, any>;
  notes?: string | null;
}

export interface AnalysisReportResponse {
  id: number;
  project_id?: number | null;
  title: string;
  inputs?: Record<string, any> | null;
  results?: Record<string, any> | null;
  overall_score?: number | null;
  overall_health?: string | null;
  notes?: string | null;
  created_at: string; // datetime ISO
}

export interface AnalysisReportUpdate {
  title?: string | null;
  notes?: string | null;
}

// Soil-water analysis at pilot/region level
export interface SoilWaterAnalysisCreate {
  region: string;
  soil_type?: string | null;
  area_ha: number;
  crop: string;
  irrigation_method?: string | null;
  parameters?: Record<string, any> | null;
}

export interface SoilWaterAnalysisResponse {
  id: string;
  region: string;
  soil_type?: string | null;
  area_ha: number;
  crop: string;
  irrigation_method?: string | null;
  results?: Record<string, any> | null;
  status: string;
  created_at: string;
  updated_at?: string | null;
}

export interface SoilWaterAnalysisList {
  analyses: SoilWaterAnalysisResponse[];
  total: number;
}

// Component indices and results
export interface LDNResult {
  ldn_score: number;
  status: string;
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
  erosion_risk_category: string;
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
  recommended_date: string; // could be date string
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

// Comprehensive indices and composite analysis
export interface ComprehensiveIndices {
  ldn?: LDNResult | null;
  ndvi?: NDVIResult | null;
  ndwi?: NDWIResult | null;
  rusle?: RUSLEResult | null;
  water_balance?: WaterBalanceResult | null;
  irrigation?: IrrigationResult | null;
  drought?: DroughtResult | null;
  carbon?: CarbonResult | null;
}

export interface ComprehensiveAnalysisRequest {
  ldn?: Record<string, any> | null;
  ndvi?: Record<string, any> | null;
  ndwi?: Record<string, any> | null;
  rusle?: Record<string, any> | null;
  water_balance?: Record<string, any> | null;
  irrigation?: Record<string, any> | null;
  drought?: Record<string, any> | null;
  carbon?: Record<string, any> | null;
}

export interface ComprehensiveAnalysisResponse {
  indices: ComprehensiveIndices;
  overall_health: string;
  overall_score: number;
  recommendations: string[];
  timestamp: string;
}

// Soil & erosion analysis
export interface SoilAnalysisRequest {
  location_lat: number;
  location_lon: number;
  soil_type: string;
  organic_matter_percent: number;
  moisture_content: number;
  ph_level: number;
}

export interface ErosionRiskResponse {
  location_lat: number;
  location_lon: number;
  risk_level: string;
  rusle_value: number;
  contributing_factors: string[];
  recommendation: string;
}

// ---------------------------------------------------------------------------
// Endpoint wrappers (مسیرها «نمونه» هستند؛ با API واقعی خود هماهنگ کنید)
// ---------------------------------------------------------------------------

// NOTE: مسیرهای زیر را با روتر FastAPI واقعی خود هماهنگ کنید.
// این‌ها نام‌گذاری منطقی هستند، مثلاً:
//  - /soil-water/dashboard
//  - /soil-water/projects
//  - /soil-water/analyses
//  - /soil-water/comprehensive
//  - /soil-water/erosion
// اگر در backend شما مسیرها فرق دارد، فقط path را عوض کنید.

// 1) Dashboard stats
export async function getSoilWaterDashboardStats(
  options?: ApiClientOptions
): Promise<DashboardStats> {
  return apiRequest<DashboardStats>("/soil-water/dashboard", "GET", undefined, options);
}

// 2) Project CRUD
export async function createSoilWaterProject(
  body: ProjectCreate,
  options?: ApiClientOptions
): Promise<ProjectResponse> {
  return apiRequest<ProjectResponse, ProjectCreate>(
    "/soil-water/projects",
    "POST",
    body,
    options
  );
}

export async function listSoilWaterProjects(
  options?: ApiClientOptions
): Promise<ProjectResponse[]> {
  return apiRequest<ProjectResponse[]>("/soil-water/projects", "GET", undefined, options);
}

export async function getSoilWaterProjectById(
  projectId: number,
  options?: ApiClientOptions
): Promise<ProjectResponse> {
  return apiRequest<ProjectResponse>(
    `/soil-water/projects/${projectId}`,
    "GET",
    undefined,
    options
  );
}

export async function updateSoilWaterProject(
  projectId: number,
  body: ProjectUpdate,
  options?: ApiClientOptions
): Promise<ProjectResponse> {
  return apiRequest<ProjectResponse, ProjectUpdate>(
    `/soil-water/projects/${projectId}`,
    "PUT",
    body,
    options
  );
}

// 3) Analysis reports
export async function createAnalysisReport(
  body: AnalysisReportCreate,
  options?: ApiClientOptions
): Promise<AnalysisReportResponse> {
  return apiRequest<AnalysisReportResponse, AnalysisReportCreate>(
    "/soil-water/analysis-reports",
    "POST",
    body,
    options
  );
}

export async function listAnalysisReports(
  options?: ApiClientOptions
): Promise<AnalysisReportResponse[]> {
  return apiRequest<AnalysisReportResponse[]>(
    "/soil-water/analysis-reports",
    "GET",
    undefined,
    options
  );
}

export async function getAnalysisReportById(
  reportId: number,
  options?: ApiClientOptions
): Promise<AnalysisReportResponse> {
  return apiRequest<AnalysisReportResponse>(
    `/soil-water/analysis-reports/${reportId}`,
    "GET",
    undefined,
    options
  );
}

export async function updateAnalysisReport(
  reportId: number,
  body: AnalysisReportUpdate,
  options?: ApiClientOptions
): Promise<AnalysisReportResponse> {
  return apiRequest<AnalysisReportResponse, AnalysisReportUpdate>(
    `/soil-water/analysis-reports/${reportId}`,
    "PUT",
    body,
    options
  );
}

// 4) Soil-water analyses (region-level)
export async function createSoilWaterAnalysis(
  body: SoilWaterAnalysisCreate,
  options?: ApiClientOptions
): Promise<SoilWaterAnalysisResponse> {
  return apiRequest<SoilWaterAnalysisResponse, SoilWaterAnalysisCreate>(
    "/soil-water/analyses",
    "POST",
    body,
    options
  );
}

export async function listSoilWaterAnalyses(
  options?: ApiClientOptions
): Promise<SoilWaterAnalysisList> {
  return apiRequest<SoilWaterAnalysisList>(
    "/soil-water/analyses",
    "GET",
    undefined,
    options
  );
}

export async function getSoilWaterAnalysisById(
  analysisId: string,
  options?: ApiClientOptions
): Promise<SoilWaterAnalysisResponse> {
  return apiRequest<SoilWaterAnalysisResponse>(
    `/soil-water/analyses/${analysisId}`,
    "GET",
    undefined,
    options
  );
}

// 5) Comprehensive analysis (LDN, NDVI, NDWI, RUSLE, water balance, irrigation, drought, carbon)
export async function runComprehensiveSoilWaterAnalysis(
  body: ComprehensiveAnalysisRequest,
  options?: ApiClientOptions
): Promise<ComprehensiveAnalysisResponse> {
  return apiRequest<ComprehensiveAnalysisResponse, ComprehensiveAnalysisRequest>(
    "/soil-water/comprehensive",
    "POST",
    body,
    options
  );
}

// 6) Soil & erosion analysis
export async function runSoilAnalysis(
  body: SoilAnalysisRequest,
  options?: ApiClientOptions
): Promise<ErosionRiskResponse> {
  return apiRequest<ErosionRiskResponse, SoilAnalysisRequest>(
    "/soil-water/soil-analysis",
    "POST",
    body,
    options
  );
}