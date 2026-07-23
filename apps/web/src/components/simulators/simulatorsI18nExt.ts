// apps/web/src/components/simulators/simulatorsI18nExt.ts
// Translations for the 14 backend simulators (name + description).
// Used when the API returns English metadata; falls back to the API value.
import type { SimLang } from "./simulatorsI18n";

interface SimTrans { name: string; desc: string; }

export const SIM_TRANSLATIONS: Record<string, Partial<Record<SimLang, SimTrans>>> = {
  climate: {
    fa: { name: "مدل سناریوی اقلیمی", desc: "دما، بارش، رویدادهای شدید و NDVI را بر اساس CO₂، حساسیت اقلیمی و مسیر IPCC شبیه‌سازی می‌کند." },
    en: { name: "Climate Scenario Simulator", desc: "Simulates temperature, precipitation, extreme events and NDVI from CO2, sensitivity and an IPCC pathway." },
    ar: { name: "محاكي السيناريو المناخي", desc: "يحاكي الحرارة والهطول والأحداث المتطرفة وNDVI من CO2 والحساسية ومسار IPCC." },
  },
  urban: {
    fa: { name: "شبیه‌ساز رشد شهری و کاربری اراضی", desc: "گسترش شهری، تغییر کاربری اراضی و پویایی جمعیت را با اتوماتای سلولی شبیه‌سازی می‌کند." },
    en: { name: "Urban Growth & Land Use Simulator", desc: "Simulates urban expansion, land use change, and population dynamics using cellular automata." },
    ar: { name: "محاكي النمو الحضري واستخدام الأراضي", desc: "يحاكي التوسع الحضري وتغير استخدام الأراضي وديناميكيات السكان." },
  },
  dssat: {
    fa: { name: "DSSAT (رشد و عملکرد محصول)", desc: "رشد محصول بر اساس زمان حرارتی (GDD) با محدودیت آب و نیتروژن؛ تودهٔ زیستی لجستیک." },
    en: { name: "DSSAT (Crop Growth & Yield)", desc: "Thermal-time (GDD) crop growth with water and nitrogen limitation; logistic biomass." },
    ar: { name: "DSSAT (نمو المحصول والإنتاج)", desc: "نمو المحصول بالوقت الحراري (GDD) مع محدودية الماء والنيتروجين." },
  },
  aquacrop: {
    fa: { name: "AquaCrop (بهره‌وری آب محصول فائو)", desc: "پاسخ عملکرد به آب را برای محصولات علفی شبیه‌سازی می‌کند؛ تعادل دقت، سادگی و پایداری." },
    en: { name: "AquaCrop (FAO Crop Water Productivity)", desc: "FAO AquaCrop simulates yield response to water for herbaceous crops." },
    ar: { name: "AquaCrop (إنتاجية مياه المحصول للفاو)", desc: "يحاكي استجابة المحصول للماء للمحاصيل العشبية." },
  },
  wofost: {
    fa: { name: "WOFOST (مطالعات غذای جهانی)", desc: "رشد و تولید محصول را برای تحلیل امنیت غذایی شبیه‌سازی می‌کند؛ بخشی از سیستم پایش رشد محصول." },
    en: { name: "WOFOST (World Food Studies)", desc: "Simulates crop growth and production for food security analysis." },
    ar: { name: "WOFOST (دراسات الغذاء العالمية)", desc: "يحاكي نمو المحصول والإنتاج لتحليل الأمن الغذائي." },
  },
  "crop-model": {
    fa: { name: "مدل عمومی رشد محصول", desc: "یک مدل سادهٔ رشد محصول بر اساس جذب نور، بهره‌وری تابش و شاخص برداشت." },
    en: { name: "Generic Crop Growth Model", desc: "A simplified crop growth model based on light interception, radiation use efficiency, and harvest index." },
    ar: { name: "نموذج عام لنمو المحصول", desc: "نموذج مبسط لنمو المحصول بناءً على اعتراض الضوء وكفاءة الإشعاع." },
  },
  swat: {
    fa: { name: "SWAT (ابزار ارزیابی خاک و آب)", desc: "تراز آب آبخیز: رواناب سطحی، جریان پایه و تبخیر و تعرق (ماهانه)." },
    en: { name: "SWAT (Soil & Water Assessment Tool)", desc: "Watershed water balance: surface runoff, baseflow and evapotranspiration (monthly)." },
    ar: { name: "SWAT (أداة تقييم التربة والمياه)", desc: "ميزان مياه الحوض: الجريان السطحي والتدفق الأساسي والنتح." },
  },
  weap: {
    fa: { name: "WEAP (ارزیابی و برنامه‌ریزی آب)", desc: "تراز عرضه-تقاضای آب ماهانه با تخصیص اولویت‌دار (شرب > صنعت > کشاورزی)." },
    en: { name: "WEAP (Water Evaluation And Planning)", desc: "Monthly water supply-demand balance with priority allocation." },
    ar: { name: "WEAP (تقييم المياه والتخطيط)", desc: "ميزان عرض وطلب المياه الشهري مع التخصيص حسب الأولوية." },
  },
  rothc: {
    fa: { name: "RothC (گردش کربن آلی خاک)", desc: "پویایی کربن آلی خاک با تجزیهٔ وابسته به دما/رطوبت/رس." },
    en: { name: "RothC (Soil Organic Carbon Turnover)", desc: "Soil organic carbon dynamics with temperature/moisture/clay-dependent decomposition." },
    ar: { name: "RothC (دوران الكربون العضوي في التربة)", desc: "ديناميكيات الكربون العضوي مع التحلل المعتمد على الحرارة والرطوبة والطين." },
  },
  century: {
    fa: { name: "CENTURY (مادهٔ آلی خاک)", desc: "پویایی کربن و مواد مغذی برای مراتع، جنگل و زراعت در مقیاس‌های زمانی بلند." },
    en: { name: "CENTURY Soil Organic Matter Model", desc: "Simulates carbon and nutrient dynamics for grassland, forest, and crop systems." },
    ar: { name: "CENTURY (نموذج المادة العضوية)", desc: "يحاكي ديناميكيات الكربون والمغذيات للمراعي والغابات والمحاصيل." },
  },
  cba: {
    fa: { name: "مدل تحلیل هزینه-فایده", desc: "امکان‌سنجی اقتصادی پروژه‌ها را با مقایسهٔ هزینه‌ها و فواید در زمان (NPV و IRR) ارزیابی می‌کند." },
    en: { name: "Cost-Benefit Analysis Model", desc: "Evaluates economic feasibility by comparing costs and benefits over time with NPV and IRR." },
    ar: { name: "نموذج تحليل التكلفة والعائد", desc: "يقيم الجدوى الاقتصادية بمقارنة التكاليف والعوائد مع NPV وIRR." },
  },
  invest: {
    fa: { name: "InVEST (خدمات اکوسیستم)", desc: "سه خدمت اکوسیستم (ذخیرهٔ کربن، عملکرد آب، کیفیت زیستگاه) در یک گرادیان تبدیل اراضی." },
    en: { name: "InVEST (Ecosystem Services)", desc: "Three ecosystem services (carbon storage, water yield, habitat quality) across a land-conversion gradient." },
    ar: { name: "InVEST (خدمات النظم البيئية)", desc: "ثلاث خدمات بيئية (الكربون والمياه وجودة الموائل) عبر تدرج تحويل الأراضي." },
  },
  homer: {
    fa: { name: "HOMER (انرژی تجدیدپذیر ترکیبی)", desc: "تولید خورشیدی + بادی در برابر تقاضا؛ سهم تجدیدپذیر و بار بی‌پاسخ." },
    en: { name: "HOMER (Hybrid Renewable Energy)", desc: "Solar PV + wind generation against demand; renewable fraction and unmet load." },
    ar: { name: "HOMER (الطاقة المتجددة الهجينة)", desc: "توليد شمسي ورياح مقابل الطلب؛ حصة المتجددة والحمل غير الملبى." },
  },
  rusle2: {
    fa: { name: "RUSLE2 (معادلهٔ جهانی فرسایش خاک)", desc: "فرسایش سالانهٔ خاک A = R·K·LS·C·P با توزیع ماهانه و بررسی حد مجاز." },
    en: { name: "RUSLE2 (Revised Universal Soil Loss Equation)", desc: "Annual soil erosion A = R*K*LS*C*P with monthly distribution and tolerance check." },
    ar: { name: "RUSLE2 (معادلة فقدان التربة)", desc: "تآكل التربة السنوي A = R*K*LS*C*P مع التوزيع الشهري." },
  },
};

/** Resolve a translated name/description for a simulator id, falling back to the API value. */
export function simName(id: string, lang: SimLang, fallback: string): string {
  return SIM_TRANSLATIONS[id]?.[lang]?.name ?? fallback;
}
export function simDesc(id: string, lang: SimLang, fallback: string): string {
  return SIM_TRANSLATIONS[id]?.[lang]?.desc ?? fallback;
}
