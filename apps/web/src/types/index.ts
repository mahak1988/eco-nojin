/**
 * ============================================================================
 *  Type Definitions — Core types for the Econojin platform
 *  تعاریف نوع برای پلتفرم اکونوجین
 * ============================================================================
 */

// Export backend types
export type {
  BackendUser,
  LoginRequest,
  RegisterPayload as RegisterRequest,
  RefreshRequest,
  AuthResponse,
  ApiResponse,
  ErrorResponse,
  AdminDashboardSummary,
  AdminSetting,
  AdminSettingUpdate,
  AuditLog,
  SystemReport,
  PaginatedResponse,
  AgentType,
  AIAgent,
  MessageResponse,
  ConversationCreate,
  ConversationResponse,
  ConversationDetail,
  ChatRequest as AIChatRequest,
  ChatResponse as AIChatResponse,
  Simulation,
  SimulationCreate,
  SimulationUpdate,
  SimulationListResponse,
} from "./backend";

// Re-export existing types
export type {
  User,
  AuthCredentials,
  AuthSession,
  RegisterPayload,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  MeResponse,
  ApiError,
  PaginatedResponse as LegacyPaginatedResponse,
  AdminDashboardSummary as LegacyAdminDashboardSummary,
  AdminSetting as LegacyAdminSetting,
  AuditLog as LegacyAuditLog,
  SystemReport as LegacySystemReport,
} from "./index_original";

// ---------------------------------------------------------------------------
// User Roles
// ---------------------------------------------------------------------------

export type UserRole = 'farmer' | 'student' | 'expert' | 'manager' | 'researcher' | 'user';

// ---------------------------------------------------------------------------
// Document Types
// ---------------------------------------------------------------------------

export interface Document {
  id: string;
  title: string;
  description?: string;
  url: string;
  tags: string[];
  status: 'draft' | 'published' | 'archived';
  createdAt: string;
  updatedAt: string;
}

// ---------------------------------------------------------------------------
// Watershed Types
// ---------------------------------------------------------------------------

export interface Watershed {
  id: string;
  name: string;
  province: string;
  area: number;
  status: 'monitored' | 'unmonitored' | 'critical';
  coordinates?: {
    latitude: number;
    longitude: number;
  };
}

// ---------------------------------------------------------------------------
// Carbon & Soil Metrics
// ---------------------------------------------------------------------------

export interface CarbonMetric {
  id: string;
  location: string;
  value: number;
  unit: string;
  timestamp: string;
}

export interface SoilMetric {
  id: string;
  location: string;
  ph: number;
  organicMatter: number;
  nitrogen: number;
  phosphorus: number;
  potassium: number;
  timestamp: string;
}

// ---------------------------------------------------------------------------
// Common Types
// ---------------------------------------------------------------------------

export interface PaginationMeta {
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
}
