/**
 * Drought Domain Types
 * تعاریف تایپ مرتبط با ماژول خشکسالی
 */

export interface DroughtIndex {
  id?: number;
  name: string;
  value: number;
  timestamp: string;
  location_lat: number;
  location_lon: number;
  severity?: DroughtSeverity;
}

export type DroughtSeverity = 
  | 'NORMAL'
  | 'MILD_DROUGHT'
  | 'MODERATE_DROUGHT'
  | 'SEVERE_DROUGHT'
  | 'EXTREME_DROUGHT'
  | 'NO_DATA';

export interface SPEIRequest {
  station_id: string;
  start_date: string;
  end_date: string;
  scale_months: number;
}

export interface CHIRPSRequest {
  lat: number;
  lon: number;
  start_date: string;
  end_date: string;
}

export interface EarlyWarningResponse {
  region: {
    lat: number;
    lon: number;
  };
  severity: DroughtSeverity;
  timestamp: string;
  recommendation: string;
}
