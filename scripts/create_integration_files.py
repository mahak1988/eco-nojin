#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eco Nojin - Phase 4 File Creator
=================================
ایجاد ۱۳ فایل integration + بازنویسی ۲ فایل

نحوه اجرا:
    python scripts/create_integration_files.py
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime

# ============================================================
# Configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "apps" / "web" / "src"

# ============================================================
# File Contents
# ============================================================

NEW_FILES = {
    # ============================================================
    # 1. API Client
    # ============================================================
    "lib/api-client.ts": '''/**
 * ============================================================================
 *  API Client — Axios instance with interceptors
 * ============================================================================
 */

import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from "axios";
import { tokenStorage } from "@/services/authService";

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const API_BASE_URL: string =
  (import.meta.env["VITE_API_BASE_URL"] as string | undefined) ??
  "http://localhost:8000";

const API_TIMEOUT = 30000;

// ---------------------------------------------------------------------------
// Axios Instance
// ---------------------------------------------------------------------------

export const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: API_TIMEOUT,
  headers: {
    "Content-Type": "application/json",
    "Accept": "application/json",
  },
});

// ---------------------------------------------------------------------------
// Request Interceptor — Add Auth Token
// ---------------------------------------------------------------------------

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = tokenStorage.getAccessToken();
    
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error: AxiosError) => Promise.reject(error)
);

// ---------------------------------------------------------------------------
// Response Interceptor — Handle Errors
// ---------------------------------------------------------------------------

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: unknown) => void;
  reject: (reason?: unknown) => void;
}> = [];

const processQueue = (error: AxiosError | null, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            return apiClient(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }
      
      originalRequest._retry = true;
      isRefreshing = true;
      
      try {
        const refreshToken = tokenStorage.getRefreshToken();
        
        if (!refreshToken) {
          throw new Error("No refresh token available");
        }
        
        const response = await axios.post(
          `${API_BASE_URL}/api/v1/auth/refresh`,
          { refreshToken },
          { headers: { "Content-Type": "application/json" } }
        );
        
        const { accessToken, refreshToken: newRefreshToken } = response.data;
        
        tokenStorage.set({
          accessToken,
          refreshToken: newRefreshToken,
        });
        
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${accessToken}`;
        }
        
        processQueue(null, accessToken);
        return apiClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError as AxiosError, null);
        tokenStorage.clear();
        
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
        
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }
    
    return Promise.reject(error);
  }
);

// ---------------------------------------------------------------------------
// Helper Functions
// ---------------------------------------------------------------------------

export const getApiBaseUrl = (): string => API_BASE_URL;

export const isApiAvailable = async (): Promise<boolean> => {
  try {
    await axios.get(`${API_BASE_URL}/health`, { timeout: 5000 });
    return true;
  } catch {
    return false;
  }
};

export default apiClient;
''',

    # ============================================================
    # 2. Query Client
    # ============================================================
    "lib/query-client.ts": '''/**
 * ============================================================================
 *  Query Client — React Query configuration
 * ============================================================================
 */

import { QueryClient } from "@tanstack/react-query";

const isDevelopment = import.meta.env.DEV;

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      gcTime: 1000 * 60 * 10,
      retry: (failureCount: number, error: any) => {
        if (error?.response?.status === 401) return false;
        if (error?.response?.status === 403) return false;
        if (error?.response?.status === 404) return false;
        return failureCount < 2;
      },
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
    },
    mutations: {
      retry: 1,
    },
  },
});

export default queryClient;
''',

    # ============================================================
    # 3. API Errors
    # ============================================================
    "lib/api-errors.ts": '''/**
 * ============================================================================
 *  API Errors — Structured error handling
 * ============================================================================
 */

import { AxiosError } from "axios";

export interface ApiErrorResponse {
  statusCode?: number;
  error?: string;
  message?: string;
  detail?: string | Record<string, any>;
}

export class ApiError extends Error {
  public statusCode: number;
  public errorType: string;
  public detail?: string | Record<string, any>;
  public originalError?: AxiosError;
  
  constructor(
    message: string,
    statusCode: number = 500,
    errorType: string = "UNKNOWN_ERROR",
    detail?: string | Record<string, any>,
    originalError?: AxiosError
  ) {
    super(message);
    this.name = "ApiError";
    this.statusCode = statusCode;
    this.errorType = errorType;
    this.detail = detail;
    this.originalError = originalError;
  }
  
  static fromAxiosError(error: AxiosError<ApiErrorResponse>): ApiError {
    const response = error.response;
    const data = response?.data;
    
    return new ApiError(
      data?.message || error.message || "An unknown error occurred",
      response?.status || 500,
      data?.error || "UNKNOWN_ERROR",
      data?.detail,
      error
    );
  }
  
  isNetworkError(): boolean {
    return !this.originalError?.response;
  }
  
  isUnauthorized(): boolean {
    return this.statusCode === 401;
  }
  
  isValidationError(): boolean {
    return this.statusCode === 422;
  }
}

export const handleApiError = (error: unknown): ApiError => {
  if (error instanceof ApiError) return error;
  if (error instanceof AxiosError) return ApiError.fromAxiosError(error);
  if (error instanceof Error) return new ApiError(error.message);
  return new ApiError("An unknown error occurred");
};

export const getErrorMessage = (error: unknown): string => {
  const apiError = handleApiError(error);
  
  if (apiError.isValidationError() && typeof apiError.detail === "object") {
    const errors = Object.values(apiError.detail).flat();
    return errors.join(", ");
  }
  
  return apiError.message;
};

export default ApiError;
''',

    # ============================================================
    # 4. User Service
    # ============================================================
    "services/userService.ts": '''/**
 * ============================================================================
 *  User Service — CRUD operations for users
 * ============================================================================
 */

import { apiClient } from "@/lib/api-client";
import type { User } from "@/types";

export interface UserCreate {
  email: string;
  password: string;
  full_name?: string;
}

export interface UserUpdate {
  email?: string;
  full_name?: string;
  is_active?: boolean;
}

export interface UserListResponse {
  items: User[];
  total: number;
  page: number;
  pageSize: number;
}

const ENDPOINTS = {
  users: "/users",
  userById: (id: number | string) => `/users/${id}`,
} as const;

export const userService = {
  async getAll(params?: { page?: number; pageSize?: number }): Promise<UserListResponse> {
    const response = await apiClient.get<UserListResponse>(ENDPOINTS.users, { params });
    return response.data;
  },
  
  async getById(id: number | string): Promise<User> {
    const response = await apiClient.get<User>(ENDPOINTS.userById(id));
    return response.data;
  },
  
  async create(data: UserCreate): Promise<User> {
    const response = await apiClient.post<User>(ENDPOINTS.users, data);
    return response.data;
  },
  
  async update(id: number | string, data: UserUpdate): Promise<User> {
    const response = await apiClient.put<User>(ENDPOINTS.userById(id), data);
    return response.data;
  },
  
  async delete(id: number | string): Promise<void> {
    await apiClient.delete(ENDPOINTS.userById(id));
  },
};

export default userService;
''',

    # ============================================================
    # 5. AI Agent Service
    # ============================================================
    "services/aiAgentService.ts": '''/**
 * ============================================================================
 *  AI Agent Service — Chat and agent operations
 * ============================================================================
 */

import { apiClient } from "@/lib/api-client";

export interface Agent {
  id: string;
  name: string;
  description: string;
  type: "financial" | "research" | "support" | "admin" | "code_assistant" | "data_analyst";
  capabilities: string[];
}

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp?: string;
}

export interface ChatRequest {
  message: string;
  history?: ChatMessage[];
  context?: Record<string, any>;
}

export interface ChatResponse {
  response: string;
  agent_id: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

const ENDPOINTS = {
  agents: "/ai-agents",
  agentById: (id: string) => `/ai-agents/${id}`,
  chat: (id: string) => `/ai-agents/${id}/chat`,
  chatStream: (id: string) => `/ai-agents/${id}/chat/stream`,
} as const;

export const aiAgentService = {
  async getAll(): Promise<Agent[]> {
    const response = await apiClient.get<Agent[]>(ENDPOINTS.agents);
    return response.data;
  },
  
  async getById(id: string): Promise<Agent> {
    const response = await apiClient.get<Agent>(ENDPOINTS.agentById(id));
    return response.data;
  },
  
  async chat(agentId: string, request: ChatRequest): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>(
      ENDPOINTS.chat(agentId),
      request
    );
    return response.data;
  },
  
  async *chatStream(
    agentId: string,
    request: ChatRequest
  ): AsyncGenerator<string, void, unknown> {
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
    const token = localStorage.getItem("econojin.access_token");
    
    const response = await fetch(
      `${API_BASE_URL}/api/v1${ENDPOINTS.chatStream(agentId)}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(request),
      }
    );
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const reader = response.body?.getReader();
    if (!reader) throw new Error("Response body is not readable");
    
    const decoder = new TextDecoder();
    
    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\\n");
        
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6);
            if (data === "[DONE]") return;
            yield data;
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  },
};

export default aiAgentService;
''',

    # ============================================================
    # 6. Simulation Service
    # ============================================================
    "services/simulationService.ts": '''/**
 * ============================================================================
 *  Simulation Service — Run and manage simulations
 * ============================================================================
 */

import { apiClient } from "@/lib/api-client";

export interface Simulation {
  id: string;
  name: string;
  type: "climate" | "hydrology" | "crop" | "carbon" | "flood" | "drought" | "biodiversity" | "soil_erosion";
  status: "pending" | "running" | "completed" | "failed";
  created_at: string;
  completed_at?: string;
  parameters: Record<string, any>;
  results?: Record<string, any>;
}

export interface SimulationRunRequest {
  type: Simulation["type"];
  parameters: Record<string, any>;
  name?: string;
}

export interface SimulationResult {
  id: string;
  data: Record<string, any>;
  summary: {
    titleKey: string;
    metrics: Array<{ labelKey: string; value: string }>;
  };
  warnings: string[];
  duration: number;
}

const ENDPOINTS = {
  simulations: "/simulations",
  simulationById: (id: string) => `/simulations/${id}`,
  run: "/simulations/run",
  result: (id: string) => `/simulations/${id}/result`,
} as const;

export const simulationService = {
  async getAll(): Promise<Simulation[]> {
    const response = await apiClient.get<Simulation[]>(ENDPOINTS.simulations);
    return response.data;
  },
  
  async getById(id: string): Promise<Simulation> {
    const response = await apiClient.get<Simulation>(ENDPOINTS.simulationById(id));
    return response.data;
  },
  
  async run(request: SimulationRunRequest): Promise<Simulation> {
    const response = await apiClient.post<Simulation>(ENDPOINTS.run, request);
    return response.data;
  },
  
  async getResult(id: string): Promise<SimulationResult> {
    const response = await apiClient.get<SimulationResult>(ENDPOINTS.result(id));
    return response.data;
  },
  
  async cancel(id: string): Promise<void> {
    await apiClient.post(`${ENDPOINTS.simulationById(id)}/cancel`);
  },
  
  async delete(id: string): Promise<void> {
    await apiClient.delete(ENDPOINTS.simulationById(id));
  },
};

export default simulationService;
''',

    # ============================================================
    # 7. useUsers Hook
    # ============================================================
    "hooks/useUsers.ts": '''/**
 * ============================================================================
 *  useUsers — React Query hooks for user operations
 * ============================================================================
 */

import {
  useQuery,
  useMutation,
  useQueryClient,
  UseQueryOptions,
} from "@tanstack/react-query";
import { userService, UserCreate, UserUpdate } from "@/services/userService";
import type { User } from "@/types";

export const userKeys = {
  all: ["users"] as const,
  lists: () => [...userKeys.all, "list"] as const,
  list: (params: Record<string, any>) => [...userKeys.lists(), params] as const,
  details: () => [...userKeys.all, "detail"] as const,
  detail: (id: number | string) => [...userKeys.details(), id] as const,
};

export const useUsers = (
  params?: { page?: number; pageSize?: number },
  options?: Omit<UseQueryOptions<any>, "queryKey" | "queryFn">
) => {
  return useQuery({
    queryKey: userKeys.list(params || {}),
    queryFn: () => userService.getAll(params),
    ...options,
  });
};

export const useUser = (
  id: number | string,
  options?: Omit<UseQueryOptions<User>, "queryKey" | "queryFn">
) => {
  return useQuery({
    queryKey: userKeys.detail(id),
    queryFn: () => userService.getById(id),
    enabled: !!id,
    ...options,
  });
};

export const useCreateUser = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: UserCreate) => userService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
    },
  });
};

export const useUpdateUser = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number | string; data: UserUpdate }) =>
      userService.update(id, data),
    onSuccess: (data, variables) => {
      queryClient.setQueryData(userKeys.detail(variables.id), data);
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
    },
  });
};

export const useDeleteUser = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number | string) => userService.delete(id),
    onSuccess: (_, id) => {
      queryClient.removeQueries({ queryKey: userKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
    },
  });
};
''',

    # ============================================================
    # 8. useAiAgents Hook
    # ============================================================
    "hooks/useAiAgents.ts": '''/**
 * ============================================================================
 *  useAiAgents — React Query hooks for AI agent operations
 * ============================================================================
 */

import {
  useQuery,
  useMutation,
  UseQueryOptions,
} from "@tanstack/react-query";
import {
  aiAgentService,
  Agent,
  ChatRequest,
} from "@/services/aiAgentService";

export const agentKeys = {
  all: ["agents"] as const,
  lists: () => [...agentKeys.all, "list"] as const,
  details: () => [...agentKeys.all, "detail"] as const,
  detail: (id: string) => [...agentKeys.details(), id] as const,
};

export const useAiAgents = (
  options?: Omit<UseQueryOptions<Agent[]>, "queryKey" | "queryFn">
) => {
  return useQuery({
    queryKey: agentKeys.lists(),
    queryFn: () => aiAgentService.getAll(),
    ...options,
  });
};

export const useAiAgent = (
  id: string,
  options?: Omit<UseQueryOptions<Agent>, "queryKey" | "queryFn">
) => {
  return useQuery({
    queryKey: agentKeys.detail(id),
    queryFn: () => aiAgentService.getById(id),
    enabled: !!id,
    ...options,
  });
};

export const useChat = () => {
  return useMutation({
    mutationFn: ({ agentId, request }: { agentId: string; request: ChatRequest }) =>
      aiAgentService.chat(agentId, request),
  });
};

export const useChatStream = () => {
  const streamChat = async function* (
    agentId: string,
    request: ChatRequest
  ): AsyncGenerator<string, void, unknown> {
    yield* aiAgentService.chatStream(agentId, request);
  };
  
  return { streamChat };
};

export const useChatState = (agentId: string) => {
  const chat = useChat();
  
  const sendMessage = async (message: string, history: any[] = []) => {
    const request: ChatRequest = { message, history };
    return chat.mutateAsync({ agentId, request });
  };
  
  return {
    sendMessage,
    isLoading: chat.isPending,
    error: chat.error,
    data: chat.data,
  };
};
''',

    # ============================================================
    # 9. useSimulations Hook
    # ============================================================
    "hooks/useSimulations.ts": '''/**
 * ============================================================================
 *  useSimulations — React Query hooks for simulation operations
 * ============================================================================
 */

import {
  useQuery,
  useMutation,
  useQueryClient,
  UseQueryOptions,
} from "@tanstack/react-query";
import {
  simulationService,
  Simulation,
  SimulationRunRequest,
  SimulationResult,
} from "@/services/simulationService";

export const simulationKeys = {
  all: ["simulations"] as const,
  lists: () => [...simulationKeys.all, "list"] as const,
  details: () => [...simulationKeys.all, "detail"] as const,
  detail: (id: string) => [...simulationKeys.details(), id] as const,
  results: (id: string) => [...simulationKeys.detail(id), "result"] as const,
};

export const useSimulations = (
  options?: Omit<UseQueryOptions<Simulation[]>, "queryKey" | "queryFn">
) => {
  return useQuery({
    queryKey: simulationKeys.lists(),
    queryFn: () => simulationService.getAll(),
    ...options,
  });
};

export const useSimulation = (
  id: string,
  options?: Omit<UseQueryOptions<Simulation>, "queryKey" | "queryFn">
) => {
  return useQuery({
    queryKey: simulationKeys.detail(id),
    queryFn: () => simulationService.getById(id),
    enabled: !!id,
    ...options,
  });
};

export const useSimulationResult = (
  id: string,
  options?: Omit<UseQueryOptions<SimulationResult>, "queryKey" | "queryFn">
) => {
  return useQuery({
    queryKey: simulationKeys.results(id),
    queryFn: () => simulationService.getResult(id),
    enabled: !!id,
    ...options,
  });
};

export const useRunSimulation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (request: SimulationRunRequest) =>
      simulationService.run(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: simulationKeys.lists() });
    },
  });
};

export const useCancelSimulation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => simulationService.cancel(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: simulationKeys.detail(id) });
    },
  });
};

export const useDeleteSimulation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => simulationService.delete(id),
    onSuccess: (_, id) => {
      queryClient.removeQueries({ queryKey: simulationKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: simulationKeys.lists() });
    },
  });
};

export const useSimulationPolling = (
  id: string,
  options: { enabled?: boolean; interval?: number } = {}
) => {
  const { enabled = true, interval = 2000 } = options;
  
  return useQuery({
    queryKey: simulationKeys.detail(id),
    queryFn: () => simulationService.getById(id),
    enabled: enabled && !!id,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (!data) return false;
      if (data.status === "completed" || data.status === "failed") return false;
      return interval;
    },
  });
};
''',

    # ============================================================
    # 10. API Types
    # ============================================================
    "types/api.ts": '''/**
 * ============================================================================
 *  API Types — Type definitions for API responses
 * ============================================================================
 */

export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: "success" | "error";
}

export interface ApiPaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface ApiError {
  statusCode: number;
  error: string;
  message: string;
  detail?: string | Record<string, any>;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface AuthResponse {
  accessToken: string;
  refreshToken?: string;
  tokenType: string;
  expiresIn: number;
}

export interface MeResponse {
  id: string | number;
  email: string;
  full_name?: string;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
  role?: string;
  email_verified?: boolean;
}

export interface UserCreateRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface UserUpdateRequest {
  email?: string;
  full_name?: string;
  is_active?: boolean;
}

export interface AgentChatRequest {
  message: string;
  history?: Array<{
    role: "user" | "assistant" | "system";
    content: string;
  }>;
  context?: Record<string, any>;
}

export interface AgentChatResponse {
  response: string;
  agent_id: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface SimulationRunRequest {
  type: string;
  parameters: Record<string, any>;
  name?: string;
}

export interface SimulationResponse {
  id: string;
  type: string;
  status: "pending" | "running" | "completed" | "failed";
  parameters: Record<string, any>;
  results?: Record<string, any>;
  created_at: string;
  completed_at?: string;
}

export interface HealthCheckResponse {
  status: "healthy" | "degraded" | "unhealthy";
  timestamp: number;
  version: string;
  modules: Record<string, string>;
}
''',
}

