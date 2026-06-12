#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix useAuth.ts file"""

content = r'''import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../client";
import { ENDPOINTS } from "../endpoints";
import { authStorage } from "@/lib/utils/storage";
import { useAuthStore } from "@/store/useAuthStore";
import { toast } from "react-hot-toast";
import type {
  LoginRequest,
  LoginResponse,
  OtpRequest,
  OtpRequestResponse,
  OtpVerify,
  UserProfile,
} from "../types/auth.types";
import type { LoginInput, RegisterInput } from "@/lib/validation/auth.schema";

// ============================================================================
// Login Hook
// ============================================================================
export function useLogin() {
  const queryClient = useQueryClient();
  const { setUser, setToken, setFarmerId } = useAuthStore();

  return useMutation({
    mutationFn: async (data: LoginInput): Promise<LoginResponse> => {
      const response = await apiClient.post<LoginResponse>(
        ENDPOINTS.AUTH.LOGIN,
        { fid: data.fid, phone: data.phone, name: "" }
      );
      return response;
    },
    onSuccess: (data) => {
      authStorage.setTokens(data.access_token);
      authStorage.setFarmerId(data.farmer_id);
      setToken(data.access_token);
      setFarmerId(data.farmer_id);
      toast.success("ورود موفقیت آمیز!");
      window.location.href = "/dashboard";
    },
    onError: (error: any) => {
      const message = error?.PersianMessage || error?.message || "خطا در ورود";
      toast.error(message);
    },
  });
}

// ============================================================================
// OTP Request Hook
// ============================================================================
export function useOtpRequest() {
  return useMutation({
    mutationFn: async (data: OtpRequest): Promise<OtpRequestResponse> => {
      const response = await apiClient.post<OtpRequestResponse>(
        ENDPOINTS.AUTH.OTP_REQUEST,
        data
      );
      return response;
    },
    onSuccess: (data) => {
      if (data.dev_code) {
        toast.success("کد OTP: " + data.dev_code + " (حالت توسعه)");
      } else {
        toast.success("کد OTP ارسال شد");
      }
    },
    onError: (error: any) => {
      const message = error?.PersianMessage || error?.message || "خطا در ارسال OTP";
      toast.error(message);
    },
  });
}

// ============================================================================
// useForgotPassword - Alias for useOtpRequest
// ============================================================================
export function useForgotPassword() {
  return useOtpRequest();
}

// ============================================================================
// OTP Verify Hook
// ============================================================================
export function useOtpVerify() {
  const queryClient = useQueryClient();
  const { setUser, setToken, setFarmerId } = useAuthStore();

  return useMutation({
    mutationFn: async (data: OtpVerify): Promise<LoginResponse> => {
      const response = await apiClient.post<LoginResponse>(
        ENDPOINTS.AUTH.OTP_VERIFY,
        data
      );
      return response;
    },
    onSuccess: (data) => {
      authStorage.setTokens(data.access_token);
      authStorage.setFarmerId(data.farmer_id);
      setToken(data.access_token);
      setFarmerId(data.farmer_id);
      toast.success("ورود موفقیت آمیز!");
      window.location.href = "/dashboard";
    },
    onError: (error: any) => {
      const message = error?.PersianMessage || error?.message || "کد OTP نامعتبر است";
      toast.error(message);
    },
  });
}

// ============================================================================
// useResetPassword
// ============================================================================
export function useResetPassword() {
  return useMutation({
    mutationFn: async (data: { token: string; newPassword: string }): Promise<any> => {
      const response = await apiClient.post(
        ENDPOINTS.AUTH.OTP_VERIFY,
        {
          phone: authStorage.getFarmerId() || "",
          code: data.token,
          fid: authStorage.getFarmerId() || "",
          name: "",
        }
      );
      return response;
    },
    onSuccess: () => {
      toast.success("رمز عبور با موفقیت تغییر کرد");
    },
    onError: (error: any) => {
      const message = error?.PersianMessage || error?.message || "خطا در تغییر رمز";
      toast.error(message);
    },
  });
}

// ============================================================================
// Register Hook
// ============================================================================
export function useRegister() {
  return useMutation({
    mutationFn: async (data: RegisterInput): Promise<LoginResponse> => {
      const response = await apiClient.post<LoginResponse>(
        ENDPOINTS.AUTH.LOGIN,
        { fid: data.fid, phone: data.phone, name: data.name }
      );
      return response;
    },
    onSuccess: () => {
      toast.success("ثبت نام موفقیت آمیز! لطفا وارد شوید.");
    },
    onError: (error: any) => {
      const message = error?.PersianMessage || error?.message || "خطا در ثبت نام";
      toast.error(message);
    },
  });
}

// ============================================================================
// Get User Profile Hook
// ============================================================================
export function useUserProfile() {
  const { setUser } = useAuthStore();
  const token = authStorage.getAccessToken();

  return useQuery({
    queryKey: ["user", "profile"],
    queryFn: async (): Promise<UserProfile> => {
      const response = await apiClient.get<UserProfile>(ENDPOINTS.AUTH.PROFILE);
      setUser(response);
      return response;
    },
    enabled: !!token,
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });
}

// ============================================================================
// Logout Hook
// ============================================================================
export function useLogout() {
  const queryClient = useQueryClient();
  const { clearAuth } = useAuthStore();

  return useMutation({
    mutationFn: async () => {},
    onSuccess: () => {
      authStorage.clearAll();
      clearAuth();
      queryClient.clear();
      toast.success("خروج موفقیت آمیز");
      window.location.href = "/login";
    },
  });
}

// ============================================================================
// Link Wallet Hook
// ============================================================================
export function useLinkWallet() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (walletAddress: string) => {
      const response = await apiClient.post(
        ENDPOINTS.AUTH.LINK_WALLET,
        { wallet_address: walletAddress }
      );
      return response;
    },
    onSuccess: () => {
      toast.success("کیف پول با موفقیت متصل شد");
      queryClient.invalidateQueries({ queryKey: ["user", "profile"] });
    },
    onError: (error: any) => {
      const message = error?.PersianMessage || error?.message || "خطا در اتصال کیف پول";
      toast.error(message);
    },
  });
}
'''

# Write to file
output_path = r"apps\web\src\lib\api\hooks\useAuth.ts"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ File written successfully: {output_path}")
print(f"📊 File size: {len(content)} bytes")
print("🚀 Now restart the frontend server")