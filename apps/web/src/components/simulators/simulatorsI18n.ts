// apps/web/src/components/simulators/simulatorsI18n.ts
import type { SimStatus } from "./simulatorsData";

export type SimLang = "fa" | "en" | "ar";

const FA = {
  title: "شبیه‌سازها", subtitle: "مدل‌های شبیه‌سازی اقلیم، آب، کشاورزی و انرژی",
  searchPlaceholder: "جست‌وجوی شبیه‌ساز…", filterAll: "همه", filter_idle: "آماده",
  filter_running: "در حال اجرا", filter_done: "تکمیل‌شده", run: "اجرا", stop: "توقف",
  reset: "بازنشانی", params: "پارامترها", output: "خروجی شبیه‌سازی", progress: "پیشرفت",
  runsLabel: "اجرا", exportAll: "خروجی CSV", kpi_runs: "کل اجراها", kpi_running: "در حال اجرا",
  kpi_done: "تکمیل‌شده", kpi_models: "مدل‌ها", st_idle: "آماده", st_running: "در حال اجرا",
  st_done: "تکمیل‌شده", n_climate: "مدل اقلیمی", n_water: "منابع آب", n_agriculture: "عملکرد کشاورزی",
  n_energy: "شبکهٔ انرژی", d_climate: "دما، بارش، رویدادهای شدید و NDVI را از CO₂ و حساسیت اقلیمی شبیه‌سازی می‌کند.",
  d_water: "موجودی مخزن را از بارش و تقاضا مدل می‌کند.",
  d_agriculture: "عملکرد فصلی محصول را از آب، دما و کیفیت خاک پیش‌بینی می‌کند.",
  d_energy: "تولید تجدیدپذیر را در برابر تقاضا در طول روز شبیه‌سازی می‌کند.",
  p_co2: "غلظت CO₂", p_sens: "حساسیت اقلیمی", p_rain: "بارش", p_wdemand: "تقاضای آب",
  p_awater: "آبیاری", p_atemp: "دما", p_soil: "کیفیت خاک", p_solar: "ظرفیت خورشیدی",
  p_wind: "ظرفیت بادی", p_edemand: "تقاضای برق", u_ppm: "ppm", u_c: "°C", u_mm: "mm",
  u_pct: "٪", u_mw: "MW", l_temp: "دما (°C)", l_reservoir: "موجودی مخزن (٪)", l_yield: "شاخص عملکرد",
  l_generation: "تولید (MW)", l_demand: "تقاضا (MW)", l_precip: "بارش (mm)",
  l_extreme: "رویدادهای شدید / سال", l_ndvi: "NDVI",
  csvHeaders: "شبیه‌ساز,وضعیت,اجراها,پیشرفت٪,پارامترها",
};

export type SimStrings = typeof FA;

export const SIM_STR: Record<SimLang, SimStrings> = {
  fa: FA,
  en: {
    title: "Simulators", subtitle: "Climate, water, agriculture and energy models",
    searchPlaceholder: "Search simulators…", filterAll: "All", filter_idle: "Ready",
    filter_running: "Running", filter_done: "Completed", run: "Run", stop: "Stop",
    reset: "Reset", params: "Parameters", output: "Simulation output", progress: "Progress",
    runsLabel: "runs", exportAll: "Export CSV", kpi_runs: "Total runs", kpi_running: "Running",
    kpi_done: "Completed", kpi_models: "Models", st_idle: "Ready", st_running: "Running",
    st_done: "Completed", n_climate: "Climate Model", n_water: "Water Resources",
    n_agriculture: "Agriculture Yield", n_energy: "Energy Grid",
    d_climate: "Simulates temperature, precipitation, extreme events and NDVI from CO2 and sensitivity.",
    d_water: "Models reservoir level from rainfall and demand.",
    d_agriculture: "Predicts seasonal crop yield from water, temperature and soil quality.",
    d_energy: "Simulates renewable generation against demand across the day.",
    p_co2: "CO2 concentration", p_sens: "Climate sensitivity", p_rain: "Rainfall",
    p_wdemand: "Water demand", p_awater: "Irrigation", p_atemp: "Temperature",
    p_soil: "Soil quality", p_solar: "Solar capacity", p_wind: "Wind capacity",
    p_edemand: "Power demand", u_ppm: "ppm", u_c: "°C", u_mm: "mm", u_pct: "%", u_mw: "MW",
    l_temp: "Temperature (°C)", l_reservoir: "Reservoir level (%)", l_yield: "Yield index",
    l_generation: "Generation (MW)", l_demand: "Demand (MW)", l_precip: "Precipitation (mm)",
    l_extreme: "Extreme events / yr", l_ndvi: "NDVI",
    csvHeaders: "Simulator,Status,Runs,Progress%,Parameters",
  },
  ar: {
    title: "المحاكيات", subtitle: "نماذج المناخ والمياه والزراعة والطاقة",
    searchPlaceholder: "ابحث في المحاكيات…", filterAll: "الكل", filter_idle: "جاهز",
    filter_running: "قيد التشغيل", filter_done: "مكتمل", run: "تشغيل", stop: "إيقاف",
    reset: "إعادة تعيين", params: "المعاملات", output: "ناتج المحاكاة", progress: "التقدم",
    runsLabel: "تشغيل", exportAll: "تصدير CSV", kpi_runs: "إجمالي التشغيلات", kpi_running: "قيد التشغيل",
    kpi_done: "مكتملة", kpi_models: "النماذج", st_idle: "جاهز", st_running: "قيد التشغيل",
    st_done: "مكتمل", n_climate: "نموذج المناخ", n_water: "موارد المياه",
    n_agriculture: "إنتاجية الزراعة", n_energy: "شبكة الطاقة",
    d_climate: "يحاكي الحرارة والهطول والأحداث المتطرفة وNDVI من CO2 والحساسية.",
    d_water: "ينمذج مستوى الخزان من الهطول والطلب.",
    d_agriculture: "يتنبأ بالإنتاج الموسمي من المياه والحرارة وجودة التربة.",
    d_energy: "يحاكي الإنتاج المتجدد مقابل الطلب خلال اليوم.",
    p_co2: "تركيز CO2", p_sens: "الحساسية المناخية", p_rain: "الهطول", p_wdemand: "طلب المياه",
    p_awater: "الري", p_atemp: "الحرارة", p_soil: "جودة التربة", p_solar: "السعة الشمسية",
    p_wind: "سعة الرياح", p_edemand: "طلب الكهرباء", u_ppm: "ppm", u_c: "°C", u_mm: "mm",
    u_pct: "٪", u_mw: "MW", l_temp: "الحرارة (°C)", l_reservoir: "مستوى الخزان (٪)",
    l_yield: "مؤشر الإنتاج", l_generation: "الإنتاج (MW)", l_demand: "الطلب (MW)",
    l_precip: "الهطول (mm)", l_extreme: "الأحداث المتطرفة / سنة", l_ndvi: "NDVI",
    csvHeaders: "المحاكي,الحالة,التشغيلات,التقدم٪,المعاملات",
  },
};

export function simText(s: SimStrings, key: string): string {
  return (s[key as keyof SimStrings] as string) ?? key;
}
export function statusText(s: SimStrings, st: SimStatus): string {
  return s[`st_${st}` as keyof SimStrings] as string;
}
export function filterText(s: SimStrings, f: string): string {
  return f === "all" ? s.filterAll : (s[`filter_${f}` as keyof SimStrings] as string);
}
export function localeOf(lang: SimLang): string {
  return lang === "fa" ? "fa-IR" : lang === "ar" ? "ar-EG" : "en-US";
}
