// apps/web/src/components/alerts/alertsI18n.ts
import type { AlertLevel } from "./alertsData";

export type AlertLang = "fa" | "en" | "ar";

const FA = {
  title: "هشدارها و اعلان‌ها",
  subtitle: "هشدارهای بلادرنگ و اخطارهای زودهنگام",
  markAllRead: "علامت‌گذاری همه به‌عنوان خوانده‌شده",
  empty: "هشداری برای این فیلتر وجود ندارد.",
  filterAll: "همه",
  filter_critical: "بحرانی",
  filter_warning: "هشدار",
  filter_info: "اطلاعیه",
  filter_success: "موفقیت",
  statCritical: "بحرانی",
  statWarning: "هشدارها",
  statInfo: "اطلاعیه‌ها",
  statUnread: "خوانده‌نشده",
  markRead: "خوانده‌شده",
  markUnread: "خوانده‌نشده",
  dismiss: "حذف",
  unreadBadge: "جدید",
  justNow: "همین حالا",
  minsAgo: "{n} دقیقه پیش",
  hoursAgo: "{n} ساعت پیش",
  daysAgo: "{n} روز پیش",
  al1_t: "خشکسالی شدید در دشت قزوین",
  al1_m: "شاخص SPI به زیر ۱٫۵− سقوط کرد؛ اقدام فوری لازم است.",
  al2_t: "افت ناگهانی پوشش گیاهی",
  al2_m: "کاهش ۳۰٪ شاخص NDVI در مزرعهٔ شمالی طی ۵ روز گذشته.",
  al3_t: "پیش‌بینی سرمازدگی",
  al3_m: "دمای زیر صفر در ۴۸ ساعت آینده پیش‌بینی می‌شود.",
  al4_t: "نگهداری سنسورهای IoT",
  al4_m: "کالیبراسیون دوره‌ای در ۳ روز آینده برنامه‌ریزی شده است.",
  al5_t: "تنش حرارتی رو به افزایش",
  al5_m: "بخش جنوبی مزرعه در محدودهٔ تنش حرارتی قرار گرفت.",
  al6_t: "ماژول جدید در دسترس است",
  al6_m: "دورهٔ «سازگاری اقلیمی» هم‌اکنون منتشر شد.",
  al7_t: "دادهٔ ماهواره‌ای جدید",
  al7_m: "تصویر امروز Sentinel-2 برای منطقهٔ شما در دسترس است.",
  al8_t: "پروژهٔ جنگل‌کاری به هدف رسید",
  al8_m: "طرح بتا به ۱۰۰۰ درخت کاشته‌شده رسید.",
  al9_t: "گزارش MRV تأیید شد",
  al9_m: "اعتبار کربن دورهٔ اخیر با موفقیت صادر شد.",
};

export type AlertStrings = typeof FA;

