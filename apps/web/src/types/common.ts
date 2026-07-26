export type DataSource = "api" | "mock" | "cache";

export interface LoadState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  source: DataSource;
}

export interface HealthResponse {
  status: string;
  version?: string;
  environment?: string;
  database?: string;
}
