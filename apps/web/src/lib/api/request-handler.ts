import { useAuthStore } from "../stores/auth";

interface ApiResponse<T> {
  data: T;
  error?: string;
  success: boolean;
}

/**
 * Generic request handler with error handling and auth token injection
 */
export async function makeAuthenticatedRequest<T>(
  endpoint: string,
  method: string = 'GET',
  body?: any
): Promise<ApiResponse<T>> {
  try {
    const authStore = useAuthStore.getState();
    
    const response = await fetch(endpoint, {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...(authStore.token ? { 'Authorization': `Bearer ${authStore.token}` } : {}),
      },
      ...(body && { body: JSON.stringify(body) })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return {
        data: null as unknown as T,
        error: errorData.detail || errorData.message || `HTTP error! status: ${response.status}`,
        success: false
      };
    }

    if (response.status === 204) {
      return {
        data: null as unknown as T,
        success: true
      };
    }

    const data = await response.json();
    return {
      data,
      success: true
    };
  } catch (error) {
    return {
      data: null as unknown as T,
      error: error instanceof Error ? error.message : 'Network error occurred',
      success: false
    };
  }
}