/**
 * ============================================================================
 *  i18n — EcoNojin Web: 15 زبان زنده دنیا
 * ============================================================================
 *
 *  پشتیبانی از ۱۵ زبان پرطرفدار جهان (به جز عبری):
 *  ──────────────────────────────────────────────
 *  1. فارسی (fa)  — RTL  | 9.  چینی ساده‌شده (zh-CN) — LTR
 *  2. انگلیسی (en) — LTR  | 10. فرانسوی (fr)          — LTR
 *  3. عربی (ar)   — RTL  | 11. آلمانی (de)           — LTR
 *  4. اردو (ur)   — RTL  | 12. ترکی (tr)             — LTR
 *  5. روسی (ru)   — LTR  | 13. اسپانیایی (es)        — LTR
 *  6. هندی (hi)   — LTR  | 14. پرتغالی (pt)          — LTR
 *  7. بنگالی (bn) — LTR  | 15. ایتالیایی (it)        — LTR
 *  8. اندونزیایی (id) — LTR
 * ============================================================================
 */

import { createInstance, type i18n as I18nInstance } from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import { initReactI18next } from "react-i18next";

// ---------------------------------------------------------------------------
// Language constants
// ---------------------------------------------------------------------------

export interface LanguageInfo {
  code: string;
  name: string;
  nativeName: string;
  dir: "rtl" | "ltr";
  flag: string;
}

/** ۱۵ زبان پشتیبانی‌شده */
export const LANGUAGES: LanguageInfo[] = [
  { code: "fa",    name: "Persian",       nativeName: "فارسی",         dir: "rtl", flag: "🇮🇷" },
  { code: "en",    name: "English",       nativeName: "English",       dir: "ltr", flag: "🇬🇧" },
  { code: "ar",    name: "Arabic",        nativeName: "العربية",      dir: "rtl", flag: "🇸🇦" },
  { code: "ur",    name: "Urdu",          nativeName: "اردو",          dir: "rtl", flag: "🇵🇰" },
  { code: "ru",    name: "Russian",       nativeName: "Русский",      dir: "ltr", flag: "🇷🇺" },
  { code: "hi",    name: "Hindi",         nativeName: "हिन्दी",         dir: "ltr", flag: "🇮🇳" },
  { code: "bn",    name: "Bengali",       nativeName: "বাংলা",         dir: "ltr", flag: "🇧🇩" },
  { code: "id",    name: "Indonesian",    nativeName: "Bahasa Indonesia", dir: "ltr", flag: "🇮🇩" },
  { code: "zh-CN", name: "Chinese (Simplified)", nativeName: "简体中文", dir: "ltr", flag: "🇨🇳" },
  { code: "fr",    name: "French",        nativeName: "Français",     dir: "ltr", flag: "🇫🇷" },
  { code: "de",    name: "German",        nativeName: "Deutsch",      dir: "ltr", flag: "🇩🇪" },
  { code: "tr",    name: "Turkish",       nativeName: "Türkçe",       dir: "ltr", flag: "🇹🇷" },
  { code: "es",    name: "Spanish",       nativeName: "Español",      dir: "ltr", flag: "🇪🇸" },
  { code: "pt",    name: "Portuguese",    nativeName: "Português",    dir: "ltr", flag: "🇵🇹" },
  { code: "it",    name: "Italian",       nativeName: "Italiano",     dir: "ltr", flag: "🇮🇹" },
];

export const SUPPORTED_LANGUAGES = LANGUAGES.map(l => l.code);
export type SupportedLanguage = (typeof SUPPORTED_LANGUAGES)[number];
export const DEFAULT_LANGUAGE: SupportedLanguage = "fa";

export const RTL_LANGUAGES: ReadonlySet<string> = new Set(
  LANGUAGES.filter(l => l.dir === "rtl").map(l => l.code)
);

// ---------------------------------------------------------------------------
// Load translation JSON files dynamically
// ---------------------------------------------------------------------------

const localeModules = import.meta.glob<Record<string, string>>("./locales/*.json", {
  eager: true,
  import: "default",
});

function buildResources(): Record<string, { translation: Record<string, string> }> {
  const resources: Record<string, { translation: Record<string, string> }> = {};
  for (const [path, module] of Object.entries(localeModules)) {
    // path = ./locales/fa.json → lang = "fa"
    const lang = path.replace("./locales/", "").replace(".json", "");
    resources[lang] = { translation: module as unknown as Record<string, string> };
  }
  return resources;
}

const resources = buildResources();

// ---------------------------------------------------------------------------
// Create the i18n instance
// ---------------------------------------------------------------------------

const i18n: I18nInstance = createInstance();

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
  const base = (value as string).split("-")[0] ?? "";
  if (isSupportedLanguage(base)) return base;
  // Map zh → zh-CN
  if (base === "zh") return "zh-CN";
  return DEFAULT_LANGUAGE;
}

export function getLanguageInfo(code: string): LanguageInfo {
  return LANGUAGES.find(l => l.code === code) ?? LANGUAGES[0];
}

export default i18n;