# ============================================================
# Files to Rewrite
# ============================================================

REWRITE_FILES = {
    "services/authService.ts": '''/**
 * ============================================================================
 *  authService — typed API client for authentication endpoints
 * ============================================================================
 * 
 * بازنویسی شده برای استفاده از api-client جدید
 */

import { apiClient } from "@/lib/api-client";
import type {
  ApiError,
  AuthCredentials,
  AuthSession,
  ForgotPasswordRequest,
  MeResponse,
  RegisterPayload,
  ResetPasswordRequest,
  User,
} from "@/types";
import { API_ENDPOINTS } from "@/types/api";

// ---------------------------------------------------------------------------
// Token storage (SSR-safe)
// ---------------------------------------------------------------------------

const TOKEN_STORAGE_KEY = "econojin.access_token";
const REFRESH_TOKEN_STORAGE_KEY = "econojin.refresh_token";

export const tokenStorage = {
  getAccessToken(): string | null {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem(TOKEN_STORAGE_KEY);
  },
  getRefreshToken(): string | null {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY);
  },
  set(session: AuthSession): void {
    if (typeof window === "undefined") return;
    window.localStorage.setItem(TOKEN_STORAGE_KEY, session.accessToken);
    if (session.refreshToken) {
      window.localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, session.refreshToken);
    }
  },
  clear(): void {
    if (typeof window === "undefined") return;
    window.localStorage.removeItem(TOKEN_STORAGE_KEY);
    window.localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY);
  },
} as const;

// ---------------------------------------------------------------------------
// Public auth API
// ---------------------------------------------------------------------------

export async function login(credentials: AuthCredentials): Promise<AuthSession> {
  const response = await apiClient.post<AuthSession>(
    API_ENDPOINTS.auth.login,
    credentials
  );
  tokenStorage.set(response.data);
  return response.data;
}

export async function register(payload: RegisterPayload): Promise<AuthSession> {
  const response = await apiClient.post<AuthSession>(
    API_ENDPOINTS.auth.register,
    payload
  );
  tokenStorage.set(response.data);
  return response.data;
}

export async function logout(): Promise<void> {
  try {
    await apiClient.post(API_ENDPOINTS.auth.logout);
  } catch {
    // Even if the server call fails, clear locally.
  } finally {
    tokenStorage.clear();
  }
}

export async function getCurrentUser(): Promise<User> {
  const response = await apiClient.get<MeResponse>(API_ENDPOINTS.auth.me);
  const me = response.data;
  
  return {
    id: (me as any).id ?? "",
    email: (me as any).email ?? "",
    username: (me as any).username ?? (me as any).email ?? "",
    displayName: (me as any).displayName ?? (me as any).full_name ?? (me as any).email ?? "",
    status: (me as any).status ?? "active",
    createdAt: (me as any).createdAt ?? new Date().toISOString(),
    updatedAt: (me as any).updatedAt ?? new Date().toISOString(),
    is_active: (me as any).is_active ?? true,
    role: (me as any).role ?? "user",
    emailVerified: (me as any).emailVerified ?? (me as any).email_verified ?? false,
  } as User;
}

export async function forgotPassword(payload: ForgotPasswordRequest): Promise<void> {
  await apiClient.post(API_ENDPOINTS.auth.forgotPassword, payload);
}

export async function resetPassword(payload: ResetPasswordRequest): Promise<void> {
  await apiClient.post(API_ENDPOINTS.auth.resetPassword, payload);
}

export async function refreshSession(): Promise<AuthSession> {
  const refreshToken = tokenStorage.getRefreshToken();
  if (!refreshToken) {
    throw {
      statusCode: 401,
      error: "Unauthorized",
      message: "auth.sessionExpired",
    } as ApiError;
  }
  
  const response = await apiClient.post<AuthSession>(
    API_ENDPOINTS.auth.refresh,
    { refreshToken }
  );
  tokenStorage.set(response.data);
  return response.data;
}
''',

    "hooks/useAuth.ts": '''/**
 * ============================================================================
 *  useAuth — React Query hooks for authentication
 * ============================================================================
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  login,
  register,
  logout,
  getCurrentUser,
} from "@/services/authService";
import type { AuthCredentials, RegisterPayload, User } from "@/types";

export const authKeys = {
  all: ["auth"] as const,
  currentUser: () => [...authKeys.all, "currentUser"] as const,
};

export const useAuth = () => {
  return useQuery<User | null>({
    queryKey: authKeys.currentUser(),
    queryFn: async () => {
      try {
        return await getCurrentUser();
      } catch {
        return null;
      }
    },
    staleTime: 1000 * 60 * 5,
    retry: false,
  });
};

export const useLogin = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (credentials: AuthCredentials) => login(credentials),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: authKeys.currentUser() });
    },
  });
};

export const useRegister = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (payload: RegisterPayload) => register(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: authKeys.currentUser() });
    },
  });
};

export const useLogout = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: logout,
    onSuccess: () => {
      queryClient.clear();
    },
  });
};
''',
}

