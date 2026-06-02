"use client";

import { createContext, useContext, useState, useCallback, useEffect } from "react";
import fa from "./messages/fa.json";
import en from "./messages/en.json";

type Locale = "fa" | "en";
const messages: Record<Locale, Record<string, string>> = { fa, en };

type I18nContextType = {
  locale: Locale;
  setLocale: (l: Locale) => void;
  t: (key: string) => string;
  dir: "rtl" | "ltr";
};

const I18nContext = createContext<I18nContextType | null>(null);

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>("fa");

  useEffect(() => {
    const saved = localStorage.getItem("econojin_locale") as Locale | null;
    if (saved === "fa" || saved === "en") setLocaleState(saved);
  }, []);

  const setLocale = useCallback((l: Locale) => {
    setLocaleState(l);
    localStorage.setItem("econojin_locale", l);
    document.documentElement.lang = l;
    document.documentElement.dir = l === "fa" ? "rtl" : "ltr";
  }, []);

  const t = useCallback(
    (key: string) => messages[locale][key] ?? key,
    [locale]
  );

  return (
    <I18nContext.Provider
      value={{ locale, setLocale, t, dir: locale === "fa" ? "rtl" : "ltr" }}
    >
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used within I18nProvider");
  return ctx;
}
