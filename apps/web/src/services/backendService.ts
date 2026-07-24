/**
 * ============================================================================
 *  Backend API Service - Typed service layer for backend communication
 *  سرویس لایه ارتباط با بک‌اند با تایپ‌های صحیح
 * ============================================================================
 */

import { apiClient } from "@/lib/api-client";
import type {
  LoginRequest,
  RegisterRequest,
  RefreshRequest,
  AuthResponse,
  BackendUser,
  AdminDashboardSummary,
  AdminSetting,
  AdminSettingUpdate,
  AuditLog,
  SystemReport,
  AIAgent,
  ConversationCreate,
  ConversationDetail,
  ChatRequest,
  ChatResponse,
  Simulation,
  SimulationCreate,
  SimulationUpdate,
  SimulationListResponse,
} from "@/types/backend";

// ---------------------------------------------------------------------------
// Authentication Endpoints (matching /api/v1/auth/*)
// ---------------------------------------------------------------------------

export const authService = {
  /**
   * Login user with email/username and password
   * POST /api/v1/auth/login
   */
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>("/auth/login", credentials);
    return response.data;
  },

  /**
   * Register new user
   * POST /api/v1/auth/register
   */
  async register(payload: RegisterRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>("/auth/register", payload);
    return response.data;
  },

  /**
   * Get current user info
   * GET /api/v1/auth/me
   */
  async getCurrentUser(): Promise<BackendUser> {
    const response = await apiClient.get<BackendUser>("/auth/me");
    return response.data;
  },

  /**
   * Logout current user
   * POST /api/v1/auth/logout
   */
  async logout(): Promise<void> {
    await apiClient.post("/auth/logout");
  },

  /**
   * Refresh access token
   * POST /api/v1/auth/refresh
   */
  async refreshToken(payload: RefreshRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>("/auth/refresh", payload);
    return response.data;
  },
};

// ---------------------------------------------------------------------------
// User Management Endpoints (matching /api/v1/users/*)
// ---------------------------------------------------------------------------

export const usersService = {
  /**
   * Get current user profile
   * GET /api/v1/users/me
   */
  async getProfile(): Promise<BackendUser> {
    const response = await apiClient.get<BackendUser>("/users/me");
    return response.data;
  },

  /**
   * Update current user profile
   * PUT /api/v1/users/me
   */
  async updateProfile(data: Partial<BackendUser>): Promise<BackendUser> {
    const response = await apiClient.put<BackendUser>("/users/me", data);
    return response.data;
  },

  /**
   * List all users (admin only)
   * GET /api/v1/users/
   */
  async listUsers(skip?: number, limit?: number): Promise<BackendUser[]> {
    const response = await apiClient.get<BackendUser[]>("/users/", {
      params: { skip, limit },
    });
    return response.data;
  },

  /**
   * Deactivate user (admin only)
   * DELETE /api/v1/users/{user_id}
   */
  async deactivateUser(userId: number): Promise<void> {
    await apiClient.delete(`/users/${userId}`);
  },
};

// ---------------------------------------------------------------------------
// Admin Panel Endpoints (matching /api/v1/admin/*)
// ---------------------------------------------------------------------------

export const adminService = {
  /**
   * Get dashboard summary
   * GET /api/v1/admin/
   */
  async getDashboardSummary(): Promise<AdminDashboardSummary> {
    const response = await apiClient.get<AdminDashboardSummary>("/admin/");
    return response.data;
  },

  /**
   * List settings
   * GET /api/v1/admin/settings
   */
  async listSettings(limit?: number, offset?: number): Promise<AdminSetting[]> {
    const response = await apiClient.get<AdminSetting[]>("/admin/settings", {
      params: { limit, offset },
    });
    return response.data;
  },

  /**
   * Get setting by key
   * GET /api/v1/admin/settings/{key}
   */
  async getSettingByKey(key: string): Promise<AdminSetting> {
    const response = await apiClient.get<AdminSetting>(`/admin/settings/${encodeURIComponent(key)}`);
    return response.data;
  },

  /**
   * Update setting
   * PUT /api/v1/admin/settings/{key}
   */
  async updateSetting(key: string, payload: AdminSettingUpdate): Promise<AdminSetting> {
    const response = await apiClient.put<AdminSetting>(`/admin/settings/${encodeURIComponent(key)}`, payload);
    return response.data;
  },

  /**
   * List audit logs
   * GET /api/v1/admin/audit-logs
   */
  async listAuditLogs(
    eventType?: string,
    limit?: number,
    offset?: number
  ): Promise<AuditLog[]> {
    const response = await apiClient.get<AuditLog[]>("/admin/audit-logs", {
      params: { event_type: eventType, limit, offset },
    });
    return response.data;
  },

  /**
   * List system reports
   * GET /api/v1/admin/reports
   */
  async listReports(limit?: number, offset?: number): Promise<SystemReport[]> {
    const response = await apiClient.get<SystemReport[]>("/admin/reports", {
      params: { limit, offset },
    });
    return response.data;
  },
};

// ---------------------------------------------------------------------------
// AI Agents Endpoints (matching /api/v1/ai-agents/*)
// ---------------------------------------------------------------------------

export const aiAgentsService = {
  /**
   * Create new conversation
   * POST /api/v1/ai-agents/conversations
   */
  async createConversation(payload: ConversationCreate): Promise<ConversationDetail> {
    const response = await apiClient.post<ConversationDetail>("/ai-agents/conversations", payload);
    return response.data;
  },

  /**
   * Get conversation details
   * GET /api/v1/ai-agents/conversations/{id}
   */
  async getConversation(id: number): Promise<ConversationDetail> {
    const response = await apiClient.get<ConversationDetail>(`/ai-agents/conversations/${id}`);
    return response.data;
  },

  /**
   * List user conversations
   * GET /api/v1/ai-agents/conversations
   */
  async listConversations(): Promise<ConversationDetail[]> {
    const response = await apiClient.get<ConversationDetail[]>("/ai-agents/conversations");
    return response.data;
  },

  /**
   * Send chat message to AI agent
   * POST /api/v1/ai-agents/chat
   */
  async chat(payload: ChatRequest): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>("/ai-agents/chat", payload);
    return response.data;
  },
};

// ---------------------------------------------------------------------------
// Simulation Endpoints (matching /api/v1/simulation/*)
// ---------------------------------------------------------------------------

export const simulationService = {
  /**
   * List simulations
   * GET /api/v1/simulation/
   */
  async listSimulations(skip?: number, limit?: number): Promise<SimulationListResponse> {
    const response = await apiClient.get<SimulationListResponse>("/simulation/", {
      params: { skip, limit },
    });
    return response.data;
  },

  /**
   * Create new simulation
   * POST /api/v1/simulation/
   */
  async createSimulation(payload: SimulationCreate): Promise<Simulation> {
    const response = await apiClient.post<Simulation>("/simulation/", payload);
    return response.data;
  },

  /**
   * Get simulation by ID
   * GET /api/v1/simulation/{id}
   */
  async getSimulation(id: number): Promise<Simulation> {
    const response = await apiClient.get<Simulation>(`/simulation/${id}`);
    return response.data;
  },

  /**
   * Update simulation
   * PATCH /api/v1/simulation/{id}
   */
  async updateSimulation(id: number, payload: SimulationUpdate): Promise<Simulation> {
    const response = await apiClient.patch<Simulation>(`/simulation/${id}`, payload);
    return response.data;
  },

  /**
   * Delete simulation
   * DELETE /api/v1/simulation/{id}
   */
  async deleteSimulation(id: number): Promise<void> {
    await apiClient.delete(`/simulation/${id}`);
  },
};
