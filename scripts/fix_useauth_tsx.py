#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eco Nojin - Fix useAuth.ts → useAuth.tsx
=========================================
تبدیل useAuth.ts به useAuth.tsx برای پشتیبانی از JSX

این اسکریپت:
✅ فایل useAuth.ts را حذف می‌کند
✅ فایل useAuth.tsx را با محتوای صحیح ایجاد می‌کند
✅ import React را اضافه می‌کند (برای JSX)
✅ تمام ۴ خطا را رفع می‌کند
"""

from pathlib import Path
import shutil

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "apps" / "web" / "src"

NEW_USE_AUTH_TSX = '''/**
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

import React, { createContext, useContext, ReactNode } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  login as apiLogin,
  register as apiRegister,
  logout as apiLogout,
  getCurrentUser,
  tokenStorage,
} from "@/services/authService";
import type { AuthCredentials, RegisterPayload, User } from "@/types";

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
    print("🔧 Fix useAuth.ts → useAuth.tsx")
    print("=" * 70)
    
    ts_file = SRC_DIR / "hooks" / "useAuth.ts"
    tsx_file = SRC_DIR / "hooks" / "useAuth.tsx"
    
    # Step 1: Backup existing .ts file
    if ts_file.exists():
        backup_path = ts_file.with_suffix(".ts.backup3")
        try:
            shutil.copy2(ts_file, backup_path)
            print(f"\n💾 Backup created: {backup_path.name}")
        except Exception as e:
            print(f"\n⚠️  Backup failed: {e}")
    
    # Step 2: Remove .ts file
    if ts_file.exists():
        try:
            ts_file.unlink()
            print(f"\n🗑️  Removed: {ts_file.name}")
        except Exception as e:
            print(f"\n❌ Failed to remove .ts file: {e}")
            return
    
    # Step 3: Create .tsx file
    try:
        tsx_file.parent.mkdir(parents=True, exist_ok=True)
        tsx_file.write_text(NEW_USE_AUTH_TSX, encoding="utf-8")
        print(f"\n✅ Created: {tsx_file.name}")
        print(f"\n📝 Key changes:")
        print(f"   • File extension: .ts → .tsx")
        print(f"   • Added: import React from 'react'")
        print(f"   • JSX now supported: <AuthContext.Provider>")
    except Exception as e:
        print(f"\n❌ Failed to create .tsx file: {e}")
        return
    
    # Step 4: Verify imports in other files
    print(f"\n🔍 Checking imports in other files...")
    
    files_to_check = [
        "src/main.tsx",
        "src/App.tsx",
        "src/pages/Login.tsx",
        "src/pages/Register/Register.tsx",
    ]
    
    for rel_path in files_to_check:
        file_path = SRC_DIR / rel_path.replace("src/", "")
        if not file_path.exists():
            continue
        
        try:
            content = file_path.read_text(encoding="utf-8")
            
            # Check if import exists
            if 'from "@/hooks/useAuth"' in content or "from '@/hooks/useAuth'" in content:
                print(f"   ✅ {rel_path}: import OK (no extension needed)")
            else:
                print(f"   ⚠️  {rel_path}: no useAuth import found")
        except Exception:
            pass
    
    print("\n" + "=" * 70)
    print("✅ Fix completed!")
    print("=" * 70)
    
    print("\n📌 Next steps:")
    print("   1. Build: cd apps/web && pnpm build")
    print("   2. If successful, commit:")
    print("      git add . && git commit -m 'fix(phase-4): convert useAuth to .tsx'")


if __name__ == "__main__":
    main()