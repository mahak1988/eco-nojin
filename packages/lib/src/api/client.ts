import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { setupRequestInterceptor, setupResponseInterceptor } from './interceptors';
import { buildUrl } from './endpoints';

// ============================================================================
// API Client Configuration
// ============================================================================

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_TIMEOUT = parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || '10000', 10);
const RETRY_ATTEMPTS = parseInt(process.env.NEXT_PUBLIC_RETRY_ATTEMPTS || '3', 10);

// ============================================================================
// API Client Class
// ============================================================================

class ApiClient {
  private client: AxiosInstance;
  private static instance: ApiClient;

  private constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: API_TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      withCredentials: true, // برای ارسال cookies در cross-origin requests
    });

    // Setup interceptors
    setupRequestInterceptor(this.client);
    setupResponseInterceptor(this.client);
  }

  // Singleton pattern
  public static getInstance(): ApiClient {
    if (!ApiClient.instance) {
      ApiClient.instance = new ApiClient();
    }
    return ApiClient.instance;
  }

  // ============================================================================
  // HTTP Methods with Type Safety
  // ============================================================================

  async get<T>(
    endpoint: string,
    params?: Record<string, any>,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const url = buildUrl(endpoint, params);
    const response = await this.client.get<T>(url, config);
    return response.data;
  }

  async post<T>(
    endpoint: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const url = buildUrl(endpoint);
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }

  async put<T>(
    endpoint: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const url = buildUrl(endpoint);
    const response = await this.client.put<T>(url, data, config);
    return response.data;
  }

  async patch<T>(
    endpoint: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const url = buildUrl(endpoint);
    const response = await this.client.patch<T>(url, data, config);
    return response.data;
  }

  async delete<T>(
    endpoint: string,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const url = buildUrl(endpoint);
    const response = await this.client.delete<T>(url, config);
    return response.data;
  }

  // ============================================================================
  // File Upload
  // ============================================================================

  async upload<T>(
    endpoint: string,
    file: File,
    fieldName: string = 'file',
    additionalData?: Record<string, any>
  ): Promise<T> {
    const formData = new FormData();
    formData.append(fieldName, file);

    if (additionalData) {
      Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, String(value));
      });
    }

    const url = buildUrl(endpoint);
    const response = await this.client.post<T>(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  // ============================================================================
  // File Download
  // ============================================================================

  async download(
    endpoint: string,
    params?: Record<string, any>,
    filename?: string
  ): Promise<void> {
    const url = buildUrl(endpoint, params);
    const response = await this.client.get(url, {
      responseType: 'blob',
    });

    // Create download link
    const blob = new Blob([response.data]);
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename || `download-${Date.now()}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  }

  // ============================================================================
  // Request Cancellation
  // ============================================================================

  createAbortController(): AbortController {
    return new AbortController();
  }

  async getWithCancellation<T>(
    endpoint: string,
    params?: Record<string, any>,
    signal?: AbortSignal
  ): Promise<T> {
    const url = buildUrl(endpoint, params);
    const response = await this.client.get<T>(url, { signal });
    return response.data;
  }
}

// ============================================================================
// Export Singleton Instance
// ============================================================================

export const apiClient = ApiClient.getInstance();

// ============================================================================
// Helper function for quick access
// ============================================================================

export const api = {
  get: apiClient.get.bind(apiClient),
  post: apiClient.post.bind(apiClient),
  put: apiClient.put.bind(apiClient),
  patch: apiClient.patch.bind(apiClient),
  delete: apiClient.delete.bind(apiClient),
  upload: apiClient.upload.bind(apiClient),
  download: apiClient.download.bind(apiClient),
};