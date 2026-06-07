// i18n utilities stub
export type Locale = "fa" | "en" | "ar" | "tr" | "zh";

export const locales: Locale[] = ["fa", "en", "ar", "tr", "zh"];
export const defaultLocale: Locale = "fa";
export const rtlLocales: Locale[] = ["fa", "ar"];

export function getDirection(locale: Locale): "rtl" | "ltr" {
  return rtlLocales.includes(locale) ? "rtl" : "ltr";
}

export async function getDictionary(locale: Locale) {
  // Stub - در نسخه واقعی از فایل‌های JSON لود می‌شود
  return {
    common: {
      appName: "Econojin",
      home: locale === "fa" ? "خانه" : "Home",
      dashboard: locale === "fa" ? "داشبورد" : "Dashboard",
    }
  };
}
