'use client';

import { createContext, useContext, ReactNode } from 'react';

interface ThemeContextType {}

const ThemeContext = createContext<ThemeContextType>({});

export function ThemeProvider({ children }: { children: ReactNode }) {
  return <ThemeContext.Provider value={{}}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  return useContext(ThemeContext);
}
