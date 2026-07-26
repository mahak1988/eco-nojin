import { create } from "zustand";
import type { AuthUser } from "../types/auth";

interface AuthStore {
  user: AuthUser | null;
  token: string | null;
  setSession: (token: string, user?: AuthUser | null) => void;
  clearSession: () => void;
  hydrate: () => void;
}

function readToken(): string | null {
  try {
    return localStorage.getItem("access_token") || localStorage.getItem("token");
  } catch {
    return null;
  }
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  token: null,
  setSession: (token, user = null) => {
    try {
      localStorage.setItem("access_token", token);
      localStorage.setItem("token", token);
    } catch {
      /* ignore */
    }
    set({ token, user });
  },
  clearSession: () => {
    try {
      localStorage.removeItem("access_token");
      localStorage.removeItem("token");
    } catch {
      /* ignore */
    }
    set({ token: null, user: null });
  },
  hydrate: () => set({ token: readToken() }),
}));
