#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eco Nojin - Phase 4: Frontend-Backend Integration Setup
========================================================
ایجاد خودکار ۱۳ فایل برای یکپارچه‌سازی فرانت‌اند با بک‌اند

فایل‌های ایجاد شده:
✅ زیرساخت API (۳ فایل):
   - src/lib/api-client.ts
   - src/lib/query-client.ts
   - src/lib/api-errors.ts

✅ Service Layer (۳ فایل جدید):
   - src/services/userService.ts
   - src/services/aiAgentService.ts
   - src/services/simulationService.ts

✅ React Query Hooks (۳ فایل جدید):
   - src/hooks/useUsers.ts
   - src/hooks/useAiAgents.ts
   - src/hooks/useSimulations.ts

✅ Types (۱ فایل):
   - src/types/api.ts

✏️ بازنویسی (۲ فایل):
   - src/services/authService.ts
   - src/hooks/useAuth.ts

📦 نصب dependencies:
   - axios
   - @tanstack/react-query
   - @tanstack/react-query-devtools

نحوه اجرا:
    python scripts/integration/phase4_setup.py
    python scripts/integration/phase4_setup.py --dry-run
    python scripts/integration/phase4_setup.py --backup

نویسنده: Eco Nojin Architecture Team
نسخه: 4.0.0
"""

import sys
import subprocess
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import logging

# ============================================================
# Configuration
# ============================================================

VERSION = "4.0.0"
PROJECT_NAME = "Eco Nojin"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phase4_integration.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================
# Data Models
# ============================================================

@dataclass
class FileAction:
    path: Path
    action: str  # create, rewrite, skip
    status: str = "pending"
    details: str = ""

@dataclass
class Phase4Report:
    timestamp: str
    dry_run: bool
    backup_path: Optional[Path] = None
    files: List[FileAction] = field(default_factory=list)
    dependencies_installed: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    @property
    def total_created(self) -> int:
        return len([f for f in self.files if f.action == "create" and f.status == "done"])
    
    @property
    def total_rewritten(self) -> int:
        return len([f for f in self.files if f.action == "rewrite" and f.status == "done"])
    
    @property
    def total_failed(self) -> int:
        return len([f for f in self.files if f.status == "failed"])

# ============================================================
# Colors
# ============================================================

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'

def cprint(msg: str, color: str = Colors.END):
    print(f"{color}{msg}{Colors.END}")

# ============================================================
# File Contents (با تحقیق دقیق)
# ============================================================

FILE_CONTENTS = {
    # ============================================================
    # 1. API Client (Axios Instance)
    # ============================================================
    "src/lib/api-client.ts": '''/**
 * ============================================================================
 *  API Client — Axios instance with interceptors
 * ============================================================================
 * 
 * این فایل یک singleton Axios instance ایجاد می‌کند که:
 * - Base URL را از environment variables می‌خواند
 * - Token احراز هویت را به صورت خودکار اضافه می‌کند
 * - خطاهای 401 را مدیریت می‌کند (redirect به login)
 * - Timeout و retry policy دارد
 * 
 * @module api-client
 */

import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from "axios";
import { tokenStorage } from "@/services/authService";

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const API_BASE_URL: string =
  (import.meta.env["VITE_API_BASE_URL"] as string | undefined) ??
  "http://localhost:8000";

const API_TIMEOUT = 30000; // 30 seconds
const MAX_RETRIES = 2;

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
  (error: AxiosError) => {
    return Promise.reject(error);
  }
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
    
    // Handle 401 Unauthorized
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Queue the request while refreshing
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
        // Try to refresh token
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
        
        // Update tokens
        tokenStorage.set({
          accessToken,
          refreshToken: newRefreshToken,
        });
        
        // Retry original request
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${accessToken}`;
        }
        
        processQueue(null, accessToken);
        return apiClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError as AxiosError, null);
        
        // Clear tokens and redirect to login
        tokenStorage.clear();
        
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
        
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }
    
    // Handle other errors
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
    # 2. Query Client (React Query)
    # ============================================================
    "src/lib/query-client.ts": '''/**
 * ============================================================================
 *  Query Client — React Query configuration
 * ============================================================================
 * 
 * این فایل QueryClient را با تنظیمات بهینه برای پروژه پیکربندی می‌کند:
 * - Stale time: 5 دقیقه (cache duration)
 * - Retry: 2 بار برای خطاهای شبکه
 * - Refetch on window focus: غیرفعال
 * - DevTools: فقط در development
 * 
 * @module query-client
 */

import { QueryClient } from "@tanstack/react-query";

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const isDevelopment = import.meta.env.DEV;

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Cache data for 5 minutes
      staleTime: 1000 * 60 * 5,
      
      // Garbage collect after 10 minutes
      gcTime: 1000 * 60 * 10,
      
      // Retry failed queries 2 times
      retry: (failureCount, error: any) => {
        // Don't retry on 401, 403, 404
        if (error?.response?.status === 401) return false;
        if (error?.response?.status === 403) return false;
        if (error?.response?.status === 404) return false;
        
        return failureCount < 2;
      },
      
      // Don't refetch on window focus
      refetchOnWindowFocus: false,
      
      // Refetch on reconnect
      refetchOnReconnect: true,
      
      // Refetch interval for real-time data (optional)
      // refetchInterval: false,
    },
    mutations: {
      // Retry mutations once
      retry: 1,
    },
  },
});

// ---------------------------------------------------------------------------
// DevTools (only in development)
// ---------------------------------------------------------------------------

if (isDevelopment) {
  // React Query DevTools will be loaded dynamically
  // See App.tsx for integration
}

export default queryClient;
''',

    # ============================================================
    # 3. API Errors
    # ============================================================
    "src/lib/api-errors.ts": '''/**
 * ============================================================================
 *  API Errors — Structured error handling
 * ============================================================================
 * 
 * این فایل کلاس‌ها و توابع کمکی برای مدیریت خطاهای API را تعریف می‌کند.
 * 
 * @module api-errors
 */

import { AxiosError } from "axios";

// ---------------------------------------------------------------------------
// Error Types
// ---------------------------------------------------------------------------

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
    
    // Maintains proper stack trace
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, ApiError);
    }
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
  
  isForbidden(): boolean {
    return this.statusCode === 403;
  }
  
  isNotFound(): boolean {
    return this.statusCode === 404;
  }
  
  isValidationError(): boolean {
    return this.statusCode === 422;
  }
  
  isServerError(): boolean {
    return this.statusCode >= 500;
  }
}

// ---------------------------------------------------------------------------
// Error Handlers
// ---------------------------------------------------------------------------

export const handleApiError = (error: unknown): ApiError => {
  if (error instanceof ApiError) {
    return error;
  }
  
  if (error instanceof AxiosError) {
    return ApiError.fromAxiosError(error);
  }
  
  if (error instanceof Error) {
    return new ApiError(error.message);
  }
  
  return new ApiError("An unknown error occurred");
};

export const getErrorMessage = (error: unknown): string => {
  const apiError = handleApiError(error);
  
  // Validation errors
  if (apiError.isValidationError() && typeof apiError.detail === "object") {
    const errors = Object.values(apiError.detail).flat();
    return errors.join(", ");
  }
  
  return apiError.message;
};

export const isNetworkError = (error: unknown): boolean => {
  return handleApiError(error).isNetworkError();
};

export default ApiError;
''',

    # ============================================================
    # 4. User Service
    # ============================================================
    "src/services/userService.ts": '''/**
 * ============================================================================
 *  User Service — CRUD operations for users
 * ============================================================================
 * 
 * این فایل تمام عملیات مرتبط با کاربران را مدیریت می‌کند:
 * - لیست کاربران
 * - دریافت کاربر
 * - ایجاد کاربر
 * - به‌روزرسانی کاربر
 * - حذف کاربر
 * 
 * @module userService
 */

import { apiClient } from "@/lib/api-client";
import type { User } from "@/types";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// API Endpoints
// ---------------------------------------------------------------------------

const ENDPOINTS = {
  users: "/users",
  userById: (id: number | string) => `/users/${id}`,
} as const;

// ---------------------------------------------------------------------------
// Service Functions
// ---------------------------------------------------------------------------

export const userService = {
  /**
   * دریافت لیست کاربران
   */
  async getAll(params?: { page?: number; pageSize?: number }): Promise<UserListResponse> {
    const response = await apiClient.get<UserListResponse>(ENDPOINTS.users, { params });
    return response.data;
  },
  
  /**
   * دریافت کاربر با ID
   */
  async getById(id: number | string): Promise<User> {
    const response = await apiClient.get<User>(ENDPOINTS.userById(id));
    return response.data;
  },
  
  /**
   * ایجاد کاربر جدید
   */
  async create(data: UserCreate): Promise<User> {
    const response = await apiClient.post<User>(ENDPOINTS.users, data);
    return response.data;
  },
  
  /**
   * به‌روزرسانی کاربر
   */
  async update(id: number | string, data: UserUpdate): Promise<User> {
    const response = await apiClient.put<User>(ENDPOINTS.userById(id), data);
    return response.data;
  },
  
  /**
   * حذف کاربر
   */
  async delete(id: number | string): Promise<void> {
    await apiClient.delete(ENDPOINTS.userById(id));
  },
  
  /**
   * جستجوی کاربر با email
   */
  async searchByEmail(email: string): Promise<User | null> {
    try {
      const response = await apiClient.get<User>(ENDPOINTS.users, {
        params: { email },
      });
      return response.data;
    } catch {
      return null;
    }
  },
};

export default userService;
''',

    # ============================================================
    # 5. AI Agent Service
    # ============================================================
    "src/services/aiAgentService.ts": '''/**
 * ============================================================================
 *  AI Agent Service — Chat and agent operations
 * ============================================================================
 * 
 * این فایل عملیات مرتبط با AI Agents را مدیریت می‌کند:
 * - لیست agents
 * - چت با agent
 * - چت streaming
 * 
 * @module aiAgentService
 */

import { apiClient } from "@/lib/api-client";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// API Endpoints
// ---------------------------------------------------------------------------

const ENDPOINTS = {
  agents: "/ai-agents",
  agentById: (id: string) => `/ai-agents/${id}`,
  chat: (id: string) => `/ai-agents/${id}/chat`,
  chatStream: (id: string) => `/ai-agents/${id}/chat/stream`,
} as const;

// ---------------------------------------------------------------------------
// Service Functions
// ---------------------------------------------------------------------------

export const aiAgentService = {
  /**
   * دریافت لیست agents
   */
  async getAll(): Promise<Agent[]> {
    const response = await apiClient.get<Agent[]>(ENDPOINTS.agents);
    return response.data;
  },
  
  /**
   * دریافت agent با ID
   */
  async getById(id: string): Promise<Agent> {
    const response = await apiClient.get<Agent>(ENDPOINTS.agentById(id));
    return response.data;
  },
  
  /**
   * چت با agent
   */
  async chat(agentId: string, request: ChatRequest): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>(
      ENDPOINTS.chat(agentId),
      request
    );
    return response.data;
  },
  
  /**
   * چت streaming با agent
   * Returns an async generator for streaming responses
   */
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
    if (!reader) {
      throw new Error("Response body is not readable");
    }
    
    const decoder = new TextDecoder();
    
    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        
        // Parse Server-Sent Events (SSE)
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
  
  /**
   * دریافت capabilities یک agent
   */
  async getCapabilities(agentId: string): Promise<string[]> {
    const agent = await this.getById(agentId);
    return agent.capabilities;
  },
};

export default aiAgentService;
''',

    # ============================================================
    # 6. Simulation Service
    # ============================================================
    "src/services/simulationService.ts": '''/**
 * ============================================================================
 *  Simulation Service — Run and manage simulations
 * ============================================================================
 * 
 * این فایل عملیات مرتبط با شبیه‌سازی‌ها را مدیریت می‌کند:
 * - لیست شبیه‌سازی‌ها
 * - اجرای شبیه‌سازی
 * - دریافت نتایج
 * 
 * @module simulationService
 */

import { apiClient } from "@/lib/api-client";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// API Endpoints
// ---------------------------------------------------------------------------

const ENDPOINTS = {
  simulations: "/simulations",
  simulationById: (id: string) => `/simulations/${id}`,
  run: "/simulations/run",
  result: (id: string) => `/simulations/${id}/result`,
} as const;

// ---------------------------------------------------------------------------
// Service Functions
// ---------------------------------------------------------------------------

export const simulationService = {
  /**
   * دریافت لیست شبیه‌سازی‌ها
   */
  async getAll(): Promise<Simulation[]> {
    const response = await apiClient.get<Simulation[]>(ENDPOINTS.simulations);
    return response.data;
  },
  
  /**
   * دریافت شبیه‌سازی با ID
   */
  async getById(id: string): Promise<Simulation> {
    const response = await apiClient.get<Simulation>(ENDPOINTS.simulationById(id));
    return response.data;
  },
  
  /**
   * اجرای شبیه‌سازی
   */
  async run(request: SimulationRunRequest): Promise<Simulation> {
    const response = await apiClient.post<Simulation>(ENDPOINTS.run, request);
    return response.data;
  },
  
  /**
   * دریافت نتایج شبیه‌سازی
   */
  async getResult(id: string): Promise<SimulationResult> {
    const response = await apiClient.get<SimulationResult>(ENDPOINTS.result(id));
    return response.data;
  },
  
  /**
   * لغو شبیه‌سازی در حال اجرا
   */
  async cancel(id: string): Promise<void> {
    await apiClient.post(`${ENDPOINTS.simulationById(id)}/cancel`);
  },
  
  /**
   * حذف شبیه‌سازی
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(ENDPOINTS.simulationById(id));
  },
  
  /**
   * Polling برای وضعیت شبیه‌سازی
   */
  async waitForCompletion(
    id: string,
    options: { interval?: number; timeout?: number } = {}
  ): Promise<Simulation> {
    const { interval = 2000, timeout = 60000 } = options;
    const startTime = Date.now();
    
    while (Date.now() - startTime < timeout) {
      const simulation = await this.getById(id);
      
      if (simulation.status === "completed" || simulation.status === "failed") {
        return simulation;
      }
      
      await new Promise((resolve) => setTimeout(resolve, interval));
    }
    
    throw new Error("Simulation timeout");
  },
};

export default simulationService;
''',

    # ============================================================
    # 7. useUsers Hook
    # ============================================================
    "src/hooks/useUsers.ts": '''/**
 * ============================================================================
 *  useUsers — React Query hooks for user operations
 * ============================================================================
 * 
 * این فایل hooks مرتبط با کاربران را تعریف می‌کند:
 * - useUsers: لیست کاربران
 * - useUser: یک کاربر
 * - useCreateUser: ایجاد کاربر
 * - useUpdateUser: به‌روزرسانی کاربر
 * - useDeleteUser: حذف کاربر
 * 
 * @module useUsers
 */

import {
  useQuery,
  useMutation,
  useQueryClient,
  UseQueryOptions,
} from "@tanstack/react-query";
import { userService, UserCreate, UserUpdate } from "@/services/userService";
import type { User } from "@/types";

// ---------------------------------------------------------------------------
// Query Keys
// ---------------------------------------------------------------------------

export const userKeys = {
  all: ["users"] as const,
  lists: () => [...userKeys.all, "list"] as const,
  list: (params: Record<string, any>) => [...userKeys.lists(), params] as const,
  details: () => [...userKeys.all, "detail"] as const,
  detail: (id: number | string) => [...userKeys.details(), id] as const,
};

// ---------------------------------------------------------------------------
// Queries
// ---------------------------------------------------------------------------

/**
 * Hook برای دریافت لیست کاربران
 */
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

/**
 * Hook برای دریافت یک کاربر
 */
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

// ---------------------------------------------------------------------------
// Mutations
// ---------------------------------------------------------------------------

/**
 * Hook برای ایجاد کاربر
 */
export const useCreateUser = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: UserCreate) => userService.create(data),
    onSuccess: () => {
      // Invalidate users list
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
    },
  });
};

/**
 * Hook برای به‌روزرسانی کاربر
 */
export const useUpdateUser = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number | string; data: UserUpdate }) =>
      userService.update(id, data),
    onSuccess: (data, variables) => {
      // Update user in cache
      queryClient.setQueryData(userKeys.detail(variables.id), data);
      // Invalidate users list
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
    },
  });
};

/**
 * Hook برای حذف کاربر
 */
export const useDeleteUser = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number | string) => userService.delete(id),
    onSuccess: (_, id) => {
      // Remove user from cache
      queryClient.removeQueries({ queryKey: userKeys.detail(id) });
      // Invalidate users list
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
    },
  });
};
''',

    # ============================================================
    # 8. useAiAgents Hook
    # ============================================================
    "src/hooks/useAiAgents.ts": '''/**
 * ============================================================================
 *  useAiAgents — React Query hooks for AI agent operations
 * ============================================================================
 * 
 * این فایل hooks مرتبط با AI Agents را تعریف می‌کند:
 * - useAiAgents: لیست agents
 * - useAiAgent: یک agent
 * - useChat: چت با agent
 * - useChatStream: چت streaming
 * 
 * @module useAiAgents
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
  ChatResponse,
} from "@/services/aiAgentService";

// ---------------------------------------------------------------------------
// Query Keys
// ---------------------------------------------------------------------------

export const agentKeys = {
  all: ["agents"] as const,
  lists: () => [...agentKeys.all, "list"] as const,
  details: () => [...agentKeys.all, "detail"] as const,
  detail: (id: string) => [...agentKeys.details(), id] as const,
};

// ---------------------------------------------------------------------------
// Queries
// ---------------------------------------------------------------------------

/**
 * Hook برای دریافت لیست agents
 */
export const useAiAgents = (
  options?: Omit<UseQueryOptions<Agent[]>, "queryKey" | "queryFn">
) => {
  return useQuery({
    queryKey: agentKeys.lists(),
    queryFn: () => aiAgentService.getAll(),
    ...options,
  });
};

/**
 * Hook برای دریافت یک agent
 */
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

// ---------------------------------------------------------------------------
// Mutations
// ---------------------------------------------------------------------------

/**
 * Hook برای چت با agent
 */
export const useChat = () => {
  return useMutation({
    mutationFn: ({ agentId, request }: { agentId: string; request: ChatRequest }) =>
      aiAgentService.chat(agentId, request),
  });
};

/**
 * Hook برای چت streaming
 * Returns a function that can be called to start streaming
 */
export const useChatStream = () => {
  const streamChat = async function* (
    agentId: string,
    request: ChatRequest
  ): AsyncGenerator<string, void, unknown> {
    yield* aiAgentService.chatStream(agentId, request);
  };
  
  return { streamChat };
};

/**
 * Helper hook برای مدیریت chat state
 */
export const useChatState = (agentId: string) => {
  const chat = useChat();
  
  const sendMessage = async (message: string, history: any[] = []) => {
    const request: ChatRequest = {
      message,
      history,
    };
    
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
    "src/hooks/useSimulations.ts": '''/**
 * ============================================================================
 *  useSimulations — React Query hooks for simulation operations
 * ============================================================================
 * 
 * این فایل hooks مرتبط با شبیه‌سازی‌ها را تعریف می‌کند:
 * - useSimulations: لیست شبیه‌سازی‌ها
 * - useSimulation: یک شبیه‌سازی
 * - useRunSimulation: اجرای شبیه‌سازی
 * - useSimulationResult: نتایج شبیه‌سازی
 * 
 * @module useSimulations
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

// ---------------------------------------------------------------------------
// Query Keys
// ---------------------------------------------------------------------------

export const simulationKeys = {
  all: ["simulations"] as const,
  lists: () => [...simulationKeys.all, "list"] as const,
  details: () => [...simulationKeys.all, "detail"] as const,
  detail: (id: string) => [...simulationKeys.details(), id] as const,
  results: (id: string) => [...simulationKeys.detail(id), "result"] as const,
};

// ---------------------------------------------------------------------------
// Queries
// ---------------------------------------------------------------------------

/**
 * Hook برای دریافت لیست شبیه‌سازی‌ها
 */
export const useSimulations = (
  options?: Omit<UseQueryOptions<Simulation[]>, "queryKey" | "queryFn">
) => {
  return useQuery({
    queryKey: simulationKeys.lists(),
    queryFn: () => simulationService.getAll(),
    ...options,
  });
};

/**
 * Hook برای دریافت یک شبیه‌سازی
 */
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

/**
 * Hook برای دریافت نتایج شبیه‌سازی
 */
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

// ---------------------------------------------------------------------------
// Mutations
// ---------------------------------------------------------------------------

/**
 * Hook برای اجرای شبیه‌سازی
 */
export const useRunSimulation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (request: SimulationRunRequest) =>
      simulationService.run(request),
    onSuccess: () => {
      // Invalidate simulations list
      queryClient.invalidateQueries({ queryKey: simulationKeys.lists() });
    },
  });
};

/**
 * Hook برای لغو شبیه‌سازی
 */
export const useCancelSimulation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => simulationService.cancel(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: simulationKeys.detail(id) });
    },
  });
};

/**
 * Hook برای حذف شبیه‌سازی
 */
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

/**
 * Hook برای polling وضعیت شبیه‌سازی
 */
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
    "src/types/api.ts": '''/**
 * ============================================================================
 *  API Types — Type definitions for API responses
 * ============================================================================
 * 
 * این فایل type های مرتبط با API responses را تعریف می‌کند.
 * این types با FastAPI backend سازگار هستند.
 * 
 * @module api-types
 */

// ---------------------------------------------------------------------------
// Generic API Response Types
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// Auth Types
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// User Types
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// AI Agent Types
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// Simulation Types
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// Health Check Types
// ---------------------------------------------------------------------------

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
    "src/services/authService.ts": '''/**
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
  
  // Transform MeResponse to User type
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

    "src/hooks/useAuth.ts": '''/**
 * ============================================================================
 *  useAuth — React Query hooks for authentication
 * ============================================================================
 * 
 * بازنویسی شده برای استفاده از React Query
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  login,
  register,
  logout,
  getCurrentUser,
} from "@/services/authService";
import type { AuthCredentials, RegisterPayload, User } from "@/types";

// ---------------------------------------------------------------------------
// Query Keys
// ---------------------------------------------------------------------------

export const authKeys = {
  all: ["auth"] as const,
  currentUser: () => [...authKeys.all, "currentUser"] as const,
};

// ---------------------------------------------------------------------------
// Queries
// ---------------------------------------------------------------------------

/**
 * Hook برای دریافت کاربر فعلی
 */
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
    staleTime: 1000 * 60 * 5, // 5 minutes
    retry: false,
  });
};

// ---------------------------------------------------------------------------
// Mutations
// ---------------------------------------------------------------------------

/**
 * Hook برای login
 */
export const useLogin = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (credentials: AuthCredentials) => login(credentials),
    onSuccess: () => {
      // Invalidate current user query
      queryClient.invalidateQueries({ queryKey: authKeys.currentUser() });
    },
  });
};

/**
 * Hook برای register
 */
export const useRegister = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (payload: RegisterPayload) => register(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: authKeys.currentUser() });
    },
  });
};

/**
 * Hook برای logout
 */
export const useLogout = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: logout,
    onSuccess: () => {
      // Clear all queries
      queryClient.clear();
    },
  });
};
''',
}

# ============================================================
# Phase 4 Setup Class
# ============================================================

class Phase4Setup:
    def __init__(self, project_root: Path, dry_run: bool = False, backup: bool = True):
        self.project_root = project_root
        self.web_dir = project_root / "apps" / "web"
        self.src_dir = self.web_dir / "src"
        self.dry_run = dry_run
        self.backup = backup
        self.backup_path: Optional[Path] = None
        self.report = Phase4Report(
            timestamp=datetime.now().isoformat(),
            dry_run=dry_run
        )
    
    def execute(self) -> Phase4Report:
        cprint("\n" + "=" * 70, Colors.BOLD)
        cprint(f"🚀 {PROJECT_NAME} - Phase 4: Frontend-Backend Integration v{VERSION}", Colors.BOLD)
        cprint(f"   Mode: {'DRY RUN' if self.dry_run else 'LIVE'}", Colors.YELLOW if self.dry_run else Colors.GREEN)
        cprint("=" * 70, Colors.BOLD)
        
        try:
            # Step 0: Pre-flight checks
            self._pre_flight_checks()
            
            # Step 1: Backup
            if self.backup and not self.dry_run:
                self._create_backup()
            
            # Step 2: Install dependencies
            self._install_dependencies()
            
            # Step 3: Create new files
            self._create_files()
            
            # Step 4: Rewrite existing files
            self._rewrite_files()
            
            # Step 5: Update .env.example
            self._update_env_example()
            
            # Step 6: Print report
            self._print_report()
            
        except Exception as e:
            logger.error(f"❌ Critical error: {e}")
            self.report.errors.append(str(e))
            import traceback
            traceback.print_exc()
        
        return self.report
    
    def _pre_flight_checks(self):
        cprint("\n🔍 Step 0: Pre-flight checks...", Colors.BLUE)
        
        if not self.src_dir.exists():
            raise FileNotFoundError(f"src/ not found: {self.src_dir}")
        
        cprint(f"   ✅ src/ found: {self.src_dir}", Colors.GREEN)
        
        # Check if package.json exists
        package_json = self.web_dir / "package.json"
        if not package_json.exists():
            raise FileNotFoundError(f"package.json not found: {package_json}")
        
        cprint(f"   ✅ package.json found", Colors.GREEN)
    
    def _create_backup(self):
        cprint("\n💾 Step 1: Creating backup...", Colors.BLUE)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_path = self.project_root / ".backups" / f"phase4_backup_{timestamp}"
        
        try:
            self.backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(self.src_dir, self.backup_path)
            self.report.backup_path = self.backup_path
            cprint(f"   ✅ Backup created: {self.backup_path}", Colors.GREEN)
        except Exception as e:
            cprint(f"   ⚠️  Backup failed: {e}", Colors.YELLOW)
    
    def _install_dependencies(self):
        cprint("\n📦 Step 2: Installing dependencies...", Colors.BLUE)
        
        deps = [
            "axios",
            "@tanstack/react-query",
            "@tanstack/react-query-devtools",
        ]
        
        if self.dry_run:
            for dep in deps:
                cprint(f"   🔍 [DRY RUN] Would install: {dep}", Colors.CYAN)
                self.report.dependencies_installed.append(dep)
            return
        
        try:
            for dep in deps:
                cprint(f"   📦 Installing: {dep}...", Colors.DIM)
                result = subprocess.run(
                    ["pnpm", "add", dep],
                    cwd=self.web_dir,
                    capture_output=True,
                    text=True,
                    check=True
                )
                cprint(f"   ✅ {dep} installed", Colors.GREEN)
                self.report.dependencies_installed.append(dep)
        except subprocess.CalledProcessError as e:
            cprint(f"   ❌ Failed to install dependencies: {e}", Colors.RED)
            self.report.errors.append(f"Dependency install failed: {e}")
    
    def _create_files(self):
        cprint("\n📝 Step 3: Creating new files...", Colors.BLUE)
        
        for rel_path, content in FILE_CONTENTS.items():
            file_path = self.src_dir / rel_path
            action = FileAction(path=file_path, action="create")
            
            if file_path.exists():
                action.status = "skipped"
                action.details = "File already exists"
                cprint(f"   ⏩ {rel_path}: already exists", Colors.DIM)
            else:
                if self.dry_run:
                    cprint(f"   🔍 [DRY RUN] Would create: {rel_path}", Colors.CYAN)
                    action.status = "pending"
                else:
                    try:
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        file_path.write_text(content, encoding="utf-8")
                        action.status = "done"
                        action.details = f"Created ({len(content)} bytes)"
                        cprint(f"   ✅ {rel_path}", Colors.GREEN)
                    except Exception as e:
                        action.status = "failed"
                        action.details = str(e)
                        cprint(f"   ❌ {rel_path}: {e}", Colors.RED)
                        self.report.errors.append(f"Create failed: {rel_path} - {e}")
            
            self.report.files.append(action)
    
    def _rewrite_files(self):
        cprint("\n✏️  Step 4: Rewriting existing files...", Colors.BLUE)
        
        for rel_path, content in REWRITE_FILES.items():
            file_path = self.src_dir / rel_path
            action = FileAction(path=file_path, action="rewrite")
            
            if not file_path.exists():
                action.status = "failed"
                action.details = "File not found"
                cprint(f"   ❌ {rel_path}: not found", Colors.RED)
                self.report.errors.append(f"Rewrite failed: {rel_path} - not found")
            else:
                if self.dry_run:
                    cprint(f"   🔍 [DRY RUN] Would rewrite: {rel_path}", Colors.CYAN)
                    action.status = "pending"
                else:
                    try:
                        # Create backup of original
                        backup_file = file_path.with_suffix(file_path.suffix + ".backup")
                        shutil.copy2(file_path, backup_file)
                        
                        # Write new content
                        file_path.write_text(content, encoding="utf-8")
                        action.status = "done"
                        action.details = f"Rewritten (backup: {backup_file.name})"
                        cprint(f"   ✅ {rel_path}", Colors.GREEN)
                    except Exception as e:
                        action.status = "failed"
                        action.details = str(e)
                        cprint(f"   ❌ {rel_path}: {e}", Colors.RED)
                        self.report.errors.append(f"Rewrite failed: {rel_path} - {e}")
            
            self.report.files.append(action)
    
    def _update_env_example(self):
        cprint("\n🔧 Step 5: Updating .env.example...", Colors.BLUE)
        
        env_example = self.web_dir / ".env.example"
        
        if not env_example.exists():
            cprint("   ⏩ .env.example not found", Colors.DIM)
            return
        
        content = env_example.read_text(encoding="utf-8")
        
        # Add API base URL if not present
        if "VITE_API_BASE_URL" not in content:
            if self.dry_run:
                cprint("   🔍 [DRY RUN] Would update .env.example", Colors.CYAN)
            else:
                with open(env_example, "a", encoding="utf-8") as f:
                    f.write("\n# Backend API Configuration\n")
                    f.write("VITE_API_BASE_URL=http://localhost:8000\n")
                cprint("   ✅ .env.example updated", Colors.GREEN)
        else:
            cprint("   ⏩ .env.example already has VITE_API_BASE_URL", Colors.DIM)
    
    def _print_report(self):
        cprint("\n" + "=" * 70, Colors.BOLD)
        cprint("📊 Final Report", Colors.BOLD)
        cprint("=" * 70, Colors.BOLD)
        
        cprint(f"\n   📦 Dependencies installed: {len(self.report.dependencies_installed)}")
        cprint(f"   📝 Files created: {self.report.total_created}")
        cprint(f"   ✏️  Files rewritten: {self.report.total_rewritten}")
        cprint(f"   ❌ Failed: {self.report.total_failed}")
        
        if self.backup_path:
            cprint(f"\n   💾 Backup: {self.backup_path}", Colors.CYAN)
        
        if self.report.errors:
            cprint(f"\n   {Colors.RED}❌ Errors:{Colors.END}")
            for error in self.report.errors:
                cprint(f"      • {error}", Colors.RED)
        
        cprint("\n" + "=" * 70, Colors.BOLD)
        
        if self.report.total_failed == 0:
            cprint("\n✅ Phase 4 setup completed successfully!", Colors.GREEN + Colors.BOLD)
            cprint("\n📌 Next steps:", Colors.BLUE)
            cprint("   1. Update .env with VITE_API_BASE_URL")
            cprint("   2. Run: cd apps/web && pnpm build")
            cprint("   3. Start backend: python -m apps.main")
            cprint("   4. Start frontend: cd apps/web && pnpm dev")
            cprint("   5. Commit: git add . && git commit -m 'feat(phase-4): add integration layer'")
            
            if self.dry_run:
                cprint("\n🔍 This was a DRY RUN. Remove --dry-run flag to execute.", Colors.YELLOW)
        else:
            cprint("\n⚠️  Some operations failed. Check errors above.", Colors.YELLOW)


# ============================================================
# Main
# ============================================================

def find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(5):
        if (current / "apps").exists():
            return current
        current = current.parent
    return Path.cwd()


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description=f"{PROJECT_NAME} - Phase 4 Setup v{VERSION}"
    )
    parser.add_argument(
        "--root", type=str, default=".",
        help="Project root path"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Dry run mode (no changes)"
    )
    parser.add_argument(
        "--no-backup", action="store_true",
        help="Skip backup creation"
    )
    
    args = parser.parse_args()
    project_root = Path(args.root).resolve()
    
    cprint(f"\n🌱 {PROJECT_NAME} Phase 4 Setup v{VERSION}", Colors.BOLD)
    cprint(f"📂 Root: {project_root}", Colors.DIM)
    
    setup = Phase4Setup(
        project_root=project_root,
        dry_run=args.dry_run,
        backup=not args.no_backup
    )
    
    report = setup.execute()
    sys.exit(1 if report.total_failed > 0 else 0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\n⏹️  Stopped", Colors.YELLOW)
        sys.exit(0)
    except Exception as e:
        cprint(f"\n❌ Unexpected error: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        sys.exit(1)