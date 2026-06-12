import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { authStorage } from '@/lib/utils/storage';
import { ApiClientError, NetworkError, TimeoutError } from './errors/api.errors';
import type { ApiError, RefreshTokenResponse } from './types/auth.types';

// ============================================================================
// Request Interceptor
// ============================================================================

export function setupRequestInterceptor(apiClient: AxiosInstance): void {
  apiClient.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      // Add Authorization header if token exists
      const token = authStorage.getAccessToken();
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }

      // Add timestamp for debugging
      config.metadata = { startTime: Date.now() };

      // Log request in development
      if (process.env.NODE_ENV === 'development') {
        console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`, {
          params: config.params,
          data: config.data,
        });
      }

      return config;
    },
    (error: AxiosError) => {
      return Promise.reject(error);
    }
  );
}

// ============================================================================
// Response Interceptor
// ============================================================================

export function setupResponseInterceptor(apiClient: AxiosInstance): void {
  apiClient.interceptors.response.use(
    (response: AxiosResponse) => {
      // Log response time in development
      if (process.env.NODE_ENV === 'development' && response.config.metadata) {
        const duration = Date.now() - response.config.metadata.startTime;
        console.log(`✅ API Response: ${response.config.url} (${duration}ms)`, {
          status: response.status,
          data: response.data,
        });
      }

      return response;
    },
    async (error: AxiosError<ApiError>) => {
      const originalRequest = error.config as InternalAxiosRequestConfig & {
        _retry?: boolean;
        metadata?: { startTime: number };
      };

      // Log error in development
      if (process.env.NODE_ENV === 'development') {
        console.error(`❌ API Error: ${originalRequest?.url}`, {
          status: error.response?.status,
          data: error.response?.data,
        });
      }

      // Handle network errors
      if (!error.response) {
        if (error.code === 'ECONNABORTED') {
          return Promise.reject(new TimeoutError());
        }
        return Promise.reject(new NetworkError());
      }

      // Handle 401 Unauthorized - Try to refresh token
      if (error.response.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;

        try {
          const refreshToken = authStorage.getRefreshToken();
          
          if (!refreshToken) {
            throw new Error('No refresh token available');
          }

          // Attempt to refresh token
          const response = await apiClient.post<RefreshTokenResponse>(
            '/auth/refresh',
            { refresh_token: refreshToken }
          );

          const { access_token } = response.data;
          
          // Update stored token
          authStorage.setTokens(access_token, refreshToken);

          // Retry original request with new token
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
          }
          
          return apiClient(originalRequest);
        } catch (refreshError) {
          // Refresh failed - clear auth and redirect to login
          authStorage.clearAll();
          
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
          
          return Promise.reject(refreshError);
        }
      }

      // Handle other errors
      const errorData = error.response.data;
      
      if (errorData && errorData.detail) {
        return Promise.reject(
          new ApiClientError({
            detail: errorData.detail,
            error_code: errorData.error_code,
            status: error.response.status,
            timestamp: errorData.timestamp || new Date().toISOString(),
          })
        );
      }

      // Fallback error
      return Promise.reject(
        new ApiClientError({
          detail: error.message || 'خطای ناشناخته',
          status: error.response.status,
          timestamp: new Date().toISOString(),
        })
      );
    }
  );
}