/**
 * ============================================================================
 *  i18n initialization — react-i18next + browser language detection
 * ============================================================================
 *
 *  Supports two languages:
 *    - "fa" (Persian, RTL) — default
 *    - "en" (English, LTR)
 *
 *  Detection order (first match wins):
 *    1. localStorage key "econojin.lang"  (set by user via LanguageSwitcher)
 *    2. navigator.language                (browser preference)
 *    3. <html lang="\u00a0">               (fallback)
 *
 *  The direction (rtl/ltr) is set on <html dir> by the useLanguage hook,
 *  NOT here — keep this module free of DOM side-effects so it stays
 *  testable in isolation.
 * ============================================================================
 */

import { createInstance, type i18n as I18nInstance } from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import { initReactI18next } from "react-i18next";

import fa from "./locales/fa.json";
import en from "./locales/en.json";

// ---------------------------------------------------------------------------
// Language constants
// ---------------------------------------------------------------------------

/** Tuple of all supported languages. Append new codes at the end. */
export const SUPPORTED_LANGUAGES = ["fa", "en"] as const;
export type SupportedLanguage = (typeof SUPPORTED_LANGUAGES)[number];

/**
 * Default language used when no detection signal is available.
 * Read from `VITE_DEFAULT_LANG` env var, falls back to "fa".
 */
export const DEFAULT_LANGUAGE: SupportedLanguage = (() => {
  const env = import.meta.env["VITE_DEFAULT_LANG"] as string | undefined;
  if (env && (SUPPORTED_LANGUAGES as readonly string[]).includes(env)) {
    return env as SupportedLanguage;
  }
  return "fa";
})();

/**
 * Languages that render right-to-left.
 * Add codes here when you add a new RTL language (ar, ur, he, ps, sd, ...).
 */
export const RTL_LANGUAGES: ReadonlySet<string> = new Set([
  "fa",
  "ar",
  "ur",
  "he",
  "ps",
  "sd",
]);

// ---------------------------------------------------------------------------
// Resources — the translation JSON files keyed by language code
// ---------------------------------------------------------------------------

const resources = {
  fa: { translation: fa },
  en: { translation: en },
} as const;

// ---------------------------------------------------------------------------
// Create the i18n instance (isolated, not the global singleton)
// ---------------------------------------------------------------------------

export const i18n: I18nInstance = createInstance();

/**
 * Initialize the instance.
 *
 * i18n.init() returns Promise<TFunction>, but we want to expose a Promise
 * that resolves to the instance itself (so callers can `await i18nReady`
 * and then use `i18n` directly). We chain `.then(() => i18n)` to do this.
 */
export const i18nReady: Promise<I18nInstance> = i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: DEFAULT_LANGUAGE,
    supportedLngs: SUPPORTED_LANGUAGES,
    nonExplicitSupportedLngs: true,
    interpolation: {
      escapeValue: false,
    },
    detection: {
      order: ["localStorage", "navigator", "htmlTag"],
      lookupLocalStorage: "econojin.lang",
      caches: ["localStorage"],
    },
    react: {
      useSuspense: false,
    },
  })
  .then(() => i18n);

// ---------------------------------------------------------------------------
// Direction helpers (pure functions — no DOM access)
// ---------------------------------------------------------------------------

export function getLanguageDir(language: string): "rtl" | "ltr" {
  return RTL_LANGUAGES.has(language) ? "rtl" : "ltr";
}

export function isLanguageRTL(language: string): boolean {
  return RTL_LANGUAGES.has(language);
}

export function isSupportedLanguage(value: string): value is SupportedLanguage {
  return (SUPPORTED_LANGUAGES as readonly string[]).includes(value);
}

export function coerceLanguage(value: string | undefined | null): SupportedLanguage {
  if (!value) return DEFAULT_LANGUAGE;
  if (isSupportedLanguage(value)) return value;
  const base = value.split("-")[0] ?? "";
  if (isSupportedLanguage(base)) return base;
  return DEFAULT_LANGUAGE;
}

// ---------------------------------------------------------------------------
// Development-only diagnostics
// ---------------------------------------------------------------------------

if (import.meta.env.DEV) {
  void i18nReady.then(() => {
    // eslint-disable-next-line no-console
    console.info(
      `[i18n] language="${i18n.language}" dir="${getLanguageDir(i18n.language)}"`,
    );
  });

  i18n.on("missingKey", (lngs, namespace, key) => {
    // eslint-disable-next-line no-console
    console.warn(`[i18n] missing key "${key}" in [${lngs.join(", ")}] / "${namespace}"`);
  });
}

export default i18n;