# ============================================================
# Main Logic
# ============================================================

def main():
    print("\n" + "=" * 70)
    print("🚀 Eco Nojin - Phase 4 File Creator")
    print("=" * 70)
    
    if not SRC_DIR.exists():
        print(f"\n❌ src/ not found: {SRC_DIR}")
        sys.exit(1)
    
    print(f"\n📂 Source directory: {SRC_DIR}")
    
    # Backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = PROJECT_ROOT / ".backups" / f"phase4_files_{timestamp}"
    
    print(f"\n💾 Creating backup at: {backup_dir}")
    try:
        backup_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(SRC_DIR, backup_dir)
        print(f"   ✅ Backup created")
    except Exception as e:
        print(f"   ⚠️  Backup failed: {e}")
    
    # Create new files
    print(f"\n📝 Creating {len(NEW_FILES)} new files...")
    created = 0
    
    for rel_path, content in NEW_FILES.items():
        file_path = SRC_DIR / rel_path
        
        if file_path.exists():
            print(f"   ⏩ {rel_path}: already exists")
            continue
        
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            print(f"   ✅ {rel_path}")
            created += 1
        except Exception as e:
            print(f"   ❌ {rel_path}: {e}")
    
    # Rewrite files
    print(f"\n✏️  Rewriting {len(REWRITE_FILES)} existing files...")
    rewritten = 0
    
    for rel_path, content in REWRITE_FILES.items():
        file_path = SRC_DIR / rel_path
        
        if not file_path.exists():
            print(f"   ❌ {rel_path}: not found")
            continue
        
        try:
            # Backup original
            backup_file = file_path.with_suffix(file_path.suffix + ".backup")
            shutil.copy2(file_path, backup_file)
            
            # Write new content
            file_path.write_text(content, encoding="utf-8")
            print(f"   ✅ {rel_path} (backup: {backup_file.name})")
            rewritten += 1
        except Exception as e:
            print(f"   ❌ {rel_path}: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print(f"✅ Phase 4 File Creator completed!")
    print(f"   📝 Created: {created}")
    print(f"   ✏️  Rewritten: {rewritten}")
    print("=" * 70)
    
    print("\n📌 Next steps:")
    print("   1. Build: cd apps/web && pnpm build")
    print("   2. Dev server: cd apps/web && pnpm dev")
    print("   3. Commit: git add . && git commit -m 'feat(phase-4): integration'")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  Stopped")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)