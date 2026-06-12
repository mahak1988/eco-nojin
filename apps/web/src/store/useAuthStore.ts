import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { UserProfile } from '@/lib/api/types/auth.types';

// ============================================================================
// Auth Store Interface
// ============================================================================

interface AuthState {
  // State
  user: UserProfile | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  
  // Actions
  setUser: (user: UserProfile | null) => void;
  setToken: (token: string | null) => void;
  setRefreshToken: (refreshToken: string | null) => void;
  clearAuth: () => void;
  
  // Computed
  hasRole: (role: 'farmer' | 'admin' | 'expert') => boolean;
}

// ============================================================================
// Auth Store
// ============================================================================

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial State
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      
      // Actions
      setUser: (user) => set({ 
        user,
        isAuthenticated: !!user && !!get().token 
      }),
      
      setToken: (token) => set({ 
        token,
        isAuthenticated: !!token && !!get().user 
      }),
      
      setRefreshToken: (refreshToken) => set({ refreshToken }),
      
      clearAuth: () => set({
        user: null,
        token: null,
        refreshToken: null,
        isAuthenticated: false,
      }),
      
      // Computed
      hasRole: (role) => {
        const { user } = get();
        return user?.role === role;
      },
    }),
    {
      name: 'econojin-auth', // LocalStorage key
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);