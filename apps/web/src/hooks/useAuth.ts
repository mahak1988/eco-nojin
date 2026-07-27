import { useCallback, useEffect, useState } from "react";
import { useAuthStore } from "../stores/authStore";
import { authApi } from "../api/auth.api";
import type { AuthUser } from "../types/auth";

function mapUser(me: {
  id: number;
  email: string;
  full_name?: string | null;
  role?: string;
  is_superuser?: boolean;
}): AuthUser {
  return {
    id: me.id,
    email: me.email,
    full_name: me.full_name ?? undefined,
    role: me.role,
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
        if (!cancelled && me && typeof me === "object" && "id" in me) {
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

  const login = useCallback(
    async (email: string, password: string) => {
      const res = await authApi.login({ email, password });
      const tok = res.access_token || "";
      if (tok) setSession(tok);
      const me = res.user || (await authApi.me());
      if (me && typeof me === "object" && "id" in me) {
        setSession(tok || "cookie", mapUser(me as never));
      }
      return res;
    },
    [setSession],
  );

  const register = useCallback(
    async (email: string, password: string, full_name?: string) => {
      const res = await authApi.register({ email, password, full_name });
      const tok = res.access_token || "";
      if (tok) setSession(tok);
      if (res.user) setSession(tok || "cookie", mapUser(res.user as never));
      return res;
    },
    [setSession],
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
  };
}
