/**
 * Soil & Water Domain Types
 * تعاریف تایپ مرتبط با ماژول خاک و آب
 */

export interface SoilAnalysis {
  id?: number;
  location_lat: number;
  location_lon: number;
  soil_type: SoilType;
  organic_matter_percent: number;
  moisture_content: number;
  ph_level: number;
  timestamp: string;
}

export type SoilType = 
  | 'SANDY'
  | 'LOAMY'
  | 'CLAY'
  | 'SILT'
  | 'PEATY';

export interface WaterBalance {
  date: string;
  precipitation: number;
  evapotranspiration: number;
  runoff: number;
  infiltration: number;
  soil_moisture_change: number;
}

export interface ErosionRisk {
  location: {
    lat: number;
    lon: number;
  };
  risk_level: 'LOW' | 'MODERATE' | 'HIGH' | 'VERY_HIGH';
  rusle_value: number;
  contributing_factors: string[];
}
