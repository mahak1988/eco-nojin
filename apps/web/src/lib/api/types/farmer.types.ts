// ============================================================================
// 🔴 تطبیق دقیق با api/modules/farmer/schemas.py
// ============================================================================

// منطبق با FarmerBase
export interface FarmerBase {
  name: string;             // min_length=2, max_length=100
  email?: string | null;
  phone?: string | null;
  farm_location?: string | null;
  farm_size_hectares?: number | null;  // ge=0
}

// منطبق با FarmerCreate
export interface FarmerCreate extends FarmerBase {}

// منطبق با FarmerUpdate
export interface FarmerUpdate {
  name?: string;
  email?: string | null;
  phone?: string | null;
  farm_location?: string | null;
  farm_size_hectares?: number | null;
}

// منطبق با FarmerResponse
export interface FarmerResponse extends FarmerBase {
  id: number;
  created_at: string;       // ISO datetime
  updated_at?: string | null;
}

// منطبق با FarmerListResponse
export interface FarmerListResponse {
  total: number;
  farmers: FarmerResponse[];
}

// ============================================================================
// Farmer Activities
// ============================================================================

export interface FarmerActivity {
  id: number;
  farmer_id: number;
  activity_type: string;
  description: string;
  created_at: string;
}