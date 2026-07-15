/**
 * ============================================================================
 *  i18n initialization — 10-language support (react-i18next)
 * ============================================================================
 *
 *  Supported languages:
 *    RTL: fa (Persian), ar (Arabic)
 *    LTR: en, es, fr, de, ru, zh, tr, hi
 *
 *  Total native speakers covered: ~4.8 billion (60% of world population)
 * ============================================================================
 */

import { createInstance, type i18n as I18nInstance } from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import { initReactI18next } from "react-i18next";

import fa from "./locales/fa.json";
import en from "./locales/en.json";
import ar from "./locales/ar.json";
import es from "./locales/es.json";
import fr from "./locales/fr.json";
import de from "./locales/de.json";
import ru from "./locales/ru.json";
import zh from "./locales/zh.json";
import tr from "./locales/tr.json";
import hi from "./locales/hi.json";

// ---------------------------------------------------------------------------
// Language constants
// ---------------------------------------------------------------------------

export const SUPPORTED_LANGUAGES = [
  "fa", "en", "ar", "es", "fr", "de", "ru", "zh", "tr", "hi"
] as const;
export type SupportedLanguage = (typeof SUPPORTED_LANGUAGES)[number];

export const DEFAULT_LANGUAGE: SupportedLanguage = (() => {
  const env = import.meta.env["VITE_DEFAULT_LANG"] as string | undefined;
  if (env && (SUPPORTED_LANGUAGES as readonly string[]).includes(env)) {
    return env as SupportedLanguage;
  }
  return "fa";
})();

export const RTL_LANGUAGES: ReadonlySet<string> = new Set([
  "fa",
  "ar",
  "ur",
  "he",
  "ps",
  "sd",
]);

// ---------------------------------------------------------------------------
// Resources
// ---------------------------------------------------------------------------

const resources = {
  fa: { translation: fa },
  en: { translation: en },
  ar: { translation: ar },
  es: { translation: es },
  fr: { translation: fr },
  de: { translation: de },
  ru: { translation: ru },
  zh: { translation: zh },
  tr: { translation: tr },
  hi: { translation: hi },
} as const;

// ---------------------------------------------------------------------------
// Create the i18n instance
// ---------------------------------------------------------------------------

export const i18n: I18nInstance = createInstance();

export const i18nReady: Promise<I18nInstance> = i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: DEFAULT_LANGUAGE,
    supportedLngs: SUPPORTED_LANGUAGES,
    nonExplicitSupportedLngs: true,
    interpolation: { escapeValue: false },
    detection: {
      order: ["localStorage", "navigator", "htmlTag"],
      lookupLocalStorage: "econojin.lang",
      caches: ["localStorage"],
    },
    react: { useSuspense: false },
  })
  .then(() => i18n);

// ---------------------------------------------------------------------------
// Direction helpers
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
