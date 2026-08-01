import { authStore } from "../../stores/authStore";

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
  method: string = "GET",
  body?: any
): Promise<ApiResponse<T>> {
  try {
    const { token } = authStore.getState();

    const response = await fetch(endpoint, {
      method,
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      ...(body && { body: JSON.stringify(body) }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return {
        data: null as unknown as T,
        error:
          (errorData as { detail?: string; message?: string }).detail ||
          (errorData as { message?: string }).message ||
          `HTTP error! status: ${response.status}`,
        success: false,
      };
    }

    if (response.status === 204) {
      return {
        data: null as unknown as T,
        success: true,
      };
    }

    const data = await response.json();
    return {
      data,
      success: true,
    };
  } catch (error) {
    return {
      data: null as unknown as T,
      error: error instanceof Error ? error.message : "Network error occurred",
      success: false,
    };
  }
}
