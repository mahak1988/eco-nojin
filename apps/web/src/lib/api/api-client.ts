import { paths } from "./minimal-schema"; // Changed from schema to minimal-schema
import { authStore } from "../../stores/authStore";

type HttpMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH" | "HEAD" | "OPTIONS";

interface ApiRequest {
  endpoint: keyof paths;
  method: HttpMethod;
  body?: any;
  params?: {
    query?: Record<string, any>;
    path?: Record<string, any>;
  };
}

// Generic API function
export async function apiClient<
  T extends keyof paths
>(
  request: ApiRequest
): Promise<
  T extends keyof paths
    ? "responses" extends keyof paths[T]
      ? "200" extends keyof paths[T]["responses"]
        ? paths[T]["responses"]["200"] extends { content: { "application/json": infer R } }
          ? R
          : never
        : never
      : never
    : never
> {
  const { endpoint, method, body, params } = request;

  // Get the base URL from environment - using public runtime config
  const baseURL =
    typeof window !== "undefined"
      ? window.location.origin
      : (typeof process !== "undefined" && (process as { env?: Record<string, string> }).env?.API_BASE_URL) ||
        "http://localhost:8000";

  // Construct the full URL with query parameters
  let url = `${baseURL}${endpoint}`;

  // Add query parameters if present
  if (params?.query) {
    const queryString = new URLSearchParams(params.query).toString();
    url += `?${queryString}`;
  }

  // Get auth token from store (authStore.getState — not React hook)
  const { token } = authStore.getState();

  const response = await fetch(url, {
    method,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  // For 204 No Content responses, return null
  if (response.status === 204) {
    return null as any;
  }

  return response.json();
}
