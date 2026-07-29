// apps/web/src/components/simulators/paramI18n.ts
// Translation dictionary for simulator parameter labels (fa/en/ar).
// Falls back to the raw label if a key is not found.
import type { SimLang } from "./simulatorsI18n";

const PARAM_DICT: Record<string, Record<SimLang, string>> = {
  crop: { fa: "نوع محصول", en: "Crop Type", ar: "نوع المحصول" },
  planting_date: { fa: "تاریخ کاشت", en: "Planting Date", ar: "تاريخ الزراعة" },
  latitude: { fa: "عرض جغرافیایی", en: "Latitude", ar: "خط العرض" },
  longitude: { fa: "طول جغرافیایی", en: "Longitude", ar: "خط الطول" },
  use_real_climate: { fa: "استفاده از دادهٔ اقلیم واقعی", en: "Use Real Climate Data", ar: "استخدام بيانات المناخ الحقيقية" },
  field_capacity: { fa: "ظرفیت زراعی", en: "Field Capacity", ar: "السعة الحقلية" },
  wilting_point: { fa: "نقطهٔ پژمردگی", en: "Wilting Point", ar: "نقطة الذبول" },
  soil_depth: { fa: "عمق خاک", en: "Soil Depth", ar: "عمق التربة" },
  total_irrigation: { fa: "کل آبیاری", en: "Total Irrigation", ar: "إجمالي الري" },
  co2_ppm: { fa: "غلظت CO₂", en: "Atmospheric CO2", ar: "تركيز CO₂" },
  fallback_precip: { fa: "بارش (حالت جایگزین)", en: "Fallback Rainfall", ar: "الهطول (بديل)" },
  fallback_et0: { fa: "ET₀ (حالت جایگزین)", en: "Fallback ET0", ar: "ET₀ (بديل)" },
  initial_population: { fa: "جمعیت اولیه", en: "Initial Population", ar: "عدد السكان الأولي" },
  growth_rate: { fa: "نرخ رشد سالانه", en: "Annual Growth Rate", ar: "معدل النمو السنوي" },
  urban_area_km2: { fa: "مساحت شهری اولیه", en: "Initial Urban Area", ar: "المساحة الحضرية الأولية" },
  years: { fa: "سال‌های شبیه‌سازی", en: "Simulation Years", ar: "سنوات المحاكاة" },
  precipitation: { fa: "بارش سالانه", en: "Annual Precipitation", ar: "الهطول السنوي" },
  runoff_coef: { fa: "ضریب رواناب", en: "Runoff Coefficient", ar: "معامل الجريان" },
  baseflow: { fa: "جریان پایه", en: "Baseflow", ar: "التدفق الأساسي" },
  potential_yield: { fa: "عملکرد پتانسیل", en: "Potential Yield", ar: "الإنتاج المحتمل" },
  water_factor: { fa: "ضریب آب", en: "Water Factor", ar: "عامل الماء" },
  nutrient_factor: { fa: "ضریب مواد مغذی", en: "Nutrient Factor", ar: "عامل المغذيات" },
  initial_soc: { fa: "کربن آلی اولیهٔ خاک", en: "Initial SOC", ar: "الكربون العضوي الأولي" },
  carbon_input: { fa: "ورودی سالانهٔ کربن", en: "Annual C Input", ar: "المدخلات السنوية للكربون" },
  temperature: { fa: "میانگین دمای سالانه", en: "Mean Annual Temp", ar: "متوسط درجة الحرارة" },
  initial_investment: { fa: "سرمایه‌گذاری اولیه", en: "Initial Investment", ar: "الاستثمار الأولي" },
  annual_benefit: { fa: "منافع سالانه", en: "Annual Benefit", ar: "الفائدة السنوية" },
  annual_cost: { fa: "هزینهٔ سالانه", en: "Annual O&M Cost", ar: "التكلفة السنوية" },
  discount_rate: { fa: "نرخ تنزیل", en: "Discount Rate", ar: "معدل الخصم" },
  solar_kw: { fa: "ظرفیت خورشیدی", en: "Solar Capacity", ar: "سعة الطاقة الشمسية" },
  wind_kw: { fa: "ظرفیت بادی", en: "Wind Capacity", ar: "سعة طاقة الرياح" },
  demand_kw: { fa: "تقاضای برق", en: "Electricity Demand", ar: "الطلب على الكهرباء" },
  R: { fa: "عامل بارندگی (R)", en: "Rainfall Factor (R)", ar: "عامل الأمطار (R)" },
  K: { fa: "فرسایش‌پذیری خاک (K)", en: "Soil Erodibility (K)", ar: "قابلية التربة للتآكل (K)" },
  LS: { fa: "عامل طول/شیب (LS)", en: "Slope Length (LS)", ar: "عامل المنحدر (LS)" },
  C: { fa: "عامل پوشش (C)", en: "Cover Factor (C)", ar: "عامل الغطاء (C)" },
  P: { fa: "عامل حفاظتی (P)", en: "Practice Factor (P)", ar: "عامل الممارسات (P)" },
  sensitivity: { fa: "حساسیت اقلیمی", en: "Climate Sensitivity", ar: "حساسية المناخ" },
  co2: { fa: "غلظت CO₂", en: "CO2 Concentration", ar: "تركيز CO₂" },
  cycle_days: { fa: "طول دورهٔ رشد", en: "Crop Cycle", ar: "دورة المحصول" },
  radiation: { fa: "تابش فصلی", en: "Season Radiation", ar: "الإشعاع الموسمي" },
  water_availability: { fa: "دسترسی به آب", en: "Water Availability", ar: "توفر المياه" },
  annual_input: { fa: "ورودی سالانهٔ کربن", en: "Annual C Input", ar: "المدخلات السنوية" },
  supply: { fa: "عرضهٔ آب", en: "Water Supply", ar: "إمدادات المياه" },
  demand_agri: { fa: "تقاضای کشاورزی", en: "Agricultural Demand", ar: "الطلب الزراعي" },
  demand_domestic: { fa: "تقاضای شرب", en: "Domestic Demand", ar: "الطلب المنزلي" },
  demand_industrial: { fa: "تقاضای صنعت", en: "Industrial Demand", ar: "الطلب الصناعي" },
  forest_area: { fa: "مساحت جنگل", en: "Forest Area", ar: "مساحة الغابات" },
  agri_area: { fa: "مساحت کشاورزی", en: "Agricultural Area", ar: "المساحة الزراعية" },
  carbon_density_forest: { fa: "چگالی کربن جنگل", en: "Forest Carbon Density", ar: "كثافة كربون الغابات" },
  irradiance: { fa: "تابش خورشیدی", en: "Solar Irradiance", ar: "الإشعاع الشمسي" },
  wind_speed: { fa: "سرعت باد", en: "Wind Speed", ar: "سرعة الرياح" },
};

export function paramLabel(key: string, raw: string, lang: SimLang): string {
  const hit = PARAM_DICT[key];
  if (hit && hit[lang]) return hit[lang];
  // حذف بخش فنی مثل "(required=False)" از برچسب خام
  return raw.replace(/\s*\(required=.*?\)/i, "").trim() || key;
}

export function paramUnit(raw: string): string {
  // استخراج واحد از پرانتز: "Field Capacity (vol %)" → "vol %"
  const m = raw.match(/\(([^)]*)\)\s*$/);
  return m ? m[1] : "";
}
