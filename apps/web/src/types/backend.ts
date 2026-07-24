/**
 * ============================================================================
 *  Backend API Types - TypeScript definitions matching Python backend schemas
 *  تعاریف TypeScript که با اسکیماهای بک‌اند پایتون مطابقت دارند
 * ============================================================================
 */

// ---------------------------------------------------------------------------
// User Types (matching apps/users/schemas.py and auth_router.py)
// ---------------------------------------------------------------------------

export interface BackendUser {
  id: number;
  email: string;
  full_name?: string | null;
  role: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

// ---------------------------------------------------------------------------
// Authentication Types (matching auth_router.py)
// ---------------------------------------------------------------------------

export interface LoginRequest {
  email?: string;
  username?: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
  role?: string;
}

export interface RefreshRequest {
  refreshToken: string;
}

export interface AuthResponse {
  accessToken: string;
  refreshToken: string;
  user: BackendUser;
}

// ---------------------------------------------------------------------------
// API Response Types
// ---------------------------------------------------------------------------

export interface ApiResponse<T> {
  detail?: string;
  message?: string;
  [key: string]: any;
}

export interface ErrorResponse {
  detail: string | { msg: string };
  status_code?: number;
}

// ---------------------------------------------------------------------------
// Admin Types (matching admin_panel/schemas.py)
// ---------------------------------------------------------------------------

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
  description?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AdminSettingUpdate {
  value?: string;
  description?: string;
  is_active?: boolean;
}

export interface AuditLog {
  id: number;
  actor_id?: number | null;
  actor_email?: string | null;
  event_type: string;
  event_data?: string | null;
  created_at: string;
}

export interface SystemReport {
  id: number;
  report_name: string;
  status: string;
  report_data?: string | null;
  created_at: string;
  completed_at?: string | null;
}

// ---------------------------------------------------------------------------
// Pagination Types
// ---------------------------------------------------------------------------

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

// ---------------------------------------------------------------------------
// AI Agents Types (matching ai_agents/schemas.py)
// ---------------------------------------------------------------------------

export type AgentType = 
  | "financial" 
  | "support" 
  | "admin" 
  | "research" 
  | "data_analyst" 
  | "code_assistant";

export interface AIAgent {
  id: number;
  name: string;
  description?: string | null;
  agent_type: AgentType;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface MessageResponse {
  id: number;
  role: "user" | "assistant" | "tool";
  content: string;
  tool_calls?: Record<string, any> | null;
  tool_call_id?: string | null;
  created_at: string;
}

export interface ConversationCreate {
  agent_type: AgentType;
  title?: string;
}

export interface ConversationResponse {
  id: number;
  user_id: number;
  agent_type: AgentType;
  title?: string | null;
  created_at: string;
  updated_at: string;
  message_count?: number;
}

export interface ConversationDetail extends ConversationResponse {
  messages: MessageResponse[];
}

export interface ChatRequest {
  conversation_id?: number;
  message: string;
  agent_type?: AgentType;
}

export interface ChatResponse {
  conversation_id: number;
  assistant_message: string;
  messages: MessageResponse[];
}

// ---------------------------------------------------------------------------
// Simulation Types (matching simulation/schemas.py)
// ---------------------------------------------------------------------------

export interface Simulation {
  id: number;
  name: string;
  description?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SimulationCreate {
  name: string;
  description?: string;
}

export interface SimulationUpdate {
  name?: string;
  description?: string;
  is_active?: boolean;
}

export interface SimulationListResponse {
  items: Simulation[];
  total: number;
  skip: number;
  limit: number;
}
