/**
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
          user: null as any,
          expiresAt: Date.now() + 3600000, // 1 hour from now
        } as any);
        
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
