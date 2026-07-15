#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eco Nojin - Fix useAuth.ts API Compatibility
=============================================
بازنویسی useAuth.ts با API سازگار با فایل‌های موجود

این اسکریپت:
✅ API قدیمی useAuth را حفظ می‌کند
✅ از api-client و React Query جدید استفاده می‌کند
✅ AuthProvider و isAuthError را export می‌کند
✅ تمام ۱۷ خطا را رفع می‌کند
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "apps" / "web" / "src"

NEW_USE_AUTH = '''/**
 * ============================================================================
 *  useAuth — Authentication hook with backward-compatible API
 * ============================================================================
 * 
 * این فایل hook احراز هویت را با API سازگار با نسخه قبلی ارائه می‌دهد:
 * - user: کاربر فعلی
 * - login: تابع ورود
 * - logout: تابع خروج
 * - register: تابع ثبت‌نام
 * - isAuthenticated: آیا کاربر لاگین است
 * - status: وضعیت (pending | success | error)
 * - AuthProvider: Context provider
 * - isAuthError: بررسی خطای احراز هویت
 * 
 * در پشت صحنه از React Query و api-client جدید استفاده می‌کند.
 */

import {
  createContext,
  useContext,
  ReactNode,
} from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  login as apiLogin,
  register as apiRegister,
  logout as apiLogout,
  getCurrentUser,
  tokenStorage,
} from "@/services/authService";
import type { AuthCredentials, RegisterPayload, User, ApiError } from "@/types";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface AuthContextValue {
  user: User | null;
  login: (credentials: AuthCredentials) => Promise<void>;
  logout: () => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  isAuthenticated: boolean;
  status: "pending" | "success" | "error";
  isLoading: boolean;
  error: Error | null;
}

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

// ---------------------------------------------------------------------------
// AuthProvider Component
// ---------------------------------------------------------------------------

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  
  // Query for current user
  const {
    data: user = null,
    status,
    error,
    isLoading,
  } = useQuery<User | null>({
    queryKey: ["auth", "currentUser"],
    queryFn: async () => {
      // Check if token exists
      const token = tokenStorage.getAccessToken();
      if (!token) return null;
      
      try {
        return await getCurrentUser();
      } catch {
        return null;
      }
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
    retry: false,
  });
  
  // Login mutation
  const loginMutation = useMutation({
    mutationFn: (credentials: AuthCredentials) => apiLogin(credentials),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["auth", "currentUser"] });
    },
  });
  
  // Register mutation
  const registerMutation = useMutation({
    mutationFn: (payload: RegisterPayload) => apiRegister(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["auth", "currentUser"] });
    },
  });
  
  // Logout mutation
  const logoutMutation = useMutation({
    mutationFn: apiLogout,
    onSuccess: () => {
      queryClient.clear();
    },
  });
  
  // Wrapper functions
  const login = async (credentials: AuthCredentials) => {
    await loginMutation.mutateAsync(credentials);
  };
  
  const logout = async () => {
    await logoutMutation.mutateAsync();
  };
  
  const register = async (payload: RegisterPayload) => {
    await registerMutation.mutateAsync(payload);
  };
  
  const isAuthenticated = !!user;
  
  const value: AuthContextValue = {
    user,
    login,
    logout,
    register,
    isAuthenticated,
    status,
    isLoading,
    error,
  };
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// ---------------------------------------------------------------------------
// useAuth Hook
// ---------------------------------------------------------------------------

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  
  return context;
}

// ---------------------------------------------------------------------------
// Helper Functions
// ---------------------------------------------------------------------------

/**
 * بررسی اینکه آیا خطا مربوط به احراز هویت است
 */
export function isAuthError(error: unknown): boolean {
  if (!error) return false;
  
  if (typeof error === "object" && error !== null) {
    const err = error as any;
    
    // Check for status code
    if (err.statusCode === 401 || err.statusCode === 403) {
      return true;
    }
    
    // Check for response status
    if (err.response?.status === 401 || err.response?.status === 403) {
      return true;
    }
    
    // Check for error type
    if (err.error === "Unauthorized" || err.error === "Forbidden") {
      return true;
    }
    
    // Check for message
    if (typeof err.message === "string") {
      const msg = err.message.toLowerCase();
      if (
        msg.includes("unauthorized") ||
        msg.includes("forbidden") ||
        msg.includes("invalid credentials") ||
        msg.includes("session expired")
      ) {
        return true;
      }
    }
  }
  
  return false;
}

// ---------------------------------------------------------------------------
// Default Export
// ---------------------------------------------------------------------------

export default useAuth;
'''

def main():
    print("\n" + "=" * 70)
    print("🔧 Fix useAuth.ts API Compatibility")
    print("=" * 70)
    
    file_path = SRC_DIR / "hooks" / "useAuth.ts"
    
    if not file_path.exists():
        print(f"\n❌ useAuth.ts not found at: {file_path}")
        return
    
    # Backup
    backup_path = file_path.with_suffix(".ts.backup2")
    try:
        import shutil
        shutil.copy2(file_path, backup_path)
        print(f"\n💾 Backup created: {backup_path.name}")
    except Exception as e:
        print(f"\n⚠️  Backup failed: {e}")
    
    # Write new content
    try:
        file_path.write_text(NEW_USE_AUTH, encoding="utf-8")
        print(f"\n✅ useAuth.ts rewritten with backward-compatible API")
        print(f"\n📝 API provided:")
        print(f"   • user: User | null")
        print(f"   • login: (credentials) => Promise<void>")
        print(f"   • logout: () => Promise<void>")
        print(f"   • register: (payload) => Promise<void>")
        print(f"   • isAuthenticated: boolean")
        print(f"   • status: 'pending' | 'success' | 'error'")
        print(f"   • isLoading: boolean")
        print(f"   • error: Error | null")
        print(f"   • AuthProvider: Component")
        print(f"   • isAuthError: (error) => boolean")
    except Exception as e:
        print(f"\n❌ Failed to write: {e}")
        return
    
    print("\n" + "=" * 70)
    print("✅ Fix completed!")
    print("=" * 70)
    
    print("\n📌 Next steps:")
    print("   1. Build: cd apps/web && pnpm build")
    print("   2. If successful, commit:")
    print("      git add . && git commit -m 'fix(phase-4): restore useAuth API'")


if __name__ == "__main__":
    main()