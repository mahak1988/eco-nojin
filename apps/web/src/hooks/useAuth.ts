import { useCallback, useEffect, useState } from "react";
import { useAuthStore } from "../stores/authStore";
import { authApi } from "../api/auth.api";
import type { AuthUser } from "../types/auth";

function mapUser(me: {
  id?: number | string;
  email?: string;
  full_name?: string | null;
  is_active?: boolean;
  is_superuser?: boolean;
  is_verified?: boolean;
  locale?: string;
}): AuthUser {
  return {
    id: String(me.id ?? ""),
    email: me.email ?? "",
    full_name: me.full_name ?? undefined,
    is_superuser: me.is_superuser,
  } as AuthUser;
}

export function useAuth() {
  const { user, token, setSession, clearSession, hydrate } = useAuthStore();
  const [booting, setBooting] = useState(true);

  useEffect(() => {
    hydrate();
    let cancelled = false;
    (async () => {
      try {
        const me = await authApi.me();
        if (!cancelled && me && typeof me === "object" && ("id" in me || "email" in me)) {
          setSession(token || "cookie", mapUser(me as never));
        }
      } catch {
        /* not logged in */
      } finally {
        if (!cancelled) setBooting(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [hydrate, setSession, token]);

  const setSessionFromAuth = useCallback(
    (tok: string, u?: unknown) => {
      if (u && typeof u === "object" && u !== null && ("id" in u || "email" in u)) {
        setSession(tok || "cookie", mapUser(u as never));
      } else if (tok) {
        setSession(tok);
      }
    },
    [setSession],
  );

  const login = useCallback(
    async (email: string, password: string) => {
      const res = await authApi.login({ username: email, password });
      // authApi.login already normalizes accessToken → access_token
      const tok = res.access_token || "";
      if (res.user) setSessionFromAuth(tok, res.user);
      else if (tok) setSession(tok);
      return res;
    },
    [setSession, setSessionFromAuth]
  );

  const register = useCallback(
    async (
      email: string,
      password: string,
      extra?: {
        full_name?: string;
        phone?: string;
        organization?: string;
        role?: "farmer" | "expert" | "viewer";
      },
    ) => {
      const res = await authApi.register({
        email,
        password,
        full_name: extra?.full_name,
        phone: extra?.phone,
        organization: extra?.organization,
        role: extra?.role ?? "farmer",
        accept_terms: true,
      });
      return res;
    },
    [],
  );

  const logout = useCallback(async () => {
    await authApi.logout();
    clearSession();
  }, [clearSession]);

  return {
    user,
    token,
    booting,
    isAuthenticated: Boolean(user) || Boolean(token),
    login,
    register,
    logout,
    setSessionFromAuth,
  };
}
