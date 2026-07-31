import React, { createContext, useContext, useEffect, useState } from 'react';

interface ThemeContextType {
  theme: string;
  themeColors: Record<string, string>;
  setTheme: (theme: string) => void;
  setCustomColors: (colors: Record<string, string>) => void;
  toggleRTL: () => void;
  isRTL: boolean;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// Default themes
const THEMES = {
  light: {
    primary: '#15803d',
    secondary: '#bbf7d0',
    accent: '#22c55e',
    background: '#ffffff',
    surface: '#f8fafc',
    text: '#1e293b',
    textSecondary: '#64748b',
  },
  dark: {
    primary: '#4ade80',
    secondary: '#166534',
    accent: '#22c55e',
    background: '#0f172a',
    surface: '#1e293b',
    text: '#f1f5f9',
    textSecondary: '#94a3b8',
  },
  eco: {
    primary: '#15803d',
    secondary: '#a3e635',
    accent: '#22c55e',
    background: '#f0fdf4',
    surface: '#dcfce7',
    text: '#14532d',
    textSecondary: '#16653d',
  },
  ocean: {
    primary: '#0ea5e9',
    secondary: '#7dd3fc',
    accent: '#0284c7',
    background: '#f0f9ff',
    surface: '#e0f2fe',
    text: '#082f49',
    textSecondary: '#1e3a8a',
  },
  sunset: {
    primary: '#f97316',
    secondary: '#fb923c',
    accent: '#ea580c',
    background: '#fffbeb',
    surface: '#fef3c7',
    text: '#9a3412',
    textSecondary: '#c2410c',
  }
};

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setThemeState] = useState<string>(() => {
    const savedTheme = localStorage.getItem('admin-theme');
    return savedTheme || 'light';
  });
  
  const [customColors, setCustomColorsState] = useState<Record<string, string>>({});
  const [isRTL, setIsRTL] = useState<boolean>(() => {
    const savedRTL = localStorage.getItem('admin-rtl');
    return savedRTL === 'true';
  });

  // Apply theme to document
  useEffect(() => {
    const root = document.documentElement;
    
    // Apply theme colors
    const currentTheme = { ...THEMES[theme as keyof typeof THEMES], ...customColors };
    Object.entries(currentTheme).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key}`, value);
    });
    
    // Apply RTL
    if (isRTL) {
      document.body.setAttribute('dir', 'rtl');
      document.body.classList.add('rtl');
    } else {
      document.body.setAttribute('dir', 'ltr');
      document.body.classList.remove('rtl');
    }
    
    // Save to localStorage
    localStorage.setItem('admin-theme', theme);
    localStorage.setItem('admin-rtl', isRTL.toString());
  }, [theme, customColors, isRTL]);

  const setTheme = (newTheme: string) => {
    if (Object.keys(THEMES).includes(newTheme)) {
      setThemeState(newTheme);
    }
  };

  const setCustomColors = (colors: Record<string, string>) => {
    setCustomColorsState(colors);
  };

  const toggleRTL = () => {
    setIsRTL(!isRTL);
  };

  const themeColors = { ...THEMES[theme as keyof typeof THEMES], ...customColors };

  return (
    <ThemeContext.Provider
      value={{
        theme,
        themeColors,
        setTheme,
        setCustomColors,
        toggleRTL,
        isRTL,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};