export const ALERT_STR: Record<AlertLang, AlertStrings> = {
  fa: FA,
  en: {
    title: "Alerts & Notifications",
    subtitle: "Real-time alerts and early warnings",
    markAllRead: "Mark all as read",
    empty: "No alerts match this filter.",
    filterAll: "All",
    filter_critical: "Critical",
    filter_warning: "Warning",
    filter_info: "Info",
    filter_success: "Success",
    statCritical: "Critical",
    statWarning: "Warnings",
    statInfo: "Info",
    statUnread: "Unread",
    markRead: "Mark read",
    markUnread: "Mark unread",
    dismiss: "Dismiss",
    unreadBadge: "New",
    justNow: "Just now",
    minsAgo: "{n} minutes ago",
    hoursAgo: "{n} hours ago",
    daysAgo: "{n} days ago",
    al1_t: "Severe drought in Qazvin plain",
    al1_m: "SPI index dropped below −1.5; urgent action required.",
    al2_t: "Sudden vegetation decline",
    al2_m: "NDVI dropped 30% in the northern farm over 5 days.",
    al3_t: "Frost forecast",
    al3_m: "Sub-zero temperatures predicted within 48 hours.",
    al4_t: "IoT sensor maintenance",
    al4_m: "Periodic calibration scheduled in 3 days.",
    al5_t: "Rising heat stress",
    al5_m: "Southern plot entered heat-stress range.",
    al6_t: "New module available",
    al6_m: "'Climate Adaptation' course is now live.",
    al7_t: "New satellite data",
    al7_m: "Today's Sentinel-2 imagery is available for your region.",
    al8_t: "Reforestation goal reached",
    al8_m: "Beta project reached 1,000 planted trees.",
    al9_t: "MRV report approved",
    al9_m: "Latest carbon credit successfully issued.",
  },
  ar: {
    title: "التنبيهات والإشعارات",
    subtitle: "تنبيهات فورية وتحذيرات مبكرة",
    markAllRead: "تحديد الكل كمقروء",
    empty: "لا توجد تنبيهات مطابقة لهذا المرشح.",
    filterAll: "الكل",
    filter_critical: "حرج",
    filter_warning: "تحذير",
    filter_info: "معلومة",
    filter_success: "نجاح",
    statCritical: "حرجة",
    statWarning: "تحذيرات",
    statInfo: "معلومات",
    statUnread: "غير مقروء",
    markRead: "تحديد كمقروء",
    markUnread: "تحديد كغير مقروء",
    dismiss: "إزالة",
    unreadBadge: "جديد",
    justNow: "الآن",
    minsAgo: "قبل {n} دقيقة",
    hoursAgo: "قبل {n} ساعة",
    daysAgo: "قبل {n} يوم",
    al1_t: "جفاف شديد في سهل قزوين",
    al1_m: "انخفض مؤشر SPI دون −١٫٥؛ إجراء عاجل مطلوب.",
    al2_t: "تراجع مفاجئ في الغطاء النباتي",
    al2_m: "انخفض NDVI بنسبة ٣٠٪ في المزرعة الشمالية خلال ٥ أيام.",
    al3_t: "توقعات بالصقيع",
    al3_m: "درجات حرارة دون الصفر متوقعة خلال ٤٨ ساعة.",
    al4_t: "صيانة حساسات IoT",
    al4_m: "معايرة دورية مجدولة خلال ٣ أيام.",
    al5_t: "إجهاد حراري متزايد",
    al5_m: "دخل الجزء الجنوبي نطاق الإجهاد الحراري.",
    al6_t: "وحدة جديدة متاحة",
    al6_m: "دورة «التكيف المناخي» متاحة الآن.",
    al7_t: "بيانات أقمار جديدة",
    al7_m: "صورة Sentinel-2 لليوم متاحة لمنطقتك.",
    al8_t: "تحقيق هدف التشجير",
    al8_m: "وصل المشروع التجريبي إلى ١٠٠٠ شجرة مزروعة.",
    al9_t: "اعتماد تقرير MRV",
    al9_m: "تم إصدار ائتمان الكربون الأخير بنجاح.",
  },
};

export function levelText(s: AlertStrings, l: AlertLevel): string {
  return s[`filter_${l}` as keyof AlertStrings] as string;
}
export function alertText(s: AlertStrings, key: string): string {
  return (s[key as keyof AlertStrings] as string) ?? key;
}
export function localeOf(lang: AlertLang): string {
  return lang === "fa" ? "fa-IR" : lang === "ar" ? "ar-EG" : "en-US";
}

// زمان نسبی بومی‌شده — جایگزین رشته‌های ثابت
export function timeAgo(iso: string, lang: AlertLang): string {
  const s = ALERT_STR[lang];
  const locale = localeOf(lang);
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60_000);
  const hours = Math.floor(mins / 60);
  const days = Math.floor(hours / 24);
  const fmt = (n: number) => n.toLocaleString(locale);
  if (mins < 1) return s.justNow;
  if (mins < 60) return s.minsAgo.replace("{n}", fmt(mins));
  if (hours < 24) return s.hoursAgo.replace("{n}", fmt(hours));
  return s.daysAgo.replace("{n}", fmt(days));
}