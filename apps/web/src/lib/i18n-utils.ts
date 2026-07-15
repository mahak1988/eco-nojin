/**
 * ============================================================================
 *  i18n utilities — direction-aware helpers for 10 languages
 * ============================================================================
 */

import type { SupportedLanguage } from "@/i18n";

// ---------------------------------------------------------------------------
// Language → direction mapping
// ---------------------------------------------------------------------------

const RTL_LANGUAGES: ReadonlySet<string> = new Set(["fa", "ar", "ur", "he", "ps", "sd"]);

export function isRTL(language: string): boolean {
  return RTL_LANGUAGES.has(language);
}

export function getDir(language: string): "rtl" | "ltr" {
  return isRTL(language) ? "rtl" : "ltr";
}

// ---------------------------------------------------------------------------
// Locale-aware number/date formatting (cached)
// ---------------------------------------------------------------------------

const LOCALE_MAP: Record<string, string> = {
  fa: "fa-IR",
  en: "en-US",
  ar: "ar-SA",
  es: "es-ES",
  fr: "fr-FR",
  de: "de-DE",
  ru: "ru-RU",
  zh: "zh-CN",
  tr: "tr-TR",
  hi: "hi-IN",
};

const numberFormatters: Record<string, Intl.NumberFormat> = {};
const decimalFormatters: Record<string, Intl.NumberFormat> = {};
const dateFormatters: Record<string, Intl.DateTimeFormat> = {};
const dateTimeFormatters: Record<string, Intl.DateTimeFormat> = {};
const longDateFormatters: Record<string, Intl.DateTimeFormat> = {};

function getLocale(language: string): string {
  return LOCALE_MAP[language] ?? "en-US";
}

export function formatNumber(value: number, language: string = "fa"): string {
  const locale = getLocale(language);
  if (!numberFormatters[locale]) {
    numberFormatters[locale] = new Intl.NumberFormat(locale);
  }
  return numberFormatters[locale].format(value);
}

export function formatDecimal(value: number, language: string = "fa"): string {
  const locale = getLocale(language);
  if (!decimalFormatters[locale]) {
    decimalFormatters[locale] = new Intl.NumberFormat(locale, { maximumFractionDigits: 1 });
  }
  return decimalFormatters[locale].format(value);
}

export function formatDate(iso: string, language: string = "fa"): string {
  const locale = getLocale(language);
  if (!dateFormatters[locale]) {
    dateFormatters[locale] = new Intl.DateTimeFormat(locale, {
      year: "numeric",
      month: "numeric",
      day: "numeric",
    });
  }
  return dateFormatters[locale].format(new Date(iso));
}

export function formatDateTime(iso: string, language: string = "fa"): string {
  const locale = getLocale(language);
  if (!dateTimeFormatters[locale]) {
    dateTimeFormatters[locale] = new Intl.DateTimeFormat(locale, {
      year: "numeric",
      month: "numeric",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }
  return dateTimeFormatters[locale].format(new Date(iso));
}

export function formatLongDate(iso: string, language: string = "fa"): string {
  const locale = getLocale(language);
  if (!longDateFormatters[locale]) {
    longDateFormatters[locale] = new Intl.DateTimeFormat(locale, {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  }
  return longDateFormatters[locale].format(new Date(iso));
}

// ---------------------------------------------------------------------------
// Language metadata (10 languages)
// ---------------------------------------------------------------------------

export interface LanguageMeta {
  code: SupportedLanguage;
  nativeName: string;
  englishName: string;
  flag: string;
  dir: "rtl" | "ltr";
}

export const LANGUAGE_META: Readonly<Record<SupportedLanguage, LanguageMeta>> = {
  fa: { code: "fa", nativeName: "فارسی", englishName: "Persian", flag: "🇮🇷", dir: "rtl" },
  en: { code: "en", nativeName: "English", englishName: "English", flag: "🇬🇧", dir: "ltr" },
  ar: { code: "ar", nativeName: "العربية", englishName: "Arabic", flag: "🇸🇦", dir: "rtl" },
  es: { code: "es", nativeName: "Español", englishName: "Spanish", flag: "🇪🇸", dir: "ltr" },
  fr: { code: "fr", nativeName: "Français", englishName: "French", flag: "🇫🇷", dir: "ltr" },
  de: { code: "de", nativeName: "Deutsch", englishName: "German", flag: "🇩🇪", dir: "ltr" },
  ru: { code: "ru", nativeName: "Русский", englishName: "Russian", flag: "🇷🇺", dir: "ltr" },
  zh: { code: "zh", nativeName: "中文", englishName: "Chinese", flag: "🇨🇳", dir: "ltr" },
  tr: { code: "tr", nativeName: "Türkçe", englishName: "Turkish", flag: "🇹🇷", dir: "ltr" },
  hi: { code: "hi", nativeName: "हिन्दी", englishName: "Hindi", flag: "🇮🇳", dir: "ltr" },
};

export const AVAILABLE_LANGUAGES: readonly LanguageMeta[] = Object.values(LANGUAGE_META);
