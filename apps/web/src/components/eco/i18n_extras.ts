/**
 * i18n extras — CONTENT first, then extras (A+B+B2+B3).
 */
import type { Lang } from "./i18n";
import { PHASE_B_EXTRAS } from "./i18n_phase_b";
import { PHASE_B2_EXTRAS } from "./i18n_phase_b2";
import { PHASE_B3_EXTRAS } from "./i18n_phase_b3";

const BASE: Record<Lang, Record<string, string>> = {
  fa: {
    nav_farms: "مزارع",
    nav_group_monitoring: "پایش و تحلیل",
    nav_group_finance: "مالی و اکوکوین",
    nav_group_community: "آموزش و جامعه",
    nav_group_regional: "پروژه‌ها و منطقه",
    nav_group_system: "سیستم",
    auth_signin: "ورود",
    auth_register: "ثبت‌نام",
    auth_email: "ایمیل",
    auth_password: "رمز عبور",
    auth_full_name: "نام کامل",
    state_loading: "در حال بارگذاری…",
    state_empty: "موردی یافت نشد",
    state_error: "خطا در دریافت داده",
    state_retry: "تلاش مجدد",
    footer_rights: "تمامی حقوق محفوظ است.",
  },
  en: {
    nav_farms: "Farms",
    nav_group_monitoring: "Monitoring & analytics",
    nav_group_finance: "Finance & EcoCoin",
    nav_group_community: "Education & community",
    nav_group_regional: "Projects & regions",
    nav_group_system: "System",
    auth_signin: "Sign in",
    auth_register: "Register",
    auth_email: "Email",
    auth_password: "Password",
    auth_full_name: "Full name",
    state_loading: "Loading…",
    state_empty: "Nothing found",
    state_error: "Failed to load data",
    state_retry: "Retry",
    footer_rights: "All rights reserved.",
  },
  ar: {
    nav_farms: "المزارع",
    nav_group_monitoring: "المراقبة والتحليل",
    nav_group_finance: "المالية وإيكو كوين",
    nav_group_community: "التعليم والمجتمع",
    nav_group_regional: "المشاريع والمناطق",
    nav_group_system: "النظام",
    auth_signin: "تسجيل الدخول",
    auth_register: "إنشاء حساب",
    auth_email: "البريد الإلكتروني",
    auth_password: "كلمة المرور",
    auth_full_name: "الاسم الكامل",
    state_loading: "جارٍ التحميل…",
    state_empty: "لا توجد عناصر",
    state_error: "فشل تحميل البيانات",
    state_retry: "إعادة المحاولة",
    footer_rights: "جميع الحقوق محفوظة.",
  },
};

function mergeLang(lang: Lang): Record<string, string> {
  return {
    ...BASE[lang],
    ...PHASE_B_EXTRAS[lang],
    ...PHASE_B2_EXTRAS[lang],
    ...PHASE_B3_EXTRAS[lang],
  };
}

export const I18N_EXTRAS: Record<Lang, Record<string, string>> = {
  fa: mergeLang("fa"),
  en: mergeLang("en"),
  ar: mergeLang("ar"),
};

export function tr(
  content: Record<string, unknown>,
  lang: Lang,
  key: string,
): string {
  const fromContent = content[key];
  if (typeof fromContent === "string" && fromContent.length > 0) return fromContent;
  return I18N_EXTRAS[lang]?.[key] ?? I18N_EXTRAS.en[key] ?? key;
}

export function tExtra(lang: Lang, key: string): string {
  return I18N_EXTRAS[lang]?.[key] ?? I18N_EXTRAS.en[key] ?? key;
}

export function useTx(lang: Lang, content?: Record<string, unknown>) {
  return (key: string) => {
    if (content) {
      const a = tr(content, lang, key);
      if (a !== key) return a;
    }
    return tExtra(lang, key);
  };
}
