"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { languages, defaultLocale, Locale, getDirection } from "./languages";

interface LanguageContextType {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  direction: "rtl" | "ltr";
  t: (key: string) => string;
  translations: any;
}

const LanguageContext = createContext<LanguageContextType | null>(null);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(defaultLocale);
  const [translations, setTranslations] = useState<any>(null);
  const [loaded, setLoaded] = useState(false);

  const direction = getDirection(locale);

  // Load locale from localStorage or browser
  useEffect(() => {
    try {
      const saved = localStorage.getItem("econojin_locale") as Locale | null;
      const browserLang = navigator.language.split("-")[0] as Locale;
      const initial = saved || (languages[browserLang] ? browserLang : defaultLocale);
      setLocaleState(initial);
    } catch (e) {
      // SSR or localStorage not available
      setLocaleState(defaultLocale);
    }
  }, []);

  // Load translations
  useEffect(() => {
    const loadTranslations = async () => {
      try {
        const module = await import(`./locales/${locale}.json`);
        setTranslations(module.default);
        setLoaded(true);
      } catch (e) {
        console.warn(`Failed to load ${locale} translations, falling back to English`);
        try {
          const fallback = await import(`./locales/en.json`);
          setTranslations(fallback.default);
          setLoaded(true);
        } catch (e2) {
          console.error("Failed to load fallback translations");
          setTranslations({});
          setLoaded(true);
        }
      }
    };
    loadTranslations();
  }, [locale]);

  // Update document direction
  useEffect(() => {
    if (typeof document !== "undefined") {
      document.documentElement.dir = direction;
      document.documentElement.lang = locale;
    }
  }, [locale, direction]);

  const setLocale = (newLocale: Locale) => {
    setLocaleState(newLocale);
    try {
      localStorage.setItem("econojin_locale", newLocale);
    } catch (e) {
      // localStorage not available
    }
  };

  // Translation function with dot notation
  const t = (key: string): string => {
    if (!loaded || !translations) return key;
    const keys = key.split(".");
    let value: any = translations;
    for (const k of keys) {
      if (value && typeof value === "object" && k in value) {
        value = value[k];
      } else {
        return key;
      }
    }
    return typeof value === "string" ? value : key;
  };

  return (
    <LanguageContext.Provider value={{ locale, setLocale, direction, t, translations }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  
  // Fallback به مقادیر پیش‌فرض اگر provider نبود
  if (!context) {
    console.warn("useLanguage used outside LanguageProvider, using fallback");
    return {
      locale: defaultLocale,
      setLocale: () => {},
      direction: getDirection(defaultLocale),
      t: (key: string) => key,
      translations: {},
    };
  }
  
  return context;
}
