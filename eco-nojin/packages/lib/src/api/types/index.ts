/**
 * API Types - Domain Index
 * بازexport کردن تمام تایپ‌های دامنه‌محور
 */

export * from './drought.types';
export * from './soil-water.types';
export * from './financial.types';
export * from './iot.types';

// Common Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
}
