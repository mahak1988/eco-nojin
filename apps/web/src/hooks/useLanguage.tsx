/**
 * ============================================================================
 *  useLanguage — language + direction hook (the heart of i18n)
 * ============================================================================
 *
 *  Wraps react-i18next's useTranslation and exposes:
 *    - language: current language code ("fa" | "en")
 *    - dir: current direction ("rtl" | "ltr")
 *    - isRTL: convenience boolean
 *    - t: translation function
 *    - changeLanguage(lang): switch language (persists to localStorage)
 *
 *  SIDE EFFECT: on every language change, this hook updates <html lang>
 *  and <html dir> so Tailwind logical properties (ms-/me-/ps-/pe-/start-/end-)
 *  flip automatically across the entire app.
 *
 *  USAGE in components:
 *    const { t, isRTL, language } = useLanguage();
 *    <p>{t('dashboard.title')}</p>
 *    <div className="ms-4 ps-2">…</div>  // auto-flips with dir
 *
 *  USAGE for locale-aware formatting:
 *    import { formatNumber } from "@/lib/i18n-utils";
 *    formatNumber(1234, language)  // "۱٬۲۳۴" in fa, "1,234" in en
 * ============================================================================
 */

import { useCallback, useEffect } from "react";
import { useTranslation } from "react-i18next";

import type { SupportedLanguage } from "@/i18n";
import { getDir, isRTL } from "@/lib/i18n-utils";

export interface UseLanguageReturn {
  language: SupportedLanguage;
  dir: "rtl" | "ltr";
  isRTL: boolean;
  t: ReturnType<typeof useTranslation>["t"];
  i18n: ReturnType<typeof useTranslation>["i18n"];
  changeLanguage: (lang: SupportedLanguage) => void;
}

export function useLanguage(): UseLanguageReturn {
  const { t, i18n } = useTranslation();
  const language = i18n.language as SupportedLanguage;
  const dir = getDir(language);
  const rtl = isRTL(language);

  // Sync <html lang> and <html dir> on every language change.
  // This is what makes Tailwind logical properties flip the layout.
  useEffect(() => {
    if (typeof document === "undefined") return;
    document.documentElement.lang = language;
    document.documentElement.dir = dir;
  }, [language, dir]);

  const changeLanguage = useCallback(
    (lang: SupportedLanguage) => {
      void i18n.changeLanguage(lang);
    },
    [i18n],
  );

  return {
    language,
    dir,
    isRTL: rtl,
    t,
    i18n,
    changeLanguage,
  };
}
