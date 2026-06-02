"use client";

import { useEffect } from "react";
import { useAppStore } from "@/store/useAppStore";
import { getStoredUser, getToken } from "@/lib/auth";

export function AppProviders({ children }: { children: React.ReactNode }) {
  const login = useAppStore((s) => s.login);

  useEffect(() => {
    const token = getToken();
    const user = getStoredUser();
    if (token) login(token, user);
  }, [login]);

  return <>{children}</>;
}
