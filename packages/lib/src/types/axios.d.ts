import "axios";

declare module "axios" {
  interface InternalAxiosRequestConfig {
    metadata?: {
      startTime?: number;
      endTime?: number;
      [key: string]: unknown;
    };
  }
}
