// apps/web/src/components/notfound/notFoundI18n.ts
export type NfLang = "fa" | "en" | "ar";

const FA = {
  code: "۴۰۴",
  title: "این مسیر به جایی نمی‌رسد",
  description:
    "صفحه‌ای که دنبالش بودید پیدا نشد — شاید جابه‌جا شده یا هرگز وجود نداشته. نگران نباشید، زمین اینجاست و راه بازگشت هم هست.",
  goHome: "بازگشت به خانه",
  goBack: "صفحهٔ قبل",
  explore: "یا این مسیرها را امتحان کنید",
  linkDashboard: "داشبورد",
  linkLibrary: "مرکز دانش",
  linkNews: "اخبار",
  orbitHint: "در حال چرخش به دور زمین…",
};

export type NotFoundStrings = typeof FA;

export const NF_STR: Record<NfLang, NotFoundStrings> = {
  fa: FA,
  en: {
    code: "404",
    title: "This path leads nowhere",
    description:
      "The page you were looking for could not be found — it may have moved or never existed. Don't worry, the Earth is still here, and so is the way back.",
    goHome: "Back to home",
    goBack: "Previous page",
    explore: "Or try one of these paths",
    linkDashboard: "Dashboard",
    linkLibrary: "Knowledge Hub",
    linkNews: "News",
    orbitHint: "Orbiting the Earth…",
  },
  ar: {
    code: "٤٠٤",
    title: "هذا المسار لا يؤدي إلى مكان",
    description:
      "تعذّر العثور على الصفحة التي تبحث عنها — ربما نُقلت أو لم تكن موجودة أصلاً. لا تقلق، الأرض ما زالت هنا، وطريق العودة أيضاً.",
    goHome: "العودة إلى الرئيسية",
    goBack: "الصفحة السابقة",
    explore: "أو جرّب أحد هذه المسارات",
    linkDashboard: "لوحة التحكم",
    linkLibrary: "مركز المعرفة",
    linkNews: "الأخبار",
    orbitHint: "يدور حول الأرض…",
  },
};

export function nfText(s: NotFoundStrings, key: keyof NotFoundStrings): string {
  return s[key];
}