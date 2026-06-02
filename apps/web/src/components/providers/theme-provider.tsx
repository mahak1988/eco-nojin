"use client";

import * as React from "react";
import { useAppStore } from "@/store/useAppStore";

type Theme = "dark" | "light";

interface ThemeProviderProps {
  children: React.ReactNode;
  attribute?: string;
  defaultTheme?: Theme;
  enableSystem?: boolean;
}

export function ThemeProvider({ children, attribute = "class", defaultTheme = "dark", enableSystem = false }: ThemeProviderProps) {
  const { theme } = useAppStore();
  
  React.useEffect(() => {
    const root = document.documentElement;
    root.classList.remove("light", "dark");
    root.classList.add(theme);
  }, [theme]);
  
  return <>{children}</>;
}
