// apps/web/src/components/analytics/analyticsI18n.ts
import type { Period } from "./analyticsData";

export type AnLang = "fa" | "en" | "ar";

const FA = {
  title: "داشبورد تحلیلی",
  subtitle: "بینش‌ها و سنجه‌های جامع داده",
  export: "خروجی",
  percent: "٪",
  period_7d: "۷ روز",
  period_30d: "۳۰ روز",
  period_90d: "۹۰ روز",
  period_1y: "یک سال",
  kpi_revenue: "درآمد کل",
  kpi_carbon: "اعتبار کربن",
  kpi_users: "کاربران فعال",
  kpi_roi: "میانگین بازده",
  revenueTrends: "روند درآمد",
  projectDistribution: "توزیع پروژه‌ها",
  performanceMetrics: "سنجه‌های عملکرد",
  total: "مجموع",
  seg_reforestation: "جنگل‌کاری",
  seg_water: "مدیریت آب",
  seg_solar: "انرژی خورشیدی",
  seg_research: "پژوهش",
  seg_community: "جامعه",
  m_efficiency: "کارایی",
  m_quality: "کیفیت",
  m_speed: "سرعت",
  m_sustainability: "پایداری",
  m_innovation: "نوآوری",
  axis_7d: ["ش", "ی", "د", "س", "چ", "پ"],
  axis_30d: ["ه۱", "ه۲", "ه۳", "ه۴", "ه۵", "ه۶"],
  axis_90d: ["مهر", "آبا", "آذر", "دی", "بهم", "اسف"],
  axis_1y: ["فرو", "ارد", "خرد", "تیر", "مرد", "شهر"],
};

export type AnalyticsStrings = typeof FA;

export const ANALYTICS_STR: Record<AnLang, AnalyticsStrings> = {
  fa: FA,
  en: {
    title: "Analytics Dashboard",
    subtitle: "Comprehensive data insights and metrics",
    export: "Export",
    percent: "%",
    period_7d: "7 Days",
    period_30d: "30 Days",
    period_90d: "90 Days",
    period_1y: "1 Year",
    kpi_revenue: "Total Revenue",
    kpi_carbon: "Carbon Credits",
    kpi_users: "Active Users",
    kpi_roi: "Avg ROI",
    revenueTrends: "Revenue Trends",
    projectDistribution: "Project Distribution",
    performanceMetrics: "Performance Metrics",
    total: "Total",
    seg_reforestation: "Reforestation",
    seg_water: "Water Management",
    seg_solar: "Solar Energy",
    seg_research: "Research",
    seg_community: "Community",
    m_efficiency: "Efficiency",
    m_quality: "Quality",
    m_speed: "Speed",
    m_sustainability: "Sustainability",
    m_innovation: "Innovation",
    axis_7d: ["Sat", "Sun", "Mon", "Tue", "Wed", "Thu"],
    axis_30d: ["W1", "W2", "W3", "W4", "W5", "W6"],
    axis_90d: ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar"],
    axis_1y: ["Apr", "May", "Jun", "Jul", "Aug", "Sep"],
  },
  ar: {
    title: "لوحة التحليلات",
    subtitle: "رؤى وقياسات شاملة للبيانات",
    export: "تصدير",
    percent: "٪",
    period_7d: "٧ أيام",
    period_30d: "٣٠ يوماً",
    period_90d: "٩٠ يوماً",
    period_1y: "سنة",
    kpi_revenue: "إجمالي الإيرادات",
    kpi_carbon: "ائتمان الكربون",
    kpi_users: "المستخدمون النشطون",
    kpi_roi: "متوسط العائد",
    revenueTrends: "اتجاهات الإيرادات",
    projectDistribution: "توزيع المشاريع",
    performanceMetrics: "مقاييس الأداء",
    total: "المجموع",
    seg_reforestation: "التشجير",
    seg_water: "إدارة المياه",
    seg_solar: "الطاقة الشمسية",
    seg_research: "البحث",
    seg_community: "المجتمع",
    m_efficiency: "الكفاءة",
    m_quality: "الجودة",
    m_speed: "السرعة",
    m_sustainability: "الاستدامة",
    m_innovation: "الابتكار",
    axis_7d: ["ح", "ن", "ث", "ر", "خ", "ج"],
    axis_30d: ["أ١", "أ٢", "أ٣", "أ٤", "أ٥", "أ٦"],
    axis_90d: ["أكت", "نوف", "دسم", "ينا", "فبر", "مار"],
    axis_1y: ["أبر", "ماي", "يون", "يول", "أغس", "سبت"],
  },
};

export function kpiText(s: AnalyticsStrings, key: string): string {
  return (s[`kpi_${key}` as keyof AnalyticsStrings] as string) ?? key;
}
export function segText(s: AnalyticsStrings, key: string): string {
  return (s[`seg_${key}` as keyof AnalyticsStrings] as string) ?? key;
}
export function periodText(s: AnalyticsStrings, p: Period): string {
  return p === "7d" ? s.period_7d : p === "30d" ? s.period_30d : p === "90d" ? s.period_90d : s.period_1y;
}
export function axisLabels(s: AnalyticsStrings, p: Period): string[] {
  return p === "7d" ? s.axis_7d : p === "30d" ? s.axis_30d : p === "90d" ? s.axis_90d : s.axis_1y;
}
export function metricLabels(s: AnalyticsStrings): string[] {
  return [s.m_efficiency, s.m_quality, s.m_speed, s.m_sustainability, s.m_innovation];
}
export function localeOf(lang: AnLang): string {
  return lang === "fa" ? "fa-IR" : lang === "ar" ? "ar-EG" : "en-US";
}