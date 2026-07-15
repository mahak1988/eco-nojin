/**
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
