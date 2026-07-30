/** Extra UI strings merged at runtime so Header/Footer never show raw keys. */
import type { Lang } from "./i18n";

export const I18N_EXTRAS: Record<
  Lang,
  Record<string, string>
> = {
  fa: {
    nav_farms: "مزارع",
    nav_group_monitoring: "پایش و تحلیل",
    nav_group_finance: "مالی و اکوکوین",
    nav_group_community: "آموزش و جامعه",
    nav_group_regional: "پروژه‌ها و منطقه",
    nav_group_system: "سیستم",
    footer_rights: "تمامی حقوق محفوظ است.",
    auth_signin: "ورود",
    auth_register: "ثبت‌نام",
    panel_ndvi_title: "شاخص NDVI",
    panel_ndvi_sub: "Sentinel-2 · تهران",
    panel_weather_title: "هواشناسی",
    panel_weather_sub: "نیمه‌ابری · تهران",
  },
  en: {
    nav_farms: "Farms",
    nav_group_monitoring: "Monitoring & analytics",
    nav_group_finance: "Finance & EcoCoin",
    nav_group_community: "Education & community",
    nav_group_regional: "Projects & regions",
    nav_group_system: "System",
    footer_rights: "All rights reserved.",
    auth_signin: "Sign in",
    auth_register: "Register",
    panel_ndvi_title: "NDVI",
    panel_ndvi_sub: "Sentinel-2 · Tehran",
    panel_weather_title: "Weather",
    panel_weather_sub: "Partly cloudy · Tehran",
  },
  ar: {
    nav_farms: "المزارع",
    nav_group_monitoring: "المراقبة والتحليل",
    nav_group_finance: "المالية وإيكو كوين",
    nav_group_community: "التعليم والمجتمع",
    nav_group_regional: "المشاريع والمناطق",
    nav_group_system: "النظام",
    footer_rights: "جميع الحقوق محفوظة.",
    auth_signin: "تسجيل الدخول",
    auth_register: "إنشاء حساب",
    panel_ndvi_title: "مؤشر NDVI",
    panel_ndvi_sub: "Sentinel-2 · طهران",
    panel_weather_title: "الطقس",
    panel_weather_sub: "غائم جزئياً · طهران",
  },
};

/** Resolve string: CONTENT first, then extras, then key. */
export function tr(
  content: Record<string, unknown>,
  lang: Lang,
  key: string,
): string {
  const fromContent = content[key];
  if (typeof fromContent === "string") return fromContent;
  const fromExtra = I18N_EXTRAS[lang]?.[key] ?? I18N_EXTRAS.en[key];
  return fromExtra ?? key;
}
