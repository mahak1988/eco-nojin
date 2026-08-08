/**
 * Auth session store — HttpOnly cookie-first with localStorage fallback.
 * Tokens are stored in HttpOnly cookies set by the backend.
 * localStorage is only used as a legacy fallback for dev without cookies.
 */
import type { AuthUser } from "../types/auth";

type Listener = () => void;

interface AuthState {
  user: AuthUser | null;
  token: string | null;
}

let state: AuthState = { user: null, token: null };
const listeners = new Set<Listener>();

function emit() {
  listeners.forEach((l) => l());
}

function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.exp * 1000 < Date.now();
  } catch { return true; }
}

function readToken(): string | null {
  // HttpOnly cookies are NOT readable by JS — this is by design.
  // The backend sets access_token cookie; we just check if we have
  // a legacy localStorage token as fallback for development.
  const tok = localStorage.getItem("access_token") || localStorage.getItem("token");
  if (tok && isTokenExpired(tok)) {
    localStorage.removeItem("access_token");
    localStorage.removeItem("token");
    return null;
  }
  return tok;
}

export const authStore = {
  getState: () => state,
  subscribe: (listener: Listener) => {
    listeners.add(listener);
    return () => listeners.delete(listener);
  },
  setSession: (token: string, user: AuthUser | null = null) => {
    // In production: token is stored in HttpOnly cookie by backend.
    // In dev fallback: also store in localStorage for apiClient.
    try {
      if (token && token !== "cookie") {
        localStorage.setItem("access_token", token);
      }
    } catch { /* ignore */ }
    state = { token, user };
    emit();
  },
  clearSession: () => {
    try {
      localStorage.removeItem("access_token");
      localStorage.removeItem("token");
    } catch { /* ignore */ }
    state = { token: null, user: null };
    emit();
  },
  hydrate: () => {
    // Check if we have a legacy token; otherwise rely on cookies
    state = { ...state, token: readToken() };
    emit();
  },
};

/** React-friendly hook without zustand */
import { useSyncExternalStore } from "react";

export function useAuthStore() {
  const snap = useSyncExternalStore(
    authStore.subscribe,
    authStore.getState,
    authStore.getState,
  );
  return {
    ...snap,
    setSession: authStore.setSession,
    clearSession: authStore.clearSession,
    hydrate: authStore.hydrate,
  };
}