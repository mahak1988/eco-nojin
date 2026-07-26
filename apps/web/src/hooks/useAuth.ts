import { useCallback, useEffect } from "react";
import { useAuthStore } from "../stores/authStore";
import { authApi } from "../api/auth.api";

export function useAuth() {
  const { user, token, setSession, clearSession, hydrate } = useAuthStore();

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  const login = useCallback(
    async (email: string, password: string) => {
      const res = await authApi.login({ email, password });
      setSession(res.access_token);
      const me = await authApi.me();
      if (me) setSession(res.access_token, me as never);
      return res;
    },
    [setSession],
  );

  const logout = useCallback(() => clearSession(), [clearSession]);

  return {
    user,
    token,
    isAuthenticated: Boolean(token),
    login,
    logout,
  };
}
