export interface CarbonResult {
  activity_type: string;
  carbon_absorbed_kg: number;
  carbon_absorbed_tons: number;
  annual_sequestration_rate: number;
  projection_10y_tons: number;
  projection_50y_tons: number;
  confidence: number;
  methodology: string;
  seed_tokens_earned: number;
  estimated_gaia_value_usd: number;
}

export interface Certificate {
  token_id: number;
  owner: string;
  activity_type: string;
  species?: string;
  carbon_kg: number;
  health_score: number;
  growth_stage: string;
  verified_sources: string[];
  metadata: any;
}

export interface Portfolio {
  owner: string;
  total_certificates: number;
  total_carbon_kg: number;
  total_carbon_tons: number;
  estimated_value_usd: number;
  certificates: Certificate[];
}

export interface Farmer {
  id: number;
  name: string;
  email?: string;
  phone?: string;
  farm_location?: string;
  farm_size_hectares?: number;
  created_at: string;
  updated_at?: string;
}

export interface PlatformStats {
  total_activities: number;
  total_carbon_kg: number;
  total_carbon_tons: number;
  equivalent_trees: number;
  estimated_value_usd: number;
  by_activity: Record<string, { count: number; carbon_kg: number }>;
  timestamp: string;
}

export interface Model {
  name: string;
  type: string;
  description: string;
  status: string;
}
