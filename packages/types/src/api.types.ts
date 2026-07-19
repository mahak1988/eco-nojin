// API Types for econojin web application

export interface CarbonMetric {
  id: string;
  region: string;
  co2eTons: number;
  source: "industrial" | "transport" | "agriculture" | "residential";
  recordedAt: string;
}

export interface CarbonProject {
  id: string;
  name: string;
  description: string;
  location: string;
  startDate: string;
  endDate: string | null;
  status: "active" | "completed" | "planned";
  baselineEmissions: number;
  reductions: number;
}

export interface CarbonStock {
  id: string;
  projectId: string;
  year: number;
  stock: number;
  sequestrationRate: number;
}

export interface Document {
  id: string;
  title: string;
  description: string;
  fileUrl: string;
  fileType: string;
  tags: string[];
  createdAt: string;
  updatedAt: string;
}

export interface PaginationMeta {
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface SoilMetric {
  id: string;
  location: string;
  ph: number;
  organicMatter: number;
  nitrogen: number;
  phosphorus: number;
  potassium: number;
  recordedAt: string;
}

export interface SoilSample {
  id: string;
  location: string;
  depthCm: number;
  collectedAt: string;
  status: "pending" | "analyzed" | "archived";
}

export interface SoilAnalysis {
  id: string;
  sampleId: string;
  ph: number;
  organicMatter: number;
  nitrogen: number;
  phosphorus: number;
  potassium: number;
  recommendations: string[];
}

export interface Watershed {
  id: string;
  name: string;
  areaKm2: number;
  annualRainfallMm: number;
  population: number;
  mainRiver: string;
}

export interface Simulation {
  id: string;
  name: string;
  type: "hydrology" | "carbon" | "soil";
  config: Record<string, unknown>;
  result: Record<string, unknown> | null;
  createdAt: string;
}

export interface HydrologyFrontend {
  id: string;
  name: string;
  areaKm2: number;
  annualRainfallMm: number;
  population: number;
  mainRiver: string;
}

export interface HydrologyFrontendCreate {
  name: string;
  areaKm2: number;
  annualRainfallMm: number;
  population: number;
  mainRiver: string;
}

export interface HydrologyFrontendUpdate {
  name?: string;
  areaKm2?: number;
  annualRainfallMm?: number;
  population?: number;
  mainRiver?: string;
}

export interface HydrologyFrontendListResponse {
  watersheds: HydrologyFrontend[];
  total: number;
}