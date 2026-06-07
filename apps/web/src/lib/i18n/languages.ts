export const languages = {
  fa: { name: "فارسی", native: "فارسی", dir: "rtl", flag: "🇮🇷" },
  en: { name: "English", native: "English", dir: "ltr", flag: "🇬🇧" },
  ar: { name: "Arabic", native: "العربية", dir: "rtl", flag: "🇸🇦" },
  zh: { name: "Chinese", native: "中文", dir: "ltr", flag: "🇨🇳" },
  es: { name: "Spanish", native: "Español", dir: "ltr", flag: "🇪🇸" },
  fr: { name: "French", native: "Français", dir: "ltr", flag: "🇫🇷" },
  de: { name: "German", native: "Deutsch", dir: "ltr", flag: "🇩🇪" },
  ru: { name: "Russian", native: "Русский", dir: "ltr", flag: "🇷🇺" },
  pt: { name: "Portuguese", native: "Português", dir: "ltr", flag: "🇵🇹" },
  ja: { name: "Japanese", native: "日本語", dir: "ltr", flag: "🇯🇵" },
  tr: { name: "Turkish", native: "Türkçe", dir: "ltr", flag: "🇹🇷" },
  hi: { name: "Hindi", native: "हिन्दी", dir: "ltr", flag: "🇮🇳" },
  ur: { name: "Urdu", native: "اردو", dir: "rtl", flag: "🇵🇰" },
  id: { name: "Indonesian", native: "Bahasa Indonesia", dir: "ltr", flag: "🇮🇩" },
  ko: { name: "Korean", native: "한국어", dir: "ltr", flag: "🇰🇷" },
  it: { name: "Italian", native: "Italiano", dir: "ltr", flag: "🇮🇹" },
  nl: { name: "Dutch", native: "Nederlands", dir: "ltr", flag: "🇳🇱" },
  pl: { name: "Polish", native: "Polski", dir: "ltr", flag: "🇵🇱" },
  sv: { name: "Swedish", native: "Svenska", dir: "ltr", flag: "🇸🇪" },
  ms: { name: "Malay", native: "Bahasa Melayu", dir: "ltr", flag: "🇲🇾" },
};

export type Locale = keyof typeof languages;
export const locales = Object.keys(languages) as Locale[];
export const defaultLocale: Locale = "fa";

export function getDirection(locale: Locale): "rtl" | "ltr" {
  return languages[locale]?.dir || "ltr";
}

export function getNativeName(locale: Locale): string {
  return languages[locale]?.native || locale;
}
