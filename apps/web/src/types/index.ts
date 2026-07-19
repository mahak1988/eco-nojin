/**
 * ============================================================================
 *  Type Definitions — Core types for the Econojin platform
 * ============================================================================
 */

// ---------------------------------------------------------------------------
// User Roles
// ---------------------------------------------------------------------------

export type UserRole = 'farmer' | 'student' | 'expert' | 'manager' | 'researcher' | 'user';

export interface User {
  id: string | number;
  email: string;
  username?: string;
  displayName?: string;
  full_name?: string;
  firstName?: string;
  lastName?: string;
  bio?: string;
  avatarUrl?: string;
  role: UserRole;
  status?: string;
  is_active?: boolean;
  is_superuser?: boolean;
  createdAt?: string;
  updatedAt?: string;
  emailVerified?: boolean;
}

// ---------------------------------------------------------------------------
// Authentication Types
// ---------------------------------------------------------------------------

export interface AuthCredentials {
  email?: string;
  username?: string;
  password: string;
  rememberMe?: boolean;
}

export interface AuthSession {
  accessToken: string;
  refreshToken?: string;
  user: User;
  expiresAt?: number;
}

export interface RegisterPayload {
  email: string;
  password: string;
  full_name?: string;
  role?: UserRole;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  new_password: string;
}

export interface MeResponse {
  id: string | number;
  email: string;
  username?: string;
  full_name?: string;
  role?: UserRole;
  is_active?: boolean;
  is_superuser?: boolean;
  created_at?: string;
  updated_at?: string;
  email_verified?: boolean;
}

// ---------------------------------------------------------------------------
// API Error Types
// ---------------------------------------------------------------------------

export interface ApiError {
  statusCode: number;
  error: string;
  message: string | string[];
  detail?: string | Record<string, any>;
}

// ---------------------------------------------------------------------------
// Common Types
// ---------------------------------------------------------------------------

export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface AdminDashboardSummary {
  user_count: number;
  active_user_count: number;
  superuser_count: number;
  total_settings: number;
  total_audit_logs: number;
  total_reports: number;
}

export interface AdminSetting {
  id: number;
  key: string;
  value: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuditLog {
  id: number;
  actor_id?: number;
  actor_email?: string;
  event_type: string;
  event_data?: string;
  created_at: string;
}

export interface SystemReport {
  id: number;
  report_name: string;
  status: string;
  report_data?: string;
  created_at: string;
  completed_at?: string;
}

// ---------------------------------------------------------------------------
// Carbon Types
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// Document Types
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// Soil Types
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// Hydrology Types
// ---------------------------------------------------------------------------

export interface Watershed {
  id: string;
  name: string;
  areaKm2: number;
  annualRainfallMm: number;
  population: number;
  mainRiver: string;
  config?: {
    rainRunoffCoeff?: number;
    evapotranspiration?: number;
  };
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