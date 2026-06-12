// ============================================================================
// 🔴 تطبیق دقیق با Pydantic Schemas از بک‌اند
// ============================================================================

// منطبق با api/modules/auth/schemas.py::LoginRequest
export interface LoginRequest {
  fid: string;      // min_length=3, max_length=32
  phone: string;    // pattern: ^\+?[0-9]{10,15}$
  name?: string;    // max_length=100
}

// منطبق با api/modules/auth/schemas.py::TokenResponse
export interface LoginResponse {
  access_token: string;
  token_type: string;  // "bearer"
  farmer_id: string;
}

// منطبق با api/modules/auth/schemas.py::OtpRequest
export interface OtpRequest {
  phone: string;    // pattern: ^\+?[0-9]{10,15}$
  fid?: string;     // max_length=32
}

// منطبق با api/modules/auth/schemas.py::OtpVerify
export interface OtpVerify {
  phone: string;    // pattern: ^\+?[0-9]{10,15}$
  code: string;     // min_length=4, max_length=8
  fid: string;      // min_length=3, max_length=32
  name?: string;    // max_length=100
}

// Response برای OTP Request (در حالت dev)
export interface OtpRequestResponse {
  sent: boolean;
  phone: string;
  dev_code?: string;  // فقط در حالت توسعه
  expires_in: number;
  message?: string;
}

// منطبق با api/modules/auth/schemas.py::ProfileResponse
export interface UserProfile {
  fid: string;
  name: string;
  phone: string;
  registered_at: string;  // ISO datetime
  wallet_address?: string | null;
}

// منطبق با api/modules/auth/schemas.py::WalletLinkRequest
export interface WalletLinkRequest {
  wallet_address: string;
}

export interface WalletLinkResponse {
  success: boolean;
  wallet_address: string;
}

// ============================================================================
// Auth State
// ============================================================================

export interface AuthState {
  isAuthenticated: boolean;
  user: UserProfile | null;
  token: string | null;
  farmerId: string | null;
}

// ============================================================================
// API Response Types
// ============================================================================

export interface ApiError {
  detail: string;
  error_code?: string;
  status: number;
  timestamp: string;
